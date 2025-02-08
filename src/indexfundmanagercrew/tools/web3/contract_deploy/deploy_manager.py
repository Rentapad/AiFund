import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from web3 import Web3
from eth_typing import Address

class ContractDeployManager:
    def __init__(self, base_path: str = "contract_deployments"):
        """
        Initialize the contract deployment manager.
        
        Args:
            base_path (str): Base directory for all contract deployments and artifacts
        """
        self.base_path = Path(base_path)
        self.contracts_path = self.base_path / "contracts"
        self.artifacts_path = self.base_path / "artifacts"
        self.deployments_path = self.base_path / "deployments"
        self._create_directory_structure()

    def _create_directory_structure(self) -> None:
        """Create the necessary directory structure if it doesn't exist."""
        for path in [self.contracts_path, self.artifacts_path, self.deployments_path]:
            path.mkdir(parents=True, exist_ok=True)

    def save_contract_artifact(
        self,
        contract_name: str,
        abi: List[Dict],
        bytecode: str,
        source_code: str,
        compiler_version: str,
        constructor_arguments: Optional[List] = None,
        optimization_used: bool = True,
        optimization_runs: int = 200,
        additional_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Save contract compilation artifacts.
        
        Args:
            contract_name: Name of the contract
            abi: Contract ABI
            bytecode: Contract bytecode
            source_code: Original source code
            compiler_version: Solidity compiler version
            constructor_arguments: Constructor arguments if any
            optimization_used: Whether optimization was used
            optimization_runs: Number of optimization runs
            additional_metadata: Any additional metadata to store
            
        Returns:
            Dict containing artifact information
        """
        # Generate artifact ID
        artifact_id = f"{contract_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Prepare artifact data
        artifact_data = {
            "artifact_id": artifact_id,
            "contract_name": contract_name,
            "created_at": datetime.now().isoformat(),
            "abi": abi,
            "bytecode": bytecode,
            "source_code": source_code,
            "compiler": {
                "version": compiler_version,
                "optimization_used": optimization_used,
                "optimization_runs": optimization_runs
            },
            "constructor_arguments": constructor_arguments,
            "metadata": additional_metadata or {}
        }

        # Save artifact
        artifact_file = self.artifacts_path / f"{artifact_id}.json"
        with open(artifact_file, 'w') as f:
            json.dump(artifact_data, f, indent=2)

        return artifact_data

    def save_deployment(
        self,
        artifact_id: str,
        network: str,
        address: Union[str, Address],
        deployer_address: Union[str, Address],
        transaction_hash: str,
        constructor_args: Optional[List] = None,
        deployment_args: Optional[Dict] = None
    ) -> Dict:
        """
        Save contract deployment information.
        
        Args:
            artifact_id: ID of the contract artifact
            network: Network where contract was deployed
            address: Deployed contract address
            deployer_address: Address that deployed the contract
            transaction_hash: Deployment transaction hash
            constructor_args: Constructor arguments used
            deployment_args: Additional deployment arguments/parameters
            
        Returns:
            Dict containing deployment information
        """
        # Load artifact data
        artifact_file = self.artifacts_path / f"{artifact_id}.json"
        if not artifact_file.exists():
            raise FileNotFoundError(f"Artifact not found: {artifact_id}")

        with open(artifact_file) as f:
            artifact_data = json.load(f)

        # Generate deployment ID
        deployment_id = f"{artifact_data['contract_name']}_{network}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Prepare deployment data
        deployment_data = {
            "deployment_id": deployment_id,
            "artifact_id": artifact_id,
            "network": network,
            "contract_name": artifact_data['contract_name'],
            "address": Web3.to_checksum_address(address),
            "deployer": Web3.to_checksum_address(deployer_address),
            "transaction_hash": transaction_hash,
            "timestamp": datetime.now().isoformat(),
            "constructor_args": constructor_args,
            "deployment_args": deployment_args or {},
            "verified": False
        }

        # Save deployment info
        deployment_file = self.deployments_path / f"{deployment_id}.json"
        with open(deployment_file, 'w') as f:
            json.dump(deployment_data, f, indent=2)

        return deployment_data

    def get_artifact(self, artifact_id: str) -> Optional[Dict]:
        """Get contract artifact by ID."""
        artifact_file = self.artifacts_path / f"{artifact_id}.json"
        if artifact_file.exists():
            with open(artifact_file) as f:
                return json.load(f)
        return None

    def get_deployment(self, deployment_id: str) -> Optional[Dict]:
        """Get deployment information by ID."""
        deployment_file = self.deployments_path / f"{deployment_id}.json"
        if deployment_file.exists():
            with open(deployment_file) as f:
                return json.load(f)
        return None

    def list_artifacts(self, contract_name: Optional[str] = None) -> List[Dict]:
        """List all artifacts, optionally filtered by contract name."""
        artifacts = []
        for artifact_file in self.artifacts_path.glob("*.json"):
            with open(artifact_file) as f:
                artifact = json.load(f)
                if not contract_name or artifact['contract_name'] == contract_name:
                    artifacts.append(artifact)
        return artifacts

    def list_deployments(
        self,
        contract_name: Optional[str] = None,
        network: Optional[str] = None
    ) -> List[Dict]:
        """List all deployments, optionally filtered by contract name and/or network."""
        deployments = []
        for deployment_file in self.deployments_path.glob("*.json"):
            with open(deployment_file) as f:
                deployment = json.load(f)
                if (not contract_name or deployment['contract_name'] == contract_name) and \
                   (not network or deployment['network'] == network):
                    deployments.append(deployment)
        return deployments

    def update_deployment_verification(
        self,
        deployment_id: str,
        verified: bool = True,
        verification_data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Update contract verification status."""
        deployment_file = self.deployments_path / f"{deployment_id}.json"
        if not deployment_file.exists():
            return None

        with open(deployment_file) as f:
            deployment_data = json.load(f)

        deployment_data['verified'] = verified
        if verification_data:
            deployment_data['verification_data'] = verification_data

        with open(deployment_file, 'w') as f:
            json.dump(deployment_data, f, indent=2)

        return deployment_data

# Example usage
if __name__ == "__main__":
    manager = ContractDeployManager()
    
    # Example artifact saving
    try:
        artifact = manager.save_contract_artifact(
            contract_name="MyToken",
            abi=[],  
            bytecode="0x...",  
            source_code="// SPDX-License-Identifier...",
            compiler_version="0.8.19",
            constructor_arguments=["TokenName", "TKN", 18],
            additional_metadata={"author": "Team"}
        )
        print(f"Artifact saved: {artifact['artifact_id']}")
        
        # Example deployment saving
        deployment = manager.save_deployment(
            artifact_id=artifact['artifact_id'],
            network="ethereum_mainnet",
            address="0x...",
            deployer_address="0x...",
            transaction_hash="0x...",
            constructor_args=["TokenName", "TKN", 18]
        )
        print(f"Deployment saved: {deployment['deployment_id']}")
        
    except Exception as e:
        print(f"Error: {e}") 