from typing import Type, Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from crewai.tools import BaseTool
from defillama import DefiLlama
from datetime import datetime

class PriceFetcherInput(BaseModel):
    chain: str = Field(description="The blockchain chain (e.g., 'ethereum', 'binance-smart-chain')")
    token_address: str = Field(description="The token contract address")
    timestamp: Optional[int] = Field(default=None, description="Optional timestamp for historical price (Unix timestamp)")

class PriceFetcherAgent(BaseTool):
    name: str = "fetch_defi_prices"
    description: str = "Fetch current or historical token prices from DeFi Llama"
    args_schema: Type[BaseModel] = PriceFetcherInput
    llama: DefiLlama = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self):
        super().__init__()
        self.llama = DefiLlama()

    def _run(self, chain: str, token_address: str, timestamp: Optional[int] = None) -> str:
        try:
            # Format the coin identifier
            coin_id = f"{chain}:{token_address}"

            if timestamp:
                # Get historical price
                response = self.llama.get_token_historical_prices(
                    coins=coin_id,
                    timestamp=timestamp,
                    searchWidth="4h"
                )
            else:
                # Get current price
                response = self.llama.get_token_current_prices(
                    coins=coin_id,
                    searchWidth="4h"
                )

            if response and 'coins' in response:
                coin_data = response['coins'].get(coin_id)
                if coin_data:
                    price = coin_data.get('price', 0)
                    timestamp = coin_data.get('timestamp', datetime.now().timestamp())
                    confidence = coin_data.get('confidence', 0)
                    
                    return f"Price: ${price:.4f}, Timestamp: {datetime.fromtimestamp(timestamp)}, Confidence: {confidence}"
                return f"No price data found for {coin_id}"
            return f"Error: Invalid response format from DeFi Llama"

        except Exception as e:
            return f"Error fetching price: {str(e)}"

class ProtocolInfoInput(BaseModel):
    protocol_name: str = Field(description="The name of the DeFi protocol (e.g., 'uniswap', 'aave')")

class ProtocolInfoTool(BaseTool):
    name: str = "get_protocol_info"
    description: str = "Get detailed information about a DeFi protocol including TVL and other metrics"
    args_schema: Type[BaseModel] = ProtocolInfoInput
    llama: DefiLlama = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self):
        super().__init__()
        self.llama = DefiLlama()

    def _run(self, protocol_name: str) -> str:
        try:
            response = self.llama.get_protocol(protocol_name)
            
            if not response:
                return f"No data found for protocol: {protocol_name}"

            # Extract relevant information
            tvl = response.get('tvl', [])
            current_tvl = tvl[-1]['totalLiquidityUSD'] if tvl else 0
            
            description = response.get('description', 'No description available')
            category = response.get('category', 'Unknown')
            chains = response.get('chains', [])

            return (
                f"Protocol: {protocol_name}\n"
                f"Current TVL: ${current_tvl:,.2f}\n"
                f"Category: {category}\n"
                f"Chains: {', '.join(chains)}\n"
                f"Description: {description}"
            )

        except Exception as e:
            return f"Error fetching protocol info: {str(e)}"

class TVLMetricsInput(BaseModel):
    chain: Optional[str] = Field(default=None, description="Optional blockchain chain for specific chain TVL")

class TVLMetricsTool(BaseTool):
    name: str = "get_tvl_metrics"
    description: str = "Get Total Value Locked (TVL) metrics for all chains or a specific chain"
    args_schema: Type[BaseModel] = TVLMetricsInput
    llama: DefiLlama = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self):
        super().__init__()
        self.llama = DefiLlama()

    def _run(self, chain: Optional[str] = None) -> str:
        try:
            if chain:
                response = self.llama.get_historical_tvl_chain(chain)
                if not response:
                    return f"No TVL data found for chain: {chain}"
                
                current_tvl = response[-1]['totalLiquidityUSD'] if response else 0
                return f"Current TVL for {chain}: ${current_tvl:,.2f}"
            else:
                response = self.llama.get_chains_current_tvl()
                if not response:
                    return "No TVL data available"

                # Format the top 5 chains by TVL
                sorted_chains = sorted(response, key=lambda x: x.get('tvl', 0), reverse=True)[:5]
                result = "Top 5 Chains by TVL:\n"
                for chain_data in sorted_chains:
                    result += f"{chain_data['name']}: ${chain_data.get('tvl', 0):,.2f}\n"
                return result

        except Exception as e:
            return f"Error fetching TVL metrics: {str(e)}"
