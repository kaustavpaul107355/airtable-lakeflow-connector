import { useState } from 'react';
import { Server, Database, ExternalLink, Check, Eye, EyeOff, Folder } from 'lucide-react';

interface TargetConfigurationProps {
  isSourceConnected: boolean;
}

export function TargetConfiguration({ isSourceConnected }: TargetConfigurationProps) {
  const [workspaceUrl, setWorkspaceUrl] = useState('');
  const [accessToken, setAccessToken] = useState('');
  const [catalog, setCatalog] = useState('');
  const [schema, setSchema] = useState('');
  const [showToken, setShowToken] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  const handleConnect = async () => {
    if (!workspaceUrl || !accessToken || !catalog || !schema) return;
    
    setIsConnecting(true);
    // Simulate API connection
    setTimeout(() => {
      setIsConnecting(false);
      setIsConnected(true);
    }, 1500);
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    setWorkspaceUrl('');
    setAccessToken('');
    setCatalog('');
    setSchema('');
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl text-slate-900 mb-2">Target: Databricks Configuration</h2>
        <p className="text-slate-600">
          Configure your Databricks workspace connection to store synchronized data.
        </p>
      </div>

      {!isSourceConnected && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-amber-800">
            Please configure the source connection first before setting up the target.
          </p>
        </div>
      )}

      {/* Connection Form */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 mb-6">
        <div className="space-y-6">
          {/* Workspace URL */}
          <div>
            <label className="block text-sm text-slate-700 mb-2">
              <div className="flex items-center gap-2">
                <Server className="w-4 h-4" />
                Workspace URL
              </div>
            </label>
            <input
              type="text"
              value={workspaceUrl}
              onChange={(e) => setWorkspaceUrl(e.target.value)}
              disabled={isConnected || !isSourceConnected}
              placeholder="https://your-workspace.cloud.databricks.com"
              className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
            />
            <p className="text-xs text-slate-500 mt-2">
              Your Databricks workspace URL (e.g., https://dbc-a1b2c3d4-e5f6.cloud.databricks.com)
            </p>
          </div>

          {/* Access Token */}
          <div>
            <label className="block text-sm text-slate-700 mb-2">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4" />
                Personal Access Token
              </div>
            </label>
            <div className="relative">
              <input
                type={showToken ? 'text' : 'password'}
                value={accessToken}
                onChange={(e) => setAccessToken(e.target.value)}
                disabled={isConnected || !isSourceConnected}
                placeholder="dapi********************************"
                className="w-full px-4 py-2.5 pr-12 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
              />
              <button
                type="button"
                onClick={() => setShowToken(!showToken)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                {showToken ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Generate a token in{' '}
              <a 
                href="https://docs.databricks.com/en/dev-tools/auth/pat.html" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-orange-600 hover:underline inline-flex items-center gap-1"
              >
                User Settings → Access Tokens
                <ExternalLink className="w-3 h-3" />
              </a>
            </p>
          </div>

          {/* Catalog and Schema */}
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-slate-700 mb-2">
                <div className="flex items-center gap-2">
                  <Folder className="w-4 h-4" />
                  Catalog
                </div>
              </label>
              <input
                type="text"
                value={catalog}
                onChange={(e) => setCatalog(e.target.value)}
                disabled={isConnected || !isSourceConnected}
                placeholder="main"
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
              />
              <p className="text-xs text-slate-500 mt-2">
                Unity Catalog name (e.g., "main")
              </p>
            </div>

            <div>
              <label className="block text-sm text-slate-700 mb-2">
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4" />
                  Schema
                </div>
              </label>
              <input
                type="text"
                value={schema}
                onChange={(e) => setSchema(e.target.value)}
                disabled={isConnected || !isSourceConnected}
                placeholder="lakeflow"
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
              />
              <p className="text-xs text-slate-500 mt-2">
                Schema/database name (e.g., "lakeflow")
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-6 pt-6 border-t border-slate-200 flex items-center gap-3">
          {!isConnected ? (
            <>
              <button
                onClick={handleConnect}
                disabled={!workspaceUrl || !accessToken || !catalog || !schema || isConnecting || !isSourceConnected}
                className="px-6 py-2.5 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-lg hover:from-orange-600 hover:to-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
              >
                {isConnecting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Connecting...
                  </>
                ) : (
                  'Test Connection'
                )}
              </button>
              <button
                type="button"
                onClick={() => {
                  setWorkspaceUrl('');
                  setAccessToken('');
                  setCatalog('');
                  setSchema('');
                }}
                disabled={!isSourceConnected}
                className="px-6 py-2.5 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Clear
              </button>
            </>
          ) : (
            <>
              <div className="flex items-center gap-2 px-4 py-2.5 bg-green-50 border border-green-200 rounded-lg text-green-700">
                <Check className="w-4 h-4" />
                Successfully Connected
              </div>
              <button
                onClick={handleDisconnect}
                className="px-6 py-2.5 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
              >
                Disconnect
              </button>
            </>
          )}
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <h3 className="text-sm text-orange-900 mb-2">Unity Catalog Setup</h3>
          <p className="text-xs text-orange-700">
            Ensure you have CREATE TABLE permissions in the specified catalog and schema. Tables will be created as Delta tables in Unity Catalog.
          </p>
        </div>
        
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-sm text-red-900 mb-2">Security Best Practices</h3>
          <p className="text-xs text-red-700">
            Use a service principal or dedicated user account for production deployments. Avoid using personal access tokens for shared applications.
          </p>
        </div>
      </div>
    </div>
  );
}
