from typing import TypedDict, Annotated, List, Dict, Any, Optional

class AgentState(TypedDict, total=False):
    messages: List[Dict[str, str]]  # Conversation window managed externally (main.py)
    user_id: str
    intent: Optional[str]
    symbol: Optional[str]
    keyword: Optional[str]
    language: str
    market_data: Dict[str, Any]
    analysis: str
    final_response: str
    chart_image: Optional[str]  # Base64 encoded chart image
