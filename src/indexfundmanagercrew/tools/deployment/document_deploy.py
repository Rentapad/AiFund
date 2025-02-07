import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

class DocumentDeployer:
    def __init__(self, base_path: str = "artifacts"):
        """
        Initialize the document deployer with base paths for artifacts and metadata.
        
        Args:
            base_path (str): Base directory for all artifacts and metadata
        """
        self.base_path = Path(base_path)
        self.documents_path = self.base_path / "documents"
        self.artifacts_path = self.base_path / "artifacts"
        self.metadata_path = self.base_path / "metadata"
        self._create_directory_structure()

    def _create_directory_structure(self) -> None:
        """Create the necessary directory structure if it doesn't exist."""
        for path in [self.documents_path, self.artifacts_path, self.metadata_path]:
            path.mkdir(parents=True, exist_ok=True)

    def deploy_document(
        self,
        document_path: Union[str, Path],
        artifacts: Optional[List[Union[str, Path]]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Deploy a document with its artifacts and metadata.
        
        Args:
            document_path: Path to the document to deploy
            artifacts: List of paths to associated artifacts
            metadata: Additional metadata to store with the document
            
        Returns:
            Dict containing deployment information
        """
        document_path = Path(document_path)
        if not document_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")

        # Generate deployment ID based on timestamp and document name
        deployment_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{document_path.stem}"
        
        # Create deployment-specific directories
        deploy_doc_dir = self.documents_path / deployment_id
        deploy_artifacts_dir = self.artifacts_path / deployment_id
        deploy_doc_dir.mkdir(parents=True, exist_ok=True)
        deploy_artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Copy document
        document_dest = deploy_doc_dir / document_path.name
        shutil.copy2(document_path, document_dest)

        # Copy artifacts if provided
        artifact_paths = []
        if artifacts:
            for artifact in artifacts:
                artifact_path = Path(artifact)
                if artifact_path.exists():
                    artifact_dest = deploy_artifacts_dir / artifact_path.name
                    shutil.copy2(artifact_path, artifact_dest)
                    artifact_paths.append(str(artifact_dest.relative_to(self.base_path)))
                else:
                    print(f"Warning: Artifact not found: {artifact_path}")

        # Prepare metadata
        deployment_metadata = {
            "deployment_id": deployment_id,
            "timestamp": datetime.now().isoformat(),
            "document": str(document_dest.relative_to(self.base_path)),
            "artifacts": artifact_paths,
            "custom_metadata": metadata or {}
        }

        # Save metadata
        metadata_file = self.metadata_path / f"{deployment_id}.json"
        with open(metadata_file, 'w') as f:
            json.dump(deployment_metadata, f, indent=2)

        return deployment_metadata

    def get_deployment_metadata(self, deployment_id: str) -> Optional[Dict]:
        """
        Retrieve metadata for a specific deployment.
        
        Args:
            deployment_id: ID of the deployment
            
        Returns:
            Dict containing deployment metadata if found, None otherwise
        """
        metadata_file = self.metadata_path / f"{deployment_id}.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                return json.load(f)
        return None

    def list_deployments(self) -> List[Dict]:
        """
        List all deployments and their metadata.
        
        Returns:
            List of deployment metadata
        """
        deployments = []
        for metadata_file in self.metadata_path.glob("*.json"):
            with open(metadata_file) as f:
                deployments.append(json.load(f))
        return deployments

# Example usage
if __name__ == "__main__":
    deployer = DocumentDeployer()
    
    # Example deployment
    try:
        deployment = deployer.deploy_document(
            document_path="example.pdf",
            artifacts=["data.csv", "figures.png"],
            metadata={"version": "1.0", "author": "AI Team"}
        )
        print(f"Deployment successful: {deployment['deployment_id']}")
        
        # List all deployments
        all_deployments = deployer.list_deployments()
        print(f"Total deployments: {len(all_deployments)}")
    except FileNotFoundError as e:
        print(f"Error: {e}") 