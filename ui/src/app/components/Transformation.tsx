import { useState } from 'react';
import { Workflow, RefreshCw, GitBranch, Filter, Code } from 'lucide-react';

interface TransformationProps {
  isSourceConnected: boolean;
  selectedTable: string | null;
  syncMode: 'full' | 'cdc' | 'rule';
  setSyncMode: (mode: 'full' | 'cdc' | 'rule') => void;
  customQuery: string;
  setCustomQuery: (query: string) => void;
  cdcTimestampField: string;
  setCdcTimestampField: (field: string) => void;
  cdcLookbackWindow: string;
  setCdcLookbackWindow: (window: string) => void;
}

type SyncMode = 'full' | 'cdc' | 'rule';

const SYNC_MODE_CONFIG = {
  full: {
    title: 'Full Table Refresh',
    description: 'Replace all data in the target table with the current snapshot from Airtable. This mode is simple and ensures data consistency but rewrites the entire table each sync.',
    icon: RefreshCw,
    color: 'orange',
    benefits: ['Best for small to medium tables', 'No incremental tracking needed', 'Guaranteed consistency']
  },
  cdc: {
    title: 'Change Data Capture (CDC)',
    description: "Sync only records that have been created or modified since the last sync. Uses Airtable's last modified time field to identify changes efficiently.",
    icon: GitBranch,
    color: 'purple',
    benefits: ['Best for large tables', 'Faster incremental updates', 'Requires modified timestamp field']
  },
  rule: {
    title: 'Rule-Based Capture',
    description: 'Sync only records that match specific filter criteria or custom query logic. Allows for selective data synchronization based on field values or conditions.',
    icon: Filter,
    color: 'blue',
    benefits: ['Best for selective sync', 'Custom filtering logic', 'Reduced data transfer']
  }
} as const;

export function Transformation({ 
  isSourceConnected, 
  selectedTable,
  syncMode,
  setSyncMode,
  customQuery,
  setCustomQuery,
  cdcTimestampField,
  setCdcTimestampField,
  cdcLookbackWindow,
  setCdcLookbackWindow
}: TransformationProps) {
  if (!isSourceConnected) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <Workflow className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-slate-900 mb-2">Source Not Connected</h3>
          <p className="text-slate-600">
            Please configure and connect to your Airtable source before setting up transformations.
          </p>
        </div>
      </div>
    );
  }

  if (!selectedTable) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <Workflow className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-slate-900 mb-2">No Table Selected</h3>
          <p className="text-slate-600">
            Please select a table from the Browse Tables tab to configure transformations.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl text-slate-900 mb-2">Transformation Configuration</h2>
        <p className="text-slate-600">
          Configure how data should be synchronized from {selectedTable} to Databricks.
        </p>
      </div>

      {/* Sync Mode Selection */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 mb-6">
        <h3 className="text-slate-900 mb-4">Sync Mode</h3>
        <p className="text-sm text-slate-600 mb-6">
          Choose how you want to synchronize data from Airtable to Databricks.
        </p>

        <div className="space-y-4">
          {/* Full Refresh */}
          <div
            onClick={() => setSyncMode('full')}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              syncMode === 'full'
                ? 'border-orange-500 bg-orange-50'
                : 'border-slate-200 hover:border-slate-300'
            }`}
          >
            <div className="flex items-start gap-4">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                syncMode === 'full' ? 'bg-orange-500' : 'bg-slate-200'
              }`}>
                <RefreshCw className={`w-5 h-5 ${
                  syncMode === 'full' ? 'text-white' : 'text-slate-600'
                }`} />
              </div>
              <div className="flex-1">
                <h4 className={`mb-1 ${
                  syncMode === 'full' ? 'text-orange-900' : 'text-slate-900'
                }`}>
                  Full Table Refresh
                </h4>
                <p className="text-sm text-slate-600">
                  Replace all data in the target table with the current snapshot from Airtable. 
                  This mode is simple and ensures data consistency but rewrites the entire table each sync.
                </p>
                <div className="mt-2 flex items-center gap-4 text-xs text-slate-500">
                  <span>• Best for small to medium tables</span>
                  <span>• No incremental tracking needed</span>
                  <span>• Guaranteed consistency</span>
                </div>
              </div>
            </div>
          </div>

          {/* Change Data Capture */}
          <div
            onClick={() => setSyncMode('cdc')}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              syncMode === 'cdc'
                ? 'border-purple-500 bg-purple-50'
                : 'border-slate-200 hover:border-slate-300'
            }`}
          >
            <div className="flex items-start gap-4">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                syncMode === 'cdc' ? 'bg-purple-500' : 'bg-slate-200'
              }`}>
                <GitBranch className={`w-5 h-5 ${
                  syncMode === 'cdc' ? 'text-white' : 'text-slate-600'
                }`} />
              </div>
              <div className="flex-1">
                <h4 className={`mb-1 ${
                  syncMode === 'cdc' ? 'text-purple-900' : 'text-slate-900'
                }`}>
                  Change Data Capture (CDC)
                </h4>
                <p className="text-sm text-slate-600">
                  Sync only records that have been created or modified since the last sync. 
                  Uses Airtable's last modified time field to identify changes efficiently.
                </p>
                <div className="mt-2 flex items-center gap-4 text-xs text-slate-500">
                  <span>• Best for large tables</span>
                  <span>• Faster incremental updates</span>
                  <span>• Requires modified timestamp field</span>
                </div>
              </div>
            </div>
          </div>

          {/* Rule-Based Capture */}
          <div
            onClick={() => setSyncMode('rule')}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              syncMode === 'rule'
                ? 'border-blue-500 bg-blue-50'
                : 'border-slate-200 hover:border-slate-300'
            }`}
          >
            <div className="flex items-start gap-4">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                syncMode === 'rule' ? 'bg-blue-500' : 'bg-slate-200'
              }`}>
                <Filter className={`w-5 h-5 ${
                  syncMode === 'rule' ? 'text-white' : 'text-slate-600'
                }`} />
              </div>
              <div className="flex-1">
                <h4 className={`mb-1 ${
                  syncMode === 'rule' ? 'text-blue-900' : 'text-slate-900'
                }`}>
                  Rule-Based Capture
                </h4>
                <p className="text-sm text-slate-600">
                  Sync only records that match specific filter criteria or custom query logic. 
                  Allows for selective data synchronization based on field values or conditions.
                </p>
                <div className="mt-2 flex items-center gap-4 text-xs text-slate-500">
                  <span>• Best for selective sync</span>
                  <span>• Custom filtering logic</span>
                  <span>• Reduced data transfer</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CDC Configuration */}
      {syncMode === 'cdc' && (
        <div className="bg-white rounded-lg border border-slate-200 p-6 mb-6">
          <h3 className="text-slate-900 mb-4">CDC Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-700 mb-2">
                Modified Timestamp Field
              </label>
              <select
                value={cdcTimestampField}
                onChange={(e) => setCdcTimestampField(e.target.value)}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option>Last Modified Time (Auto)</option>
                <option>Created Time</option>
                <option>Custom Field...</option>
              </select>
              <p className="text-xs text-slate-500 mt-2">
                Select the field that tracks when records were last modified.
              </p>
            </div>

            <div>
              <label className="block text-sm text-slate-700 mb-2">
                Lookback Window
              </label>
              <select
                value={cdcLookbackWindow}
                onChange={(e) => setCdcLookbackWindow(e.target.value)}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option>1 hour</option>
                <option>6 hours</option>
                <option>24 hours</option>
                <option>7 days</option>
                <option>Custom...</option>
              </select>
              <p className="text-xs text-slate-500 mt-2">
                How far back to check for changes on the first sync.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Rule-Based Configuration */}
      {syncMode === 'rule' && (
        <div className="bg-white rounded-lg border border-slate-200 p-6 mb-6">
          <h3 className="text-slate-900 mb-4">Filter Rules</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-700 mb-2">
                <div className="flex items-center gap-2">
                  <Code className="w-4 h-4" />
                  Filter Formula (Airtable Formula Syntax)
                </div>
              </label>
              <textarea
                value={customQuery}
                onChange={(e) => setCustomQuery(e.target.value)}
                placeholder="Example: {Status} = 'Active'"
                rows={4}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              />
              <p className="text-xs text-slate-500 mt-2">
                Use Airtable formula syntax to filter records. Leave empty to sync all records.
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm text-blue-900 mb-2">Formula Examples:</h4>
              <ul className="text-xs text-blue-700 space-y-1 font-mono">
                <li>• {`{Status} = 'Active'`}</li>
                <li>• {`AND({Priority} = 'High', {Assigned} != '')`}</li>
                <li>• {`CREATED_TIME() > '2024-01-01'`}</li>
                <li>• {`OR({Region} = 'US', {Region} = 'EU')`}</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Additional Options */}
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <h3 className="text-slate-900 mb-4">Additional Options</h3>
        <div className="space-y-4">
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              className="w-4 h-4 text-orange-600 border-slate-300 rounded focus:ring-orange-500"
            />
            <div>
              <p className="text-sm text-slate-900">Enable automatic schema evolution</p>
              <p className="text-xs text-slate-500">
                Automatically add new columns when detected in the source
              </p>
            </div>
          </label>

          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              defaultChecked
              className="w-4 h-4 text-orange-600 border-slate-300 rounded focus:ring-orange-500"
            />
            <div>
              <p className="text-sm text-slate-900">Preserve deleted records</p>
              <p className="text-xs text-slate-500">
                Soft delete records instead of hard deleting from target
              </p>
            </div>
          </label>

          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              className="w-4 h-4 text-orange-600 border-slate-300 rounded focus:ring-orange-500"
            />
            <div>
              <p className="text-sm text-slate-900">Include attachment URLs</p>
              <p className="text-xs text-slate-500">
                Sync attachment field URLs (attachments themselves are not downloaded)
              </p>
            </div>
          </label>
        </div>
      </div>
    </div>
  );
}