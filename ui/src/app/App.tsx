import { useState } from 'react';
import { SourceConfiguration } from './components/SourceConfiguration';
import { TargetConfiguration } from './components/TargetConfiguration';
import { TableBrowser } from './components/TableBrowser';
import { Transformation } from './components/Transformation';
import { DataPreview } from './components/DataPreview';
import { SyncConfiguration } from './components/SyncConfiguration';
import { Database, Table, Eye, ArrowRight, Workflow, Settings, Check } from 'lucide-react';

type TabType = 'source' | 'target' | 'tables' | 'preview' | 'transformation' | 'sync';
type SyncStatus = 'idle' | 'syncing' | 'success' | 'error';
type SyncMode = 'full' | 'cdc' | 'rule';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('source');
  const [isConnected, setIsConnected] = useState(false);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState<SyncStatus>('idle');
  
  // Transformation state
  const [syncMode, setSyncMode] = useState<SyncMode>('full');
  const [customQuery, setCustomQuery] = useState('');
  const [cdcTimestampField, setCdcTimestampField] = useState('Last Modified Time (Auto)');
  const [cdcLookbackWindow, setCdcLookbackWindow] = useState('24 hours');

  const handleSync = () => {
    setIsSyncing(true);
    setSyncStatus('syncing');
    
    setTimeout(() => {
      setIsSyncing(false);
      setSyncStatus('success');
      
      setTimeout(() => {
        setSyncStatus('idle');
      }, 3000);
    }, 2000);
  };

  const getFlowNodeClass = (condition: boolean, activeCondition: boolean) => {
    if (condition) return 'bg-gradient-to-br from-blue-500 to-cyan-600';
    if (activeCondition) return 'bg-gradient-to-br from-blue-400/50 to-cyan-500/50 ring-2 ring-blue-400';
    return 'bg-slate-700';
  };

  const getArrowClass = (status: SyncStatus, isConnected: boolean) => {
    if (status === 'syncing') return 'bg-orange-500 animate-pulse';
    if (status === 'success') return 'bg-green-500';
    if (isConnected) return 'bg-slate-600';
    return 'bg-slate-700';
  };

  const getArrowLabel = (status: SyncStatus, isConnected: boolean) => {
    if (status === 'syncing') return 'Syncing...';
    if (status === 'success') return 'Synced';
    if (isConnected) return 'Ready';
    return 'Not configured';
  };

  // Get record count for selected table
  const getRecordCount = () => {
    if (!selectedTable) return 0;
    const mockCounts: Record<string, number> = {
      'Contacts': 5,
      'Projects': 4,
      'Tasks': 5,
      'Companies': 4,
      'Products': 4
    };
    return mockCounts[selectedTable] || 0;
  };

  return (
    <div className="h-screen flex flex-col bg-slate-50">
      {/* Top Navigation Bar */}
      <header className="h-14 bg-white border-b border-slate-200 flex items-center px-6">
        <div className="flex items-center gap-3">
          <div className="p-1.5 bg-gradient-to-br from-orange-500 to-red-600 rounded">
            <Database className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-slate-900">Airtable Connector</h1>
            <p className="text-xs text-slate-500">Lakeflow Community Connector</p>
          </div>
        </div>
        
        {isConnected && (
          <div className="ml-auto flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-md">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm text-green-700">Source Connected</span>
          </div>
        )}
      </header>

      {/* Visual Flow Section - Top */}
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 p-8 border-b border-slate-700">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center justify-center gap-8">
            {/* Source - Airtable */}
            <div className="flex flex-col items-center">
              <div className={`w-24 h-24 rounded-2xl flex items-center justify-center mb-3 shadow-lg transition-all ${
                getFlowNodeClass(isConnected, activeTab === 'source')
              }`}>
                <Database className="w-12 h-12 text-white" />
              </div>
              <h3 className="text-white mb-1">Source</h3>
              <p className="text-sm text-slate-300">Airtable</p>
              <p className="text-xs text-slate-400 mt-1">
                {selectedTable || (isConnected ? 'Connected' : 'Not configured')}
              </p>
            </div>

            {/* Arrow */}
            <div className="flex flex-col items-center">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-3 transition-all ${
                getArrowClass(syncStatus, isConnected)
              }`}>
                <ArrowRight className="w-8 h-8 text-white" />
              </div>
              <p className="text-xs text-slate-400">
                {getArrowLabel(syncStatus, isConnected)}
              </p>
            </div>

            {/* Transformation */}
            <div className="flex flex-col items-center">
              <div className={`w-24 h-24 rounded-2xl flex items-center justify-center mb-3 shadow-lg transition-all ${
                isConnected ? 'bg-gradient-to-br from-purple-500 to-pink-600' : 'bg-slate-700'
              }`}>
                <Workflow className="w-12 h-12 text-white" />
              </div>
              <h3 className="text-white mb-1">Transform</h3>
              <p className="text-sm text-slate-300">Lakeflow</p>
              <p className="text-xs text-slate-400 mt-1">ETL Pipeline</p>
            </div>

            {/* Arrow */}
            <div className="flex flex-col items-center">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-3 transition-all ${
                syncStatus === 'success' ? 'bg-green-500' : isConnected ? 'bg-slate-600' : 'bg-slate-700'
              }`}>
                <ArrowRight className="w-8 h-8 text-white" />
              </div>
              <p className="text-xs text-slate-400">
                {syncStatus === 'success' ? 'Completed' : isConnected ? 'Pending' : 'Not configured'}
              </p>
            </div>

            {/* Target - Databricks */}
            <div className="flex flex-col items-center">
              <div className={`w-24 h-24 rounded-2xl flex items-center justify-center mb-3 shadow-lg transition-all ${
                isConnected 
                  ? 'bg-gradient-to-br from-orange-500 to-red-600' 
                  : activeTab === 'target'
                  ? 'bg-gradient-to-br from-orange-400/50 to-red-500/50 ring-2 ring-orange-400'
                  : 'bg-slate-700'
              }`}>
                <Database className="w-12 h-12 text-white" />
              </div>
              <h3 className="text-white mb-1">Target</h3>
              <p className="text-sm text-slate-300">Databricks</p>
              <p className="text-xs text-slate-400 mt-1">
                {selectedTable ? `lakeflow.${selectedTable.toLowerCase()}` : 'Not configured'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Section - Tabs and Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Tab Navigation */}
        <div className="bg-white border-b border-slate-200">
          <nav className="flex items-center gap-1 px-6">
            <button
              onClick={() => setActiveTab('source')}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                activeTab === 'source'
                  ? 'border-blue-500 text-blue-700'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Database className="w-4 h-4" />
              Source Configuration
            </button>
            
            <button
              onClick={() => setActiveTab('target')}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                activeTab === 'target'
                  ? 'border-orange-500 text-orange-700'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Database className="w-4 h-4" />
              Target Configuration
            </button>
            
            <button
              onClick={() => setActiveTab('tables')}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                activeTab === 'tables'
                  ? 'border-purple-500 text-purple-700'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Table className="w-4 h-4" />
              Browse Tables
            </button>

            <button
              onClick={() => setActiveTab('preview')}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                activeTab === 'preview'
                  ? 'border-green-500 text-green-700'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Eye className="w-4 h-4" />
              Data Preview
            </button>

            <button
              onClick={() => setActiveTab('transformation')}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                activeTab === 'transformation'
                  ? 'border-pink-500 text-pink-700'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Workflow className="w-4 h-4" />
              Transformation
            </button>
            
            <button
              onClick={() => setActiveTab('sync')}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                activeTab === 'sync'
                  ? 'border-teal-500 text-teal-700'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Settings className="w-4 h-4" />
              Sync Configuration
            </button>
          </nav>
        </div>

        {/* Content Area */}
        <main className="flex-1 overflow-auto">
          {activeTab === 'source' && (
            <SourceConfiguration 
              onConnect={setIsConnected} 
              isConnected={isConnected}
            />
          )}
          {activeTab === 'target' && (
            <TargetConfiguration 
              isSourceConnected={isConnected}
            />
          )}
          {activeTab === 'tables' && (
            <TableBrowser 
              isConnected={isConnected}
              onSelectTable={(table) => {
                setSelectedTable(table);
                setActiveTab('preview');
              }}
            />
          )}
          {activeTab === 'preview' && (
            <DataPreview 
              selectedTable={selectedTable}
              isSourceConnected={isConnected}
            />
          )}
          {activeTab === 'transformation' && (
            <Transformation 
              isSourceConnected={isConnected}
              selectedTable={selectedTable}
              syncMode={syncMode}
              setSyncMode={setSyncMode}
              customQuery={customQuery}
              setCustomQuery={setCustomQuery}
              cdcTimestampField={cdcTimestampField}
              setCdcTimestampField={setCdcTimestampField}
              cdcLookbackWindow={cdcLookbackWindow}
              setCdcLookbackWindow={setCdcLookbackWindow}
            />
          )}
          {activeTab === 'sync' && (
            <SyncConfiguration 
              selectedTable={selectedTable}
              syncStatus={syncStatus}
              onSync={handleSync}
              isSyncing={isSyncing}
              syncMode={syncMode}
              customQuery={customQuery}
              cdcTimestampField={cdcTimestampField}
              cdcLookbackWindow={cdcLookbackWindow}
              isSourceConnected={isConnected}
              recordCount={getRecordCount()}
            />
          )}
        </main>
      </div>
    </div>
  );
}
