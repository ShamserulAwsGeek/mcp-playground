from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

#Initialize FastMCP server:
mcp = FastMCP("weather")

#constants:
NWS_API_BASE_URL = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def get_nws_request(url: str) -> dict[str, Any] | None:
    """
    Make a GET request to the NWS API with proper error handling and return the JSON response.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
        }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except Exception:
            return None
        
def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
        Event: {props.get('event', 'Unknown')}
        Area: {props.get('areaDesc', 'Unknown')}
        Severity: {props.get('severity', 'Unknown')}
        Description: {props.get('description', 'No description available')}
        Instructions: {props.get('instruction', 'No specific instructions provided')}
        """

@mcp.tool()
async def get_weather_alerts(state:str) -> str:
    """
    Get weather alerts for USA states.

    Args:
        state (str): The two-letter state code (e.g., 'CA' for California

    """
    
    url = f"{NWS_API_BASE_URL}/alerts/active/area/{state}"
    data = await get_nws_request(url)

    
    if not data or "features" not in data:
        return "unable to get weather alerts or no alerts found"
    
    if not data["features"]:
        return "No active weather alerts for this state."
    
    alerts = [format_alert(feature) for feature in data["features"]]   
    return "\n---\n".join(alerts)


@mcp.resource("config://app")
def get_config() -> str:
    """
    Get the configuration for the weather app.

    Returns:
        str: The configuration string.
    """
    return "Weather App Configuration"

@mcp.resource("echo://{message}")
def echo(message: str) -> str:
    """ Echo a message as resource """
    return f"Resource echo: {message}"