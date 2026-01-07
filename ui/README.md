# Airtable Connector for Databricks

A professional, point-and-click UI for configuring Airtable to Databricks data synchronization using the Lakeflow Community Connector template.

## Overview

This application provides an intuitive interface for users to configure, preview, and sync data from Airtable to Databricks without writing code. Built with React, TypeScript, and Tailwind CSS, it follows Databricks design patterns with a dark theme and orange accent colors.

## Features

### 🎯 Six-Tab Workflow

1. **Source Configuration**: Connect to your Airtable workspace
   - API key management
   - Base and workspace selection
   - Connection testing

2. **Target Configuration**: Configure Databricks destination
   - Workspace URL and token
   - Catalog and schema selection
   - Connection validation

3. **Browse Tables**: Explore available Airtable tables
   - Visual table cards with metadata
   - Search and filter capabilities
   - One-click table selection

4. **Data Preview**: View table data before syncing
   - Live data preview with refresh
   - Column and record statistics
   - Export capabilities

5. **Transformation**: Configure ETL sync modes
   - **Full Table Refresh**: Complete data synchronization
   - **Change Data Capture (CDC)**: Incremental updates based on timestamps
   - **Rule-Based Capture**: Custom Airtable filter formulas
   - Schema evolution options
   - Soft delete handling

6. **Sync Configuration**: Execute and schedule data syncs
   - Real-time sync status
   - Schedule configuration (manual, 15min, hourly, daily, weekly)
   - Audit logging and error notifications
   - Visual sync statistics

### 🎨 Visual Flow Diagram

Top pane shows an animated data flow visualization:
- Source (Airtable) → Transform (Lakeflow) → Target (Databricks)
- Real-time status updates
- Color-coded states
- Progress animations

## Technology Stack

- **React 18**: Modern React with functional components and hooks
- **TypeScript**: Full type safety throughout the application
- **Tailwind CSS 4.0**: Utility-first CSS framework
- **Lucide React**: Beautiful, consistent icons
- **Vite**: Fast build tool and development server

## Project Structure

```
src/
├── app/
│   ├── App.tsx                      # Main application component
│   └── components/
│       ├── SourceConfiguration.tsx  # Airtable connection setup
│       ├── TargetConfiguration.tsx  # Databricks configuration
│       ├── TableBrowser.tsx         # Table selection interface
│       ├── DataPreview.tsx          # Data preview component
│       ├── Transformation.tsx       # ETL mode configuration
│       └── SyncConfiguration.tsx    # Sync execution and scheduling
├── styles/
│   ├── theme.css                    # Global styles and theme
│   └── fonts.css                    # Font imports
└── main.tsx                         # Application entry point
```

## Component Architecture

### State Management

All application state is centralized in `App.tsx`:

```typescript
// Connection state
const [isConnected, setIsConnected] = useState(false);
const [selectedTable, setSelectedTable] = useState<string | null>(null);

// Sync state
const [syncStatus, setSyncStatus] = useState<SyncStatus>('idle');
const [isSyncing, setIsSyncing] = useState(false);

// Transformation configuration
const [syncMode, setSyncMode] = useState<SyncMode>('full');
const [customQuery, setCustomQuery] = useState('');
const [cdcTimestampField, setCdcTimestampField] = useState('Last Modified Time (Auto)');
const [cdcLookbackWindow, setCdcLookbackWindow] = useState('24 hours');
```

### Component Props Pattern

Components receive props for both reading state and updating it:

```typescript
interface TransformationProps {
  isSourceConnected: boolean;
  selectedTable: string | null;
  syncMode: 'full' | 'cdc' | 'rule';
  setSyncMode: (mode: 'full' | 'cdc' | 'rule') => void;
  customQuery: string;
  setCustomQuery: (query: string) => void;
  // ... other configuration props
}
```

## Integration with Databricks Apps

### Environment Variables

For production deployment, replace mock API keys with environment variables:

```typescript
// Example in SourceConfiguration.tsx
const AIRTABLE_API_KEY = import.meta.env.VITE_AIRTABLE_API_KEY;
const DATABRICKS_TOKEN = import.meta.env.VITE_DATABRICKS_TOKEN;
```

### API Integration Points

Replace mock functions with actual API calls:

1. **Source Configuration** (`SourceConfiguration.tsx`):
   - `handleConnect()`: Validate Airtable API key
   - `handleTestConnection()`: Test Airtable connectivity

2. **Target Configuration** (`TargetConfiguration.tsx`):
   - Validate Databricks workspace token
   - Fetch available catalogs and schemas

3. **Table Browser** (`TableBrowser.tsx`):
   - `generateMockTables()` → Fetch actual Airtable bases and tables

4. **Data Preview** (`DataPreview.tsx`):
   - `generateMockData()` → Fetch real table data from Airtable

5. **Sync Configuration** (`SyncConfiguration.tsx`):
   - `handleSync()` → Trigger actual Lakeflow sync job
   - Add job monitoring and status polling

### Lakeflow Integration

This UI is designed to work with the [Lakeflow Community Connectors](https://github.com/yyoli-db/lakeflow-community-connectors) template:

```python
# Example Python backend integration
from lakeflow_connectors import AirtableConnector

def execute_sync(config):
    connector = AirtableConnector(
        api_key=config['airtable_api_key'],
        base_id=config['base_id'],
        table_name=config['table_name']
    )
    
    if config['sync_mode'] == 'cdc':
        connector.sync_incremental(
            timestamp_field=config['cdc_timestamp_field'],
            lookback_window=config['cdc_lookback_window']
        )
    elif config['sync_mode'] == 'rule':
        connector.sync_filtered(
            filter_formula=config['custom_query']
        )
    else:
        connector.sync_full()
```

## Development

### Prerequisites

- Node.js 18+ and npm
- Modern web browser

### Installation

```bash
npm install
```

### Development Server

```bash
npm run dev
```

Visit `http://localhost:5173` to see the application.

### Build for Production

```bash
npm run build
```

The optimized production build will be in the `dist/` directory.

### Type Checking

```bash
npm run type-check
```

## Customization

### Theme Colors

Edit `/src/styles/theme.css` to customize colors:

```css
:root {
  --color-primary: #ea580c; /* Orange accent */
  --color-secondary: #0f172a; /* Dark slate */
  /* ... other theme variables */
}
```

### Adding New Sync Modes

1. Update the `SyncMode` type in `App.tsx`
2. Add configuration in `SYNC_MODE_CONFIG` in `Transformation.tsx`
3. Update the mode selection UI
4. Implement backend logic

### Mock Data

Mock data for development is in each component:
- `TableBrowser.tsx`: `generateMockTables()`
- `DataPreview.tsx`: `generateMockData()`

Replace these with actual API calls for production.

## Deployment to Databricks Apps

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Configure environment variables** in Databricks:
   - `AIRTABLE_API_KEY`
   - `DATABRICKS_WORKSPACE_URL`
   - `DATABRICKS_TOKEN`

3. **Deploy static files** to Databricks Apps hosting

4. **Set up backend API** endpoints for:
   - Authentication
   - Airtable connectivity
   - Databricks job triggering
   - Sync status monitoring

## Security Considerations

- Never commit API keys or tokens
- Use environment variables for sensitive data
- Implement proper authentication and authorization
- Validate all user inputs
- Use HTTPS for all API communications
- Implement rate limiting for sync operations

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

MIT

## Contributing

This project is part of the Lakeflow Community Connectors initiative. Contributions are welcome!

## Support

For issues and questions:
- GitHub Issues: [lakeflow-community-connectors](https://github.com/yyoli-db/lakeflow-community-connectors/issues)
- Databricks Community Forums

## Acknowledgments

- Built for Databricks Apps
- Based on Lakeflow Community Connectors template
- Designed to follow Databricks UI patterns and conventions
