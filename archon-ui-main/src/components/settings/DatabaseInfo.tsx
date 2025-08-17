import { useState, useEffect } from 'react';
import { Database, Server, CheckCircle, XCircle, AlertCircle, Loader } from 'lucide-react';
import { motion } from 'framer-motion';

interface DatabaseConfig {
  type: string;
  backend: string;
  configured: boolean;
  status?: string;
  error_message?: string;
  host?: string;
  port?: number;
  database?: string;
  user?: string;
  url?: string;
  project_id?: string;
  features?: {
    vector_search?: string;
    json_support?: boolean;
    transactions?: boolean;
    connection_pooling?: boolean;
    row_level_security?: boolean;
    realtime?: boolean;
  };
}

export const DatabaseInfo = () => {
  const [dbInfo, setDbInfo] = useState<DatabaseConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDatabaseInfo();
  }, []);

  const fetchDatabaseInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/database/info');
      if (!response.ok) {
        throw new Error('Failed to fetch database info');
      }
      const data = await response.json();
      setDbInfo(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load database information');
      console.error('Error fetching database info:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = () => {
    if (loading) {
      return <Loader className="w-5 h-5 animate-spin text-gray-500" />;
    }
    if (!dbInfo || dbInfo.status === 'error') {
      return <XCircle className="w-5 h-5 text-red-500" />;
    }
    if (dbInfo.status === 'connected') {
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    }
    return <AlertCircle className="w-5 h-5 text-yellow-500" />;
  };

  const getStatusText = () => {
    if (loading) return 'Checking...';
    if (!dbInfo) return 'Unknown';
    if (dbInfo.status === 'connected') return 'Connected';
    if (dbInfo.status === 'error') return 'Connection Error';
    return 'Disconnected';
  };

  const getStatusColor = () => {
    if (!dbInfo || dbInfo.status === 'error') return 'text-red-600 dark:text-red-400';
    if (dbInfo.status === 'connected') return 'text-green-600 dark:text-green-400';
    return 'text-yellow-600 dark:text-yellow-400';
  };

  const getDatabaseTypeIcon = () => {
    const iconClass = "w-12 h-12 mb-2";
    if (!dbInfo) return <Database className={iconClass + " text-gray-400"} />;
    
    switch (dbInfo.type) {
      case 'mysql':
        return (
          <div className="flex items-center justify-center w-12 h-12 mb-2 rounded-lg bg-blue-100 dark:bg-blue-900">
            <Database className="w-7 h-7 text-blue-600 dark:text-blue-400" />
          </div>
        );
      case 'postgresql':
        return (
          <div className="flex items-center justify-center w-12 h-12 mb-2 rounded-lg bg-indigo-100 dark:bg-indigo-900">
            <Database className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
          </div>
        );
      case 'supabase':
        return (
          <div className="flex items-center justify-center w-12 h-12 mb-2 rounded-lg bg-emerald-100 dark:bg-emerald-900">
            <Server className="w-7 h-7 text-emerald-600 dark:text-emerald-400" />
          </div>
        );
      default:
        return (
          <div className="flex items-center justify-center w-12 h-12 mb-2 rounded-lg bg-gray-100 dark:bg-gray-800">
            <Database className="w-7 h-7 text-gray-600 dark:text-gray-400" />
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-center py-8">
          <Loader className="animate-spin text-gray-500" size={24} />
        </div>
      </div>
    );
  }

  if (error && !dbInfo) {
    return (
      <div className="space-y-4">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-4"
    >
      {/* Database Type Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-start gap-4">
          {getDatabaseTypeIcon()}
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
              {dbInfo?.backend || 'Unknown Database'}
            </h3>
            <div className="flex items-center gap-2 mb-3">
              {getStatusIcon()}
              <span className={`text-sm font-medium ${getStatusColor()}`}>
                {getStatusText()}
              </span>
            </div>
            
            {/* Connection Details */}
            {dbInfo && (
              <div className="space-y-2 text-sm">
                {dbInfo.type === 'supabase' ? (
                  <>
                    {dbInfo.project_id && (
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500 dark:text-gray-400">Project ID:</span>
                        <span className="text-gray-700 dark:text-gray-300 font-mono">
                          {dbInfo.project_id}
                        </span>
                      </div>
                    )}
                  </>
                ) : (
                  <>
                    {dbInfo.host && (
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500 dark:text-gray-400">Host:</span>
                        <span className="text-gray-700 dark:text-gray-300 font-mono">
                          {dbInfo.host}:{dbInfo.port}
                        </span>
                      </div>
                    )}
                    {dbInfo.database && (
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500 dark:text-gray-400">Database:</span>
                        <span className="text-gray-700 dark:text-gray-300 font-mono">
                          {dbInfo.database}
                        </span>
                      </div>
                    )}
                    {dbInfo.user && (
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500 dark:text-gray-400">User:</span>
                        <span className="text-gray-700 dark:text-gray-300 font-mono">
                          {dbInfo.user}
                        </span>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Features Card */}
      {dbInfo?.features && (
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Database Features
          </h4>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {dbInfo.features.vector_search && (
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span className="text-gray-600 dark:text-gray-400">
                  Vector Search: <span className="font-medium">{dbInfo.features.vector_search}</span>
                </span>
              </div>
            )}
            {dbInfo.features.json_support && (
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span className="text-gray-600 dark:text-gray-400">JSON Support</span>
              </div>
            )}
            {dbInfo.features.transactions && (
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span className="text-gray-600 dark:text-gray-400">Transactions</span>
              </div>
            )}
            {dbInfo.features.connection_pooling && (
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span className="text-gray-600 dark:text-gray-400">Connection Pooling</span>
              </div>
            )}
            {dbInfo.features.row_level_security && (
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span className="text-gray-600 dark:text-gray-400">Row Level Security</span>
              </div>
            )}
            {dbInfo.features.realtime && (
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span className="text-gray-600 dark:text-gray-400">Realtime Updates</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error Message */}
      {dbInfo?.error_message && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-sm text-red-600 dark:text-red-400">
            <strong>Error:</strong> {dbInfo.error_message}
          </p>
        </div>
      )}
    </motion.div>
  );
};