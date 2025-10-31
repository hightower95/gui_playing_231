# Azure DevOps Integration

## Overview

The DevOps tab provides integration with Azure DevOps, specifically for executing work item queries and viewing results.

## Features

### Azure DevOps Query Viewer

**Location:** DevOps → Query Viewer

The Query Viewer allows you to:
- Connect to Azure DevOps organizations
- Execute saved queries by ID
- Execute custom WIQL (Work Item Query Language) queries
- View results in a tabular format

## Setup

### Azure DevOps Connection

To connect to Azure DevOps, you need:

1. **Organization Name**: Your Azure DevOps organization (e.g., `mycompany`)
2. **Project Name**: The project within your organization (e.g., `MyProject`)
3. **Personal Access Token (PAT)**: A token with "Work Items (Read)" permission

#### Creating a Personal Access Token

1. Go to Azure DevOps: `https://dev.azure.com/{your-organization}`
2. Click on your profile icon (top right) → Security
3. Click "+ New Token"
4. Configure:
   - **Name**: Something descriptive like "Query Viewer Tool"
   - **Organization**: Select your organization
   - **Expiration**: Choose expiration date
   - **Scopes**: Select "Work Items" → "Read"
5. Click "Create"
6. **IMPORTANT**: Copy the token immediately (you won't be able to see it again)

## Usage

### Connecting to Azure DevOps

1. Open the **DevOps** tab
2. Select the **Query Viewer** sub-tab
3. Fill in the connection details:
   - Organization: Your Azure DevOps organization name
   - Project: Your project name
   - PAT: Your Personal Access Token
4. Click **Connect**

Once connected, the "Execute Query" button will be enabled.

### Running Saved Queries

1. Select "Saved Query (ID)" from the Query Type dropdown
2. Enter the GUID of your saved query
   - You can find this in Azure DevOps by navigating to Boards → Queries → Right-click a query → "Copy query URL"
   - The GUID is in the URL: `?id=12345678-1234-1234-1234-123456789012`
3. Click **Execute Query**

### Running WIQL Queries

1. Select "WIQL Query" from the Query Type dropdown
2. Enter your WIQL query in the text area

**Example WIQL:**
```wiql
SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo]
FROM WorkItems
WHERE [System.WorkItemType] = 'Bug'
AND [System.State] = 'Active'
ORDER BY [System.CreatedDate] DESC
```

3. Click **Execute Query**

### Common WIQL Examples

#### All Active Bugs
```wiql
SELECT [System.Id], [System.Title], [System.State]
FROM WorkItems
WHERE [System.WorkItemType] = 'Bug'
AND [System.State] = 'Active'
```

#### Tasks Assigned to Me
```wiql
SELECT [System.Id], [System.Title], [System.State]
FROM WorkItems
WHERE [System.WorkItemType] = 'Task'
AND [System.AssignedTo] = @Me
```

#### Recently Created Items
```wiql
SELECT [System.Id], [System.Title], [System.WorkItemType], [System.State]
FROM WorkItems
WHERE [System.CreatedDate] >= @StartOfDay('-7d')
ORDER BY [System.CreatedDate] DESC
```

## Implementation Status

### ✅ Completed
- UI layout and design
- Connection form (organization, project, PAT)
- Query type selection (Saved Query vs WIQL)
- Query input area with syntax examples
- Results table display
- Status messages and error handling

### 🚧 Pending Implementation
- Actual Azure DevOps API integration
- Work item details expansion
- Query result export (CSV, Excel)
- Query history/favorites
- Advanced filtering on results

## Technical Details

### Azure DevOps Python SDK

To implement the actual API calls, install the Azure DevOps SDK:

```bash
pip install azure-devops
```

### Example Connection Code

```python
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

# Create connection
credentials = BasicAuthentication('', pat)
connection = Connection(
    base_url=f'https://dev.azure.com/{organization}',
    creds=credentials
)

# Get work item tracking client
wit_client = connection.clients.get_work_item_tracking_client()
```

### Example WIQL Execution

```python
from azure.devops.v7_0.work_item_tracking.models import Wiql

# Execute WIQL query
wiql_object = Wiql(query=wiql_string)
query_result = wit_client.query_by_wiql(wiql_object)

# Get full work item details
work_item_ids = [item.id for item in query_result.work_items]
work_items = wit_client.get_work_items(ids=work_item_ids)
```

## Files

- **View**: `app/devops/QueryViewer/view.py` - UI components
- **Model**: `app/devops/QueryViewer/model.py` - Data and API logic
- **Presenter**: `app/devops/QueryViewer/presenter.py` - Business logic
- **Tab Container**: `app/devops/devops_tab.py` - Main DevOps tab

## Future Enhancements

- **Saved Queries**: Save frequently used queries locally
- **Query Templates**: Pre-built query templates for common scenarios
- **Work Item Details**: Click on row to see full work item details
- **Bulk Operations**: Select multiple items for bulk updates
- **Charts/Visualizations**: Visual representations of query results
- **Export**: Export results to CSV, Excel, or JSON
- **Query Builder**: Visual query builder for non-WIQL users
- **Multiple Organizations**: Support switching between multiple Azure DevOps organizations

## Troubleshooting

### "Connection failed" Error
- Verify your organization and project names are correct
- Ensure your PAT hasn't expired
- Check that the PAT has "Work Items (Read)" scope
- Verify network connectivity to `https://dev.azure.com`

### "Query execution failed" Error
- For saved queries: Verify the Query ID (GUID) is correct
- For WIQL: Check syntax - WIQL is case-sensitive for field names
- Ensure you have permission to access the work items

### Empty Results
- Query might be valid but returning no items
- Check your WHERE clause conditions
- Verify work items matching your criteria exist in the project
