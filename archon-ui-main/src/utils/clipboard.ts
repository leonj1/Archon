import { useState, useCallback, useEffect, useRef } from 'react';

/**
 * Centralized clipboard utilities with fallback methods
 * Provides consistent clipboard handling across the application
 */

export interface ClipboardOptions {
  onSuccess?: (text: string) => void;
  onError?: (error: Error) => void;
  fallback?: boolean;
}

/**
 * Copy text to clipboard with modern API and fallback support
 * Uses Clipboard API first, then falls back to legacy methods
 */
export async function copyToClipboard(text: string, options: ClipboardOptions = {}): Promise<boolean> {
  const { onSuccess, onError, fallback = true } = options;

  try {
    // Try modern Clipboard API first
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      onSuccess?.(text);
      return true;
    }
    
    // Fallback to legacy method if modern API is unavailable
    if (fallback) {
      return copyToClipboardLegacy(text, options);
    }
    
    throw new Error('Clipboard API not available and fallback disabled');
  } catch (error) {
    const clipboardError = error instanceof Error ? error : new Error('Failed to copy to clipboard');
    onError?.(clipboardError);
    
    // Try fallback method if not explicitly disabled
    if (fallback) {
      return copyToClipboardLegacy(text, options);
    }
    
    return false;
  }
}

/**
 * Legacy clipboard copy method using execCommand
 * Used as fallback when Clipboard API is unavailable
 */
function copyToClipboardLegacy(text: string, options: ClipboardOptions = {}): boolean {
  const { onSuccess, onError } = options;
  
  try {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    
    // Make the textarea invisible but accessible
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    textArea.setAttribute('readonly', '');
    textArea.setAttribute('aria-hidden', 'true');
    
    document.body.appendChild(textArea);
    
    // Select and copy the text
    textArea.focus();
    textArea.select();
    
    const successful = document.execCommand('copy');
    document.body.removeChild(textArea);
    
    if (successful) {
      onSuccess?.(text);
      return true;
    } else {
      throw new Error('execCommand failed');
    }
  } catch (error) {
    const clipboardError = error instanceof Error ? error : new Error('Legacy clipboard copy failed');
    onError?.(clipboardError);
    return false;
  }
}

/**
 * Check if clipboard functionality is available
 */
export function isClipboardSupported(): boolean {
  return !!(
    (navigator.clipboard && window.isSecureContext) ||
    document.execCommand
  );
}

/**
 * Read text from clipboard (modern API only)
 * Note: This requires user permission and secure context
 */
export async function readFromClipboard(): Promise<string | null> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      return await navigator.clipboard.readText();
    }
    return null;
  } catch (error) {
    console.warn('Failed to read from clipboard:', error);
    return null;
  }
}

/**
 * React hook for clipboard operations with state management
 */
export function useClipboard(timeout: number = 2000) {
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const copy = useCallback(async (text: string): Promise<boolean> => {
    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    setError(null);
    
    const success = await copyToClipboard(text, {
      onError: (err) => setError(err.message)
    });
    
    if (success) {
      setCopied(true);
      timeoutRef.current = setTimeout(() => {
        setCopied(false);
      }, timeout);
    }
    
    return success;
  }, [timeout]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const reset = useCallback(() => {
    setCopied(false);
    setError(null);
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  return {
    copied,
    error,
    copy,
    reset,
    isSupported: isClipboardSupported()
  };
}

