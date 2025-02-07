import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, List
from dotenv import load_dotenv
import os
import json
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path

config
# Filter-related code
class SortOrder(Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"

@dataclass
class RangeFilter:
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def matches(self, value: float) -> bool:
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True

@dataclass
class AgentFilter:
    market_cap: RangeFilter = field(default_factory=RangeFilter)
    volume_24h: RangeFilter = field(default_factory=RangeFilter)
    liquidity: RangeFilter = field(default_factory=RangeFilter)
    mindshare: RangeFilter = field(default_factory=RangeFilter)
    holders_count: RangeFilter = field(default_factory=RangeFilter)
    chains: List[int] = field(default_factory=list)  # Chain IDs: -2 for Solana, 8453 for Base network
    sort_by: str = "marketCap"
    sort_order: SortOrder = SortOrder.DESCENDING

    def set_market_cap_range(self, min_value: Optional[float] = None, max_value: Optional[float] = None) -> None:
        self.market_cap = RangeFilter(min_value, max_value)

    def set_volume_range(self, min_value: Optional[float] = None, max_value: Optional[float] = None) -> None:
        self.volume_24h = RangeFilter(min_value, max_value)

    def set_liquidity_range(self, min_value: Optional[float] = None, max_value: Optional[float] = None) -> None:
        self.liquidity = RangeFilter(min_value, max_value)

    def set_mindshare_range(self, min_value: Optional[float] = None, max_value: Optional[float] = None) -> None:
        self.mindshare = RangeFilter(min_value, max_value)

    def set_holders_range(self, min_value: Optional[float] = None, max_value: Optional[float] = None) -> None:
        self.holders_count = RangeFilter(min_value, max_value)

    def set_chains(self, chains: List[int]) -> None:
        """
        Set the chain IDs to filter by.
        Special chain IDs:
        - -2: Solana network
        - 8453: Base network
        
        Args:
            chains (List[int]): List of chain IDs to filter by
        """
        self.chains = chains

    def set_sorting(self, field: str, order: SortOrder = SortOrder.DESCENDING) -> None:
        self.sort_by = field
        self.sort_order = order

    def matches(self, agent: Dict[str, Any]) -> bool:
        # Check numeric ranges
        if not self.market_cap.matches(agent.get('marketCap', 0)):
            return False
        if not self.volume_24h.matches(agent.get('volume24Hours', 0)):
            return False
        if not self.liquidity.matches(agent.get('liquidity', 0)):
            return False
        if not self.mindshare.matches(agent.get('mindshare', 0)):
            return False
        if not self.holders_count.matches(agent.get('holdersCount', 0)):
            return False

        # Check chains if specified
        if self.chains:
            agent_chains = [contract['chain'] for contract in agent.get('contracts', [])]
            if not any(chain in self.chains for chain in agent_chains):
                return False

        return True

def apply_filters_and_sort(agents: List[Dict[str, Any]], filter_params: AgentFilter) -> List[Dict[str, Any]]:
    """Apply filters and sorting to a list of agents"""
    # Filter agents
    filtered_agents = [agent for agent in agents if filter_params.matches(agent)]
    
    # Sort agents
    reverse = filter_params.sort_order == SortOrder.DESCENDING
    return sorted(
        filtered_agents,
        key=lambda x: x.get(filter_params.sort_by, 0),
        reverse=reverse
    )

# Cache-related code
class APICache:
    """Cache for API responses"""
    
    def __init__(self, cache_dir: str = None, cache_duration: timedelta = timedelta(hours=1)):
        if cache_dir is None:
            # Use a consistent location in the workspace
            workspace_root = Path(__file__).parent.parent.parent
            cache_dir = workspace_root / ".cache" / "cookieswarm"
        else:
            cache_dir = Path(cache_dir)
            
        self.cache_dir = cache_dir
        self.cache_duration = cache_duration
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for a key"""
        # Use a hash of the key to avoid filename issues
        import hashlib
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.json"
        
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data if it exists and is not expired"""
        cache_file = self._get_cache_file(key)
        
        if not cache_file.exists():
            return None
            
        try:
            with cache_file.open('r') as f:
                cached = json.load(f)
                
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached['timestamp'])
            if datetime.now() - cached_time > self.cache_duration:
                return None
                
            return cached['data']
            
        except (json.JSONDecodeError, KeyError, ValueError):
            return None
            
    def set(self, key: str, data: Dict[str, Any]) -> None:
        """Cache data with timestamp"""
        cache_file = self._get_cache_file(key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        with cache_file.open('w') as f:
            json.dump(cache_data, f)
            
    def clear(self) -> None:
        """Clear all cached data"""
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()
            
    def clear_expired(self) -> None:
        """Clear only expired cache entries"""
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with cache_file.open('r') as f:
                    cached = json.load(f)
                cached_time = datetime.fromisoformat(cached['timestamp'])
                if datetime.now() - cached_time > self.cache_duration:
                    cache_file.unlink()
            except (json.JSONDecodeError, KeyError, ValueError):
                cache_file.unlink()

class CookieAPIError(Exception):
    """Custom exception for CookieAPI errors"""
    pass

class CookieAPI:
    """
    A wrapper class for the Cookie API that provides methods to interact with various endpoints.
    """
    
    def __init__(self, api_key: str, use_cache: bool = True, 
                 cache_duration: timedelta = timedelta(hours=1)):
        """
        Initialize the CookieAPI client.
        
        Args:
            api_key (str): The API key for authentication
            use_cache (bool): Whether to use caching
            cache_duration (timedelta): How long to cache responses
        """
        if not api_key:
            raise ValueError("API key is required")
            
        self.api_key = api_key
        self.base_url = 'https://api.cookie.fun'
        self.headers = {'x-api-key': self.api_key}
        self.use_cache = use_cache
        self.cache = APICache(cache_duration=cache_duration) if use_cache else None

    def _get_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """Generate a cache key for the request"""
        key_parts = [endpoint]
        if params:
            key_parts.extend(f"{k}={v}" for k, v in sorted(params.items()))
        return "|".join(key_parts)

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the API with caching.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            params (Optional[Dict]): Query parameters
            
        Returns:
            Dict[str, Any]: JSON response from the API
            
        Raises:
            CookieAPIError: If the API request fails
        """
        # Check cache first
        if self.use_cache and method == 'GET':
            cache_key = self._get_cache_key(endpoint, params)
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        url = f'{self.base_url}{endpoint}'
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            # Store rate limit information
            self.rate_limit = {
                'limit': response.headers.get('X-RateLimit-Limit'),
                'remaining': response.headers.get('X-RateLimit-Remaining'),
                'reset': response.headers.get('X-RateLimit-Reset')
            }
            
            response.raise_for_status()
            data = response.json()
            
            # Handle standardized response format
            if 'ok' in data and data.get('success', False):
                result = data['ok']
            elif 'error' in data:
                raise CookieAPIError(data['error'].get('message', 'Unknown error'))
            else:
                result = data

            # Cache the result if it's a GET request
            if self.use_cache and method == 'GET':
                self.cache.set(cache_key, result)

            return result
            
        except requests.exceptions.RequestException as e:
            raise CookieAPIError(f"API request failed: {str(e)}")
        except ValueError as e:
            raise CookieAPIError(f"Failed to parse API response: {str(e)}")

    def get_agent_by_twitter_username(self, twitter_username: str, interval: str = '_7Days') -> Dict[str, Any]:
        """
        Get agent information by Twitter username.
        
        Args:
            twitter_username (str): Twitter username to look up
            interval (str): Time interval for data (e.g., '_7Days')
            
        Returns:
            Dict[str, Any]: Agent information
        """
        endpoint = f'/v2/agents/twitterUsername/{twitter_username}'
        return self._make_request('GET', endpoint, params={'interval': interval})

    def get_agent_by_contract_address(self, contract_address: str, interval: str = '_7Days') -> Dict[str, Any]:
        """
        Get agent information by contract address.
        
        Args:
            contract_address (str): Contract address to look up
            interval (str): Time interval for data (e.g., '_3Days')
            
        Returns:
            Dict[str, Any]: Agent information
        """
        endpoint = f'/v2/agents/contractAddress/{contract_address}'
        return self._make_request('GET', endpoint, params={'interval': interval})

    def get_agents_paged(self, interval: str = '_7Days', page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Get paginated list of agents.
        
        Args:
            interval (str): Time interval for data
            page (int): Page number
            page_size (int): Number of items per page (max 25)
            
        Returns:
            Dict[str, Any]: Paginated agent information
        """
        endpoint = '/v2/agents/agentsPaged'
        params = {
            'interval': interval,
            'page': page,
            'pageSize': min(page_size, 25)  # Enforce max page size
        }
        return self._make_request('GET', endpoint, params=params)

    def search_tweets(self, search_query: str, from_date: str, to_date: str) -> Dict[str, Any]:
        """
        Search tweets within a date range.
        
        Args:
            search_query (str): Search query string
            from_date (str): Start date in YYYY-MM-DD format
            to_date (str): End date in YYYY-MM-DD format
            
        Returns:
            Dict[str, Any]: Search results
        """
        endpoint = f'/v1/hackathon/search/{search_query}'
        params = {'from': from_date, 'to': to_date}
        return self._make_request('GET', endpoint, params=params)

    def check_quota_status(self) -> Dict[str, Any]:
        """
        Check API quota status.
        
        Returns:
            Dict[str, Any]: Quota status information
        """
        endpoint = '/authorization'
        return self._make_request('GET', endpoint)

    def get_filtered_agents(self, filter_params: AgentFilter, page: int = 1, page_size: int = 10, interval: str = '_7Days') -> Dict[str, Any]:
        """
        Get filtered and sorted list of agents.
        
        Args:
            filter_params (AgentFilter): Filter and sort parameters
            page (int): Page number for pagination
            page_size (int): Number of items per page
            interval (str): Time interval for data
            
        Returns:
            Dict[str, Any]: Filtered and sorted agent information
        """
        # Get all agents for the current page
        response = self.get_agents_paged(interval=interval, page=page, page_size=page_size)
        
        if not response or 'data' not in response:
            return {'data': [], 'currentPage': page, 'totalPages': 0, 'totalCount': 0}
        
        # Apply filters and sorting
        filtered_data = apply_filters_and_sort(response['data'], filter_params)
        
        # Update response with filtered data
        response['data'] = filtered_data
        response['totalCount'] = len(filtered_data)
        response['totalPages'] = (len(filtered_data) + page_size - 1) // page_size
        
        return response

    def get_all_filtered_agents(self, filter_params: AgentFilter, interval: str = '_7Days') -> List[Dict[str, Any]]:
        """
        Get all agents matching the filter criteria (fetches all pages).
        
        Args:
            filter_params (AgentFilter): Filter and sort parameters
            interval (str): Time interval for data
            
        Returns:
            List[Dict[str, Any]]: All filtered and sorted agents
        """
        all_agents = []
        page = 1
        page_size = 25  # Maximum allowed by API
        
        while True:
            response = self.get_agents_paged(interval=interval, page=page, page_size=page_size)
            if not response or 'data' not in response or not response['data']:
                break
                
            all_agents.extend(response['data'])
            
            if page >= response['totalPages']:
                break
                
            page += 1
        
        # Apply filters and sorting to all agents
        return apply_filters_and_sort(all_agents, filter_params)

    def get_agents_by_chain(self, chain_id: int, interval: str = '_7Days') -> List[Dict[str, Any]]:
        """
        Get all agents on a specific chain.
        
        Args:
            chain_id (int): Chain ID to filter by
            interval (str): Time interval for data
            
        Returns:
            List[Dict[str, Any]]: Agents on the specified chain
        """
        filter_params = AgentFilter()
        filter_params.set_chains([chain_id])
        return self.get_all_filtered_agents(filter_params, interval)

    def get_top_agents_by_metric(self, metric: str, min_value: float = 0, limit: int = 10, interval: str = '_7Days') -> List[Dict[str, Any]]:
        """
        Get top agents by a specific metric.
        
        Args:
            metric (str): Metric to sort by (e.g., 'marketCap', 'volume24Hours')
            min_value (float): Minimum value for the metric
            limit (int): Number of agents to return
            interval (str): Time interval for data
            
        Returns:
            List[Dict[str, Any]]: Top agents by the specified metric
        """
        filter_params = AgentFilter()
        filter_params.set_sorting(metric, SortOrder.DESCENDING)
        
        # Set the appropriate range filter
        if metric == 'marketCap':
            filter_params.set_market_cap_range(min_value=min_value)
        elif metric == 'volume24Hours':
            filter_params.set_volume_range(min_value=min_value)
        elif metric == 'liquidity':
            filter_params.set_liquidity_range(min_value=min_value)
        elif metric == 'mindshare':
            filter_params.set_mindshare_range(min_value=min_value)
        elif metric == 'holdersCount':
            filter_params.set_holders_range(min_value=min_value)
            
        results = self.get_all_filtered_agents(filter_params, interval)
        return results[:limit]

    @property
    def rate_limits(self) -> Dict[str, str]:
        """
        Get current rate limit information from the last request.
        
        Returns:
            Dict[str, str]: Rate limit details including limit, remaining, and reset time
        """
        return getattr(self, 'rate_limit', {})

def create_production_instance(api_key: Optional[str] = None) -> CookieAPI:
    """
    Create a production instance of CookieAPI.
    
    Args:
        api_key (Optional[str]): API key to use (if None, loads from environment)
        
    Returns:
        CookieAPI: Configured instance for production
    """
    if api_key is None:
        load_dotenv()
        api_key = os.getenv('COOKIE_API_KEY')
        if not api_key:
            raise ValueError("COOKIE_API_KEY not found in environment variables")
    return CookieAPI(api_key)

# Example usage
def main():
    try:
        api = create_production_instance()
        print("Testing API:")
        print("Quota Status:", api.check_quota_status())
        
    except CookieAPIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()