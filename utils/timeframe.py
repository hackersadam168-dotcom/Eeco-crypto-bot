"""Timeframe utilities."""

def timeframe_to_minutes(timeframe: str) -> int:
    """Convert timeframe string to minutes.
    
    Args:
        timeframe: Timeframe string (e.g., '15m', '1H', '4H', '1D')
        
    Returns:
        Timeframe in minutes
    """
    timeframe = timeframe.upper().strip()
    
    if timeframe.endswith('M'):
        return int(timeframe[:-1])
    elif timeframe.endswith('H'):
        return int(timeframe[:-1]) * 60
    elif timeframe.endswith('D'):
        return int(timeframe[:-1]) * 1440
    elif timeframe.endswith('W'):
        return int(timeframe[:-1]) * 10080
    
    return 60  # Default to 1H

def minutes_to_timeframe(minutes: int) -> str:
    """Convert minutes to timeframe string.
    
    Args:
        minutes: Minutes
        
    Returns:
        Timeframe string
    """
    if minutes == 15:
        return '15m'
    elif minutes == 60:
        return '1H'
    elif minutes == 240:
        return '4H'
    elif minutes == 1440:
        return '1D'
    elif minutes < 60:
        return f'{minutes}m'
    elif minutes < 1440:
        hours = minutes // 60
        return f'{hours}H'
    else:
        days = minutes // 1440
        return f'{days}D'
