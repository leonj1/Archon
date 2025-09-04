import React, { createContext, useContext, useState, ReactNode } from 'react';

interface SettingsContextType {
  loading: boolean;
  refreshSettings: () => Promise<void>;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

interface SettingsProviderProps {
  children: ReactNode;
}

export const SettingsProvider: React.FC<SettingsProviderProps> = ({ children }) => {
  const [loading, setLoading] = useState(false);

  const refreshSettings = async () => {
    // Placeholder for future settings
    setLoading(true);
    setLoading(false);
  };

  const value: SettingsContextType = {
    loading,
    refreshSettings
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};