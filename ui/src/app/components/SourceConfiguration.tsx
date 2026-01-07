import { useState } from 'react';
import { Key, Database, ExternalLink, Check, Eye, EyeOff } from 'lucide-react';

interface SourceConfigurationProps {
  onConnect: (connected: boolean) => void;
  isConnected: boolean;
}

export function SourceConfiguration({ onConnect, isConnected }: SourceConfigurationProps) {
  const [apiKey, setApiKey] = useState('');
  const [baseId, setBaseId] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const handleConnect = async () => {
    if (!apiKey || !baseId) return;
    
    setIsConnecting(true);
    // Simulate API connection
    setTimeout(() => {
      setIsConnecting(false);
      onConnect(true);
    }, 1500);
  };

  const handleDisconnect = () => {
    onConnect(false);
    setApiKey('');
    setBaseId('');
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl text-slate-900 mb-2">Source: Airtable Configuration</h2>
        <p className="text-slate-600">
          Configure your Airtable connection credentials to access your data.
        </p>
      </div>

      {/* Connection Form */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 mb-6">
        <div className="space-y-6">
          {/* API Key Input */}
          <div>
            <label className="block text-sm text-slate-700 mb-2">
              <div className="flex items-center gap-2">
                <Key className="w-4 h-4" />
                Airtable API Key
              </div>
            </label>
            <div className="relative">
              <input
                type={showApiKey ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                disabled={isConnected}
                placeholder="keyXXXXXXXXXXXXXX"
                className="w-full px-4 py-2.5 pr-12 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
              />
              <button
                type="button"
                onClick={() => setShowApiKey(!showApiKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Find your API key in{' '}
              <a 
                href="https://airtable.com/create/tokens" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-orange-600 hover:underline inline-flex items-center gap-1"
              >
                Airtable Account Settings
                <ExternalLink className="w-3 h-3" />
              </a>
            </p>
          </div>

          {/* Base ID Input */}
          <div>
            <label className="block text-sm text-slate-700 mb-2">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4" />
                Base ID
              </div>
            </label>
            <input
              type="text"
              value={baseId}
              onChange={(e) => setBaseId(e.target.value)}
              disabled={isConnected}
              placeholder="appXXXXXXXXXXXXXX"
              className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
            />
            <p className="text-xs text-slate-500 mt-2">
              Found in your Airtable base URL: airtable.com/<span className="text-orange-600">appXXXXXXXXXXXXXX</span>/...
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-6 pt-6 border-t border-slate-200 flex items-center gap-3">
          {!isConnected ? (
            <>
              <button
                onClick={handleConnect}
                disabled={!apiKey || !baseId || isConnecting}
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
                  setApiKey('');
                  setBaseId('');
                }}
                className="px-6 py-2.5 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
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
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm text-blue-900 mb-2">Getting Your API Key</h3>
          <p className="text-xs text-blue-700">
            Create a personal access token in your Airtable account settings with appropriate scopes (data.records:read, schema.bases:read).
          </p>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h3 className="text-sm text-purple-900 mb-2">Finding Your Base ID</h3>
          <p className="text-xs text-purple-700">
            Open your Airtable base and look at the URL. The Base ID starts with "app" followed by alphanumeric characters.
          </p>
        </div>
      </div>
    </div>
  );
}
