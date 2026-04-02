from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.memory import MemorySaver
from redis import Redis
from src.state import AgentState
from src.agents.nodes import classify_input, fetch_market_data, analyze_and_predict, general_chat
from src.config import Config

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("classifier", classify_input)
workflow.add_node("market_data", fetch_market_data)
workflow.add_node("analyst", analyze_and_predict)
workflow.add_node("chatbot", general_chat)

# Define edges
def route_request(state: AgentState):
    """
    Routes the request based on intent.
    - Market intents (price, analysis, prediction, top_coins, list_all_coins, search_coins, market_overview, learn) -> fetch market data -> analyze
    - Chat -> general_chat directly
    """
    intent = state.get("intent")
    
    # Market data needs to be fetched for these intents (including learn)
    if intent in ["price", "analysis", "prediction", "top_coins", "list_all_coins", "search_coins", "market_overview", "learn", "compare"]:
        return "market_data"
    
    # General conversation
    return "chatbot"

workflow.set_entry_point("classifier")

workflow.add_conditional_edges(
    "classifier",
    route_request,
    {
        "market_data": "market_data",
        "chatbot": "chatbot"
    }
)

workflow.add_edge("market_data", "analyst")
workflow.add_edge("analyst", END)
workflow.add_edge("chatbot", END)

# Initialize Checkpointer - Try Redis first (Option 1), then MemorySaver fallback
try:
    redis_client = Redis.from_url(Config.REDIS_URL, socket_timeout=2)
    redis_client.ping()
    print("[OK] Connected to Redis successfully. Using RedisSaver.")
    checkpointer = RedisSaver(redis_client)
except Exception as e:
    print(f"[WARNING] Redis connection failed ({e}). Using MemorySaver (RAM) instead.")
    checkpointer = MemorySaver()

# NOTE: PostgreSQL conversation storage is handled separately in main.py
# - Uses Database.log_message() to save all conversations
# - Uses Database.save_analysis() for predictions
# - Checkpointer (Redis/MemorySaver) only handles LangGraph conversation state

# Compile the graph
app = workflow.compile(checkpointer=checkpointer)
