import { useState } from 'react';
import { Play, Check, RefreshCw, GitBranch, Filter, Code, Clock, Calendar, AlertCircle } from 'lucide-react';

interface SyncConfigurationProps {
  selectedTable: string | null;
  syncStatus: 'idle' | 'syncing' | 'success' | 'error';
  onSync: () => void;
  isSyncing: boolean;
  syncMode: 'full' | 'cdc' | 'rule';
  customQuery: string;
  cdcTimestampField: string;
  cdcLookbackWindow: string;
  isSourceConnected: boolean;
  recordCount: number;
}

export function SyncConfiguration({
  selectedTable,
  syncStatus,
  onSync,
  isSyncing,
  syncMode,
  customQuery,
  cdcTimestampField,
  cdcLookbackWindow,
  isSourceConnected,
  recordCount,
}: SyncConfigurationProps) {
  const [schedule, setSchedule] = useState('manual');
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);

  // Get sync mode details
  const getSyncModeInfo = () => {
    switch (syncMode) {
      case 'full':
        return {
          label: 'Full Table Refresh',
          description: 'All records will be synchronized',
          icon: RefreshCw,
          color: 'orange',
          recordsToSync: recordCount,
        };
      case 'cdc':
        return {
          label: 'Change Data Capture (CDC)',
          description: `Tracking changes via ${cdcTimestampField}`,
          icon: GitBranch,
          color: 'purple',
          recordsToSync: Math.ceil(recordCount * 0.3), // ~30% changed
        };
      case 'rule':
        return {
          label: 'Rule-Based Capture',
          description: customQuery || 'No filter applied - all records will sync',
          icon: Filter,
          color: 'blue',
          recordsToSync: customQuery ? Math.ceil(recordCount * 0.6) : recordCount,
        };
      default:
        return {
          label: 'Full Table Refresh',
          description: 'All records will be synchronized',
          icon: RefreshCw,
          color: 'orange',
          recordsToSync: recordCount,
        };
    }
  };

  const syncModeInfo = getSyncModeInfo();
  const SyncIcon = syncModeInfo.icon;

  const handleSyncClick = () => {
    onSync();
    setLastSyncTime(new Date());
  };

  if (!selectedTable) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-slate-900 mb-2">No Table Selected</h3>
          <p className="text-slate-600">
            Please select a table from the Browse Tables tab to configure sync settings.
          </p>
        </div>
      </div>
    );
  }

  if (!isSourceConnected) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-slate-900 mb-2">Source Not Connected</h3>
          <p className="text-slate-600">
            Please configure and connect to your Airtable source before setting up sync.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl text-slate-900 mb-2">Sync Configuration</h2>
        <p className="text-slate-600">
          Configure and execute data synchronization from Airtable to Databricks.
        </p>
      </div>

      {/* Current Transformation Mode */}
      <div
        className={`mb-6 border-l-4 rounded-lg p-5 ${
          syncModeInfo.color === 'orange'
            ? 'bg-orange-50 border-orange-500'
            : syncModeInfo.color === 'purple'
            ? 'bg-purple-50 border-purple-500'
            : 'bg-blue-50 border-blue-500'
        }`}
      >
        <div className="flex items-start gap-4">
          <div
            className={`w-12 h-12 rounded-lg flex items-center justify-center ${
              syncModeInfo.color === 'orange'
                ? 'bg-orange-500'
                : syncModeInfo.color === 'purple'
                ? 'bg-purple-500'
                : 'bg-blue-500'
            }`}
          >
            <SyncIcon className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <h3
                className={`text-lg ${
                  syncModeInfo.color === 'orange'
                    ? 'text-orange-900'
                    : syncModeInfo.color === 'purple'
                    ? 'text-purple-900'
                    : 'text-blue-900'
                }`}
              >
                {syncModeInfo.label}
              </h3>
              <div
                className={`px-4 py-1.5 rounded-full text-sm ${
                  syncModeInfo.color === 'orange'
                    ? 'bg-orange-100 text-orange-800'
                    : syncModeInfo.color === 'purple'
                    ? 'bg-purple-100 text-purple-800'
                    : 'bg-blue-100 text-blue-800'
                }`}
              >
                {syncModeInfo.recordsToSync} of {recordCount} records will sync
              </div>
            </div>
            <p
              className={`text-sm mb-2 ${
                syncModeInfo.color === 'orange'
                  ? 'text-orange-700'
                  : syncModeInfo.color === 'purple'
                  ? 'text-purple-700'
                  : 'text-blue-700'
              }`}
            >
              {syncModeInfo.description}
            </p>
            {syncMode === 'cdc' && (
              <div className="flex items-center gap-4 text-xs text-slate-600">
                <span>• Lookback window: {cdcLookbackWindow}</span>
                <span>• Timestamp field: {cdcTimestampField}</span>
              </div>
            )}
            {syncMode === 'rule' && customQuery && (
              <div className="mt-3 bg-white/70 border border-slate-200 rounded p-3">
                <div className="flex items-center gap-2 mb-2">
                  <Code className="w-4 h-4 text-slate-500" />
                  <span className="text-xs text-slate-600">Active Filter:</span>
                </div>
                <code className="text-sm text-blue-700 font-mono">{customQuery}</code>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Sync Settings */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 mb-6">
        <h3 className="text-slate-900 mb-4">Sync Settings</h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm text-slate-700 mb-2">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Schedule
              </div>
            </label>
            <select
              value={schedule}
              onChange={(e) => setSchedule(e.target.value)}
              className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="manual">Manual</option>
              <option value="15min">Every 15 minutes</option>
              <option value="hourly">Hourly</option>
              <option value="daily">Daily at 12:00 AM</option>
              <option value="weekly">Weekly on Sunday</option>
            </select>
            <p className="text-xs text-slate-500 mt-2">
              Set how often the sync should run automatically
            </p>
          </div>

          <div>
            <label className="block text-sm text-slate-700 mb-2">
              Target Table Name
            </label>
            <input
              type="text"
              value={`lakeflow.${selectedTable.toLowerCase()}`}
              readOnly
              className="w-full px-4 py-2.5 border border-slate-300 rounded-lg bg-slate-50"
            />
            <p className="text-xs text-slate-500 mt-2">
              Data will be written to this Databricks table
            </p>
          </div>
        </div>

        {/* Additional Options */}
        <div className="mt-6 pt-6 border-t border-slate-200">
          <h4 className="text-sm text-slate-900 mb-3">Additional Options</h4>
          <div className="space-y-3">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                defaultChecked
                className="w-4 h-4 text-orange-600 border-slate-300 rounded focus:ring-orange-500"
              />
              <div>
                <p className="text-sm text-slate-900">Enable error notifications</p>
                <p className="text-xs text-slate-500">
                  Get notified when sync failures occur
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
                <p className="text-sm text-slate-900">Create audit logs</p>
                <p className="text-xs text-slate-500">
                  Track all sync operations and data changes
                </p>
              </div>
            </label>

            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                className="w-4 h-4 text-orange-600 border-slate-300 rounded focus:ring-orange-500"
              />
              <div>
                <p className="text-sm text-slate-900">Enable data validation</p>
                <p className="text-xs text-slate-500">
                  Validate data integrity before writing to target
                </p>
              </div>
            </label>
          </div>
        </div>
      </div>

      {/* Sync Status & Statistics */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 mb-6">
        <h3 className="text-slate-900 mb-4">Sync Status</h3>
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-xs text-blue-700 mb-1">Source Records</p>
            <p className="text-2xl text-blue-900">{recordCount}</p>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <p className="text-xs text-purple-700 mb-1">To Sync</p>
            <p className="text-2xl text-purple-900">{syncModeInfo.recordsToSync}</p>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-xs text-green-700 mb-1">Last Sync</p>
            <p className="text-lg text-green-900">
              {lastSyncTime ? lastSyncTime.toLocaleTimeString() : 'Never'}
            </p>
          </div>
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
            <p className="text-xs text-slate-700 mb-1">Status</p>
            <p className="text-lg text-slate-900">
              {syncStatus === 'syncing' ? 'Syncing...' : syncStatus === 'success' ? 'Success' : 'Idle'}
            </p>
          </div>
        </div>
      </div>

      {/* Sync Actions */}
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg p-8 text-center">
        <h3 className="text-white text-xl mb-2">Ready to Sync</h3>
        <p className="text-slate-300 mb-6">
          {syncModeInfo.recordsToSync} records from {selectedTable} will be synchronized to Databricks
        </p>

        <button
          onClick={handleSyncClick}
          disabled={isSyncing || !isSourceConnected}
          className="inline-flex items-center gap-3 px-10 py-4 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-lg hover:from-orange-600 hover:to-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg text-lg"
        >
          {isSyncing ? (
            <>
              <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Syncing to Databricks...
            </>
          ) : (
            <>
              <Play className="w-6 h-6" />
              Start Sync
            </>
          )}
        </button>

        {syncStatus === 'success' && (
          <div className="mt-6 inline-flex items-center gap-2 px-6 py-3 bg-green-500/20 border border-green-400 rounded-lg text-green-300">
            <Check className="w-5 h-5" />
            Sync completed successfully at {lastSyncTime?.toLocaleTimeString()}
          </div>
        )}

        {schedule !== 'manual' && (
          <p className="mt-6 text-sm text-slate-400">
            <Clock className="w-4 h-4 inline mr-1" />
            Automatic sync scheduled: {schedule === '15min' ? 'Every 15 minutes' : schedule === 'hourly' ? 'Hourly' : schedule === 'daily' ? 'Daily' : 'Weekly'}
          </p>
        )}
      </div>
    </div>
  );
}
