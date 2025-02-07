from typing import Type, ClassVar, List, Optional, Dict, Any
from datetime import timedelta
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
from ..api.Cookie import (
    CookieAPI,
    APICache,
    CookieAPIError,
    AgentFilter,
    SortOrder,
    apply_filters_and_sort
)
from crewai.tools import tool
from dotenv import load_dotenv
import os

class CookieFilterInput(BaseModel):
    filters: Dict[str, Any] = Field(description="Filters to apply to the Cookie API data")
    sort_order: Optional[str] = Field(default="desc", description="Sort order for the results")

class CookieFilterTool(BaseTool):
    name: str = "filter_cookie_data"
    description: str = "Filter and sort Cookie API data based on specified criteria"
    args_schema: Type[BaseModel] = CookieFilterInput
    api: Optional[CookieAPI] = None
    max_pages: int = 10

    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, api_key: Optional[str] = None, cache_duration: timedelta = timedelta(hours=1), max_pages: int = 10):
        super().__init__()
        if api_key is None:
            load_dotenv()
            api_key = os.getenv('COOKIE_API_KEY')
            if not api_key:
                raise ValueError("COOKIE_API_KEY not found in environment variables")
                
        self.api = CookieAPI(api_key)
        self.api.use_cache = True
        self.api.cache = APICache(cache_duration=cache_duration)
        self.max_pages = max_pages

    def _run(self, filters: Dict[str, Any], sort_order: str = "desc") -> str:
        try:
            data = self.api.get_data()
            filtered_data = apply_filters_and_sort(data, filters, SortOrder[sort_order.upper()])
            return str(filtered_data)
        except CookieAPIError as e:
            return f"Error filtering Cookie data: {str(e)}"

class AgentDetailInput(BaseModel):
    contract_address: str = Field(description="The contract address of the agent to get details for")
    interval: str = Field(default="_7Days", description="Time interval for metrics (_7Days, _30Days, _90Days)")

class AgentDetailTool(BaseTool):
    name: str = "get_agent_details"
    description: str = "Get detailed metrics for a specific agent by contract address"
    args_schema: Type[BaseModel] = AgentDetailInput
    api: Optional[CookieAPI] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        if api_key is None:
            load_dotenv()
            api_key = os.getenv('COOKIE_API_KEY')
            if not api_key:
                raise ValueError("COOKIE_API_KEY not found in environment variables")
        self.api = CookieAPI(api_key)

    def _run(self, contract_address: str, interval: str = "_7Days") -> str:
        try:
            data = self.api.get_agent_by_contract_address(contract_address, interval)
            return str(data)
        except CookieAPIError as e:
            return f"Error getting agent details: {str(e)}"

class TweetSearchInput(BaseModel):
    query: str = Field(description="The search query for tweets")
    from_date: str = Field(description="Start date for tweet search (YYYY-MM-DD)")
    to_date: str = Field(description="End date for tweet search (YYYY-MM-DD)")

class TweetSearchTool(BaseTool):
    name: str = "search_tweets"
    description: str = "Search tweets related to agents within a date range"
    args_schema: Type[BaseModel] = TweetSearchInput
    api: Optional[CookieAPI] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        if api_key is None:
            load_dotenv()
            api_key = os.getenv('COOKIE_API_KEY')
            if not api_key:
                raise ValueError("COOKIE_API_KEY not found in environment variables")
        self.api = CookieAPI(api_key)

    def _run(self, query: str, from_date: str, to_date: str) -> str:
        try:
            data = self.api.search_tweets(query, from_date, to_date)
            return str(data)
        except CookieAPIError as e:
            return f"Error searching tweets: {str(e)}"

# Decorator-based Tools
@tool("check_api_status")
def check_api_health(api_key: Optional[str] = None) -> str:
    """Check if the Cookie API is responsive and return rate limits"""
    try:
        if api_key is None:
            load_dotenv()
            api_key = os.getenv('COOKIE_API_KEY')
            if not api_key:
                raise ValueError("COOKIE_API_KEY not found in environment variables")
        api = CookieAPI(api_key)
        rate_limits = api.rate_limits
        return f"Rate Limits: {rate_limits}"
    except Exception as e:
        return f"API Health Check Failed: {str(e)}"

@tool("get_quota_info")
def get_quota_status(api_key: Optional[str] = None) -> str:
    """Check current API quota status"""
    try:
        if api_key is None:
            load_dotenv()
            api_key = os.getenv('COOKIE_API_KEY')
            if not api_key:
                raise ValueError("COOKIE_API_KEY not found in environment variables")
        api = CookieAPI(api_key)
        return str(api.check_quota_status())
    except Exception as e:
        return f"Failed to get quota status: {str(e)}"