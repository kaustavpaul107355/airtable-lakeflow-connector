import { useState } from 'react';
import { Table, ChevronRight, RefreshCw, Database } from 'lucide-react';

interface TableBrowserProps {
  isConnected: boolean;
  onSelectTable: (tableName: string) => void;
}

// Mock data for Airtable tables
const mockTables = [
  {
    id: 'tbl001',
    name: 'Contacts',
    recordCount: 1247,
    fields: ['Name', 'Email', 'Phone', 'Company', 'Status'],
    lastModified: '2 hours ago'
  },
  {
    id: 'tbl002',
    name: 'Projects',
    recordCount: 89,
    fields: ['Project Name', 'Status', 'Owner', 'Start Date', 'End Date', 'Budget'],
    lastModified: '1 day ago'
  },
  {
    id: 'tbl003',
    name: 'Tasks',
    recordCount: 542,
    fields: ['Task Name', 'Assignee', 'Priority', 'Due Date', 'Status'],
    lastModified: '3 hours ago'
  },
  {
    id: 'tbl004',
    name: 'Companies',
    recordCount: 324,
    fields: ['Company Name', 'Industry', 'Location', 'Size', 'Website'],
    lastModified: '5 hours ago'
  },
  {
    id: 'tbl005',
    name: 'Products',
    recordCount: 156,
    fields: ['Product Name', 'SKU', 'Price', 'Category', 'Stock'],
    lastModified: '12 hours ago'
  }
];

export function TableBrowser({ isConnected, onSelectTable }: TableBrowserProps) {
  const [tables, setTables] = useState(mockTables);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [expandedTable, setExpandedTable] = useState<string | null>(null);

  const handleRefresh = () => {
    setIsRefreshing(true);
    // Simulate API refresh
    setTimeout(() => {
      setIsRefreshing(false);
    }, 1000);
  };

  if (!isConnected) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Database className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-slate-900 mb-2">Not Connected</h3>
          <p className="text-slate-600">
            Please configure your connection in the Configuration tab first.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl text-slate-900 mb-2">Browse Tables</h2>
          <p className="text-slate-600">
            Select a table to preview and sync data
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Tables Grid */}
      <div className="space-y-3">
        {tables.map((table) => (
          <div
            key={table.id}
            className="bg-white border border-slate-200 rounded-lg overflow-hidden hover:border-orange-300 transition-colors"
          >
            <button
              onClick={() => setExpandedTable(expandedTable === table.id ? null : table.id)}
              className="w-full px-6 py-4 flex items-center gap-4 text-left hover:bg-slate-50 transition-colors"
            >
              <div className="p-2 bg-orange-100 rounded-lg">
                <Table className="w-5 h-5 text-orange-600" />
              </div>
              
              <div className="flex-1">
                <h3 className="text-slate-900 mb-1">{table.name}</h3>
                <div className="flex items-center gap-4 text-sm text-slate-500">
                  <span>{table.recordCount.toLocaleString()} records</span>
                  <span>•</span>
                  <span>{table.fields.length} fields</span>
                  <span>•</span>
                  <span>Updated {table.lastModified}</span>
                </div>
              </div>

              <ChevronRight
                className={`w-5 h-5 text-slate-400 transition-transform ${
                  expandedTable === table.id ? 'rotate-90' : ''
                }`}
              />
            </button>

            {/* Expanded Details */}
            {expandedTable === table.id && (
              <div className="border-t border-slate-200 bg-slate-50 px-6 py-4">
                <div className="mb-4">
                  <h4 className="text-sm text-slate-700 mb-2">Fields ({table.fields.length})</h4>
                  <div className="flex flex-wrap gap-2">
                    {table.fields.map((field, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-white border border-slate-200 rounded-md text-sm text-slate-700"
                      >
                        {field}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectTable(table.name);
                    }}
                    className="px-4 py-2 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-lg hover:from-orange-600 hover:to-red-700 transition-all text-sm"
                  >
                    Preview Data
                  </button>
                  <button
                    onClick={(e) => e.stopPropagation()}
                    className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-white transition-colors text-sm"
                  >
                    View Schema
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary Card */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Database className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="text-sm text-blue-900 mb-1">
              Found {tables.length} tables in your Airtable base
            </h3>
            <p className="text-xs text-blue-700">
              Total records: {tables.reduce((sum, t) => sum + t.recordCount, 0).toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
