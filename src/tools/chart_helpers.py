"""
Enhanced Market Data Fetching with Chart Support
"""

def fetch_market_data_with_charts(coin_symbol: str, market_data: dict, language: str = 'en'):
    """
    Prepare market data with chart information
    
    Args:
        coin_symbol: e.g., 'BTC', 'ETH'
        market_data: Dict with price, volume, change_24h, etc.
        language: 'en' or 'vi'
    
    Returns:
        Dict with formatted response and chart data
    """
    from src.tools.visualization import ResponseFormatter
    
    formatted_response = ResponseFormatter.format_price_info(coin_symbol, market_data, language)
    
    # Add chart metadata (for actual implementation)
    chart_data = {
        'symbol': coin_symbol,
        'current_price': market_data.get('current_price', 0),
        'price_change_24h': market_data.get('change_24h', 0),
        'market_cap': market_data.get('market_cap', 0),
        'volume_24h': market_data.get('volume_24h', 0),
        'chart_type': 'price_chart'  # Can be 'price_chart', 'market_overview', 'volatility'
    }
    
    return {
        'response': formatted_response,
        'chart_data': chart_data
    }

def prepare_market_overview_with_chart(top_coins: list, language: str = 'en'):
    """
    Prepare market overview response with chart
    
    Args:
        top_coins: List of top coins with data
        language: 'en' or 'vi'
    
    Returns:
        Dict with formatted response and chart data
    """
    from src.tools.visualization import ResponseFormatter
    
    formatted_response = ResponseFormatter.format_market_overview(top_coins, language)
    
    chart_data = {
        'chart_type': 'market_overview',
        'coins': top_coins,
        'metric': 'market_cap'
    }
    
    return {
        'response': formatted_response,
        'chart_data': chart_data
    }
