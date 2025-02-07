# Document Deployment System

This module provides a robust system for deploying documents along with their associated artifacts and metadata.

## Directory Structure

The system creates the following directory structure:
```
artifacts/
├── documents/     # Stores deployed documents
├── artifacts/     # Stores associated artifacts
└── metadata/      # Stores JSON metadata files
```

## Usage

### Basic Usage

```python
from document_deploy import DocumentDeployer

# Initialize the deployer
deployer = DocumentDeployer()

# Deploy a document with artifacts and metadata
deployment = deployer.deploy_document(
    document_path="path/to/your/document.pdf",
    artifacts=["path/to/data.csv", "path/to/figures.png"],
    metadata={
        "version": "1.0",
        "author": "Team Name",
        "description": "Document description"
    }
)

# Get deployment ID
deployment_id = deployment['deployment_id']
```

### Retrieving Deployment Information

```python
# Get metadata for a specific deployment
metadata = deployer.get_deployment_metadata(deployment_id)

# List all deployments
all_deployments = deployer.list_deployments()
```

## Features

- Automatic directory structure creation
- Unique deployment IDs based on timestamp and document name
- Metadata storage in JSON format
- Support for multiple artifacts per document
- Easy retrieval of deployment information
- Automatic file copying and organization

## Metadata Structure

Each deployment generates a metadata JSON file with the following structure:

```json
{
    "deployment_id": "YYYYMMDD_HHMMSS_documentname",
    "timestamp": "ISO-format timestamp",
    "document": "relative/path/to/document",
    "artifacts": [
        "relative/path/to/artifact1",
        "relative/path/to/artifact2"
    ],
    "custom_metadata": {
        // User-provided metadata
    }
}
``` 