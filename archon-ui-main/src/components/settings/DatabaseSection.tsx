import { useState, useEffect } from 'react';
import { Database, RefreshCw, CheckCircle, XCircle, Loader } from 'lucide-react';
import { credentialsService, DatabaseInfo } from '../../services/credentialsService';

export const DatabaseSection = () => {
  const [databaseInfo, setDatabaseInfo] = useState<DatabaseInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDatabaseInfo();
  }, []);

  const fetchDatabaseInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      const info = await credentialsService.getDatabaseInfo();
      setDatabaseInfo(info);
    } catch (err) {
      setError('Failed to fetch database information');
      console.error('Error fetching database info:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-6">
        <Loader className="w-5 h-5 animate-spin text-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
        <p className="text-red-600 dark:text-red-400">{error}</p>
        <button
          onClick={fetchDatabaseInfo}
          className="mt-2 text-sm text-red-600 dark:text-red-400 hover:underline"
        >
          Try again
        </button>
      </div>
    );
  }

  if (!databaseInfo) {
    return null;
  }

  const getDatabaseIcon = () => {
    switch (databaseInfo.type) {
      case 'sqlite':
        return (
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30">
            <Database className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
        );
      case 'supabase':
        return (
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-900/30">
            <Database className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          </div>
        );
      default:
        return (
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-900/30">
            <Database className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </div>
        );
    }
  };

  const getStatusIndicator = () => {
    if (databaseInfo.type === 'sqlite') {
      return databaseInfo.exists ? (
        <div className="flex items-center gap-1.5">
          <CheckCircle className="w-4 h-4 text-green-500" />
          <span className="text-sm text-green-600 dark:text-green-400">Connected</span>
        </div>
      ) : (
        <div className="flex items-center gap-1.5">
          <XCircle className="w-4 h-4 text-red-500" />
          <span className="text-sm text-red-600 dark:text-red-400">Not Found</span>
        </div>
      );
    }
    
    // For Supabase, assume connected if we have a URL
    return databaseInfo.path && databaseInfo.path !== 'Not configured' ? (
      <div className="flex items-center gap-1.5">
        <CheckCircle className="w-4 h-4 text-green-500" />
        <span className="text-sm text-green-600 dark:text-green-400">Connected</span>
      </div>
    ) : (
      <div className="flex items-center gap-1.5">
        <XCircle className="w-4 h-4 text-yellow-500" />
        <span className="text-sm text-yellow-600 dark:text-yellow-400">Not Configured</span>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Database Type and Status */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          {getDatabaseIcon()}
          <div>
            <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
              {databaseInfo.display_type}
            </h3>
            <p className="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
              {databaseInfo.description}
            </p>
          </div>
        </div>
        {getStatusIndicator()}
      </div>

      {/* Database Details */}
      <div className="space-y-3 pt-3 border-t border-gray-200 dark:border-gray-700">
        {/* Database Path */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Database Path
          </label>
          <div className="flex items-center gap-2">
            <code className="flex-1 px-3 py-2 text-xs bg-gray-100 dark:bg-gray-800 rounded-lg text-gray-700 dark:text-gray-300 font-mono break-all">
              {databaseInfo.path}
            </code>
          </div>
        </div>

        {/* Additional Info */}
        <div className="grid grid-cols-2 gap-4">
          {/* Database Size (for SQLite) */}
          {databaseInfo.size_mb !== undefined && (
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                Database Size
              </label>
              <div className="text-sm text-gray-900 dark:text-gray-100">
                {databaseInfo.size_mb} MB
              </div>
            </div>
          )}

          {/* Type Label */}
          <div>
            <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
              Backend Type
            </label>
            <div className="text-sm text-gray-900 dark:text-gray-100">
              {databaseInfo.type.toUpperCase()}
            </div>
          </div>
        </div>

        {/* Full URL for Supabase (if available) */}
        {databaseInfo.full_url && (
          <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
            <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
              Full Connection URL
            </label>
            <code className="block px-3 py-2 text-xs bg-gray-100 dark:bg-gray-800 rounded-lg text-gray-700 dark:text-gray-300 font-mono break-all">
              {databaseInfo.full_url}
            </code>
          </div>
        )}
      </div>

      {/* Refresh Button */}
      <div className="flex justify-end pt-3 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={fetchDatabaseInfo}
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>
    </div>
  );
};
