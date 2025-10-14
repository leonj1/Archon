import { expect, afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'

// Set required environment variables for tests
process.env.ARCHON_SERVER_PORT = '8181'

// Mock import.meta.env for tests
Object.defineProperty(import.meta, 'env', {
  value: {
    DEV: true,
    PROD: false,
    VITE_HOST: 'localhost',
    VITE_PORT: '8181',
    VITE_ALLOWED_HOSTS: '',
  },
  configurable: true,
})

// Clean up after each test
afterEach(() => {
  cleanup()
})

// Simple mocks only - fetch
// Don't mock fetch for integration tests (they need real HTTP requests)
const isIntegrationTest = process.env.INTEGRATION_TEST === 'true';
if (!isIntegrationTest) {
  global.fetch = vi.fn((url: string | URL, options?: RequestInit) => {
    const urlString = typeof url === 'string' ? url : url.toString();
    const method = options?.method?.toUpperCase() || 'GET';

    // Return appropriate default responses based on endpoint and method
    let jsonResponse: any = {};

    if (urlString.includes('/progress/active') || urlString.endsWith('/progress/')) {
      // Active operations list endpoint
      jsonResponse = { operations: [], count: 0, timestamp: new Date().toISOString() };
    } else if (urlString.includes('/progress/') && urlString.split('/progress/')[1]) {
      // Single progress endpoint (e.g., /progress/{id})
      const progressId = urlString.split('/progress/')[1].replace(/[/?].*$/, '');
      if (progressId === 'mock-progress-id') {
        // Return progress data for the mock crawl
        jsonResponse = {
          progressId: 'mock-progress-id',
          status: 'processing',
          progress: 50,
          type: 'crawl',
          message: 'Processing...',
        };
      } else if (progressId && progressId !== 'active') {
        // Return 404 for non-existent progress IDs in tests
        return Promise.resolve({
          ok: false,
          status: 404,
          json: () => Promise.resolve({ detail: 'Progress not found' }),
          text: () => Promise.resolve(JSON.stringify({ detail: 'Progress not found' })),
          headers: new Headers(),
        } as Response);
      }
    } else if (urlString.includes('/knowledge-items/sources')) {
      jsonResponse = []; // Sources endpoint returns an array
    } else if (urlString.includes('/knowledge-items/summary')) {
      // Extract page and per_page from URL query parameters
      const url = new URL(urlString, 'http://localhost');
      const page = parseInt(url.searchParams.get('page') || '1', 10);
      const per_page = parseInt(url.searchParams.get('per_page') || '10', 10);
      jsonResponse = { items: [], total: 0, page, per_page };
    } else if (method === 'DELETE' && urlString.includes('/knowledge-items/')) {
      // DELETE operations return success with message
      jsonResponse = { success: true, message: 'Successfully deleted knowledge item' };
    } else if (method === 'POST' && urlString.includes('/knowledge-items/crawl')) {
      // Validate URL format like the backend does
      const body = options?.body ? JSON.parse(options.body as string) : {};
      const requestUrl = body.url || '';

      if (!requestUrl.startsWith('http://') && !requestUrl.startsWith('https://')) {
        // Simulate backend validation error
        return Promise.resolve({
          ok: false,
          status: 422,
          json: () => Promise.resolve({
            detail: 'URL must start with http:// or https://'
          }),
          text: () => Promise.resolve(JSON.stringify({
            detail: 'URL must start with http:// or https://'
          })),
          headers: new Headers(),
        } as Response);
      }

      // Valid crawl request
      jsonResponse = {
        success: true,
        progressId: 'mock-progress-id',
        message: 'Crawling started',
        estimatedDuration: '3-5 minutes'
      };
    }

    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve(jsonResponse),
      text: () => Promise.resolve(''),
      status: 200,
      headers: new Headers(),
    } as Response);
  }) as any;
}

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(() => null),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

// Mock DOM methods that might not exist in test environment
Element.prototype.scrollIntoView = vi.fn()
window.HTMLElement.prototype.scrollIntoView = vi.fn()

// Mock lucide-react icons - simple implementation
vi.mock('lucide-react', () => ({
  Trash2: () => 'Trash2',
  X: () => 'X',
  AlertCircle: () => 'AlertCircle',
  Loader2: () => 'Loader2',
  BookOpen: () => 'BookOpen',
  Settings: () => 'Settings',
  WifiOff: () => 'WifiOff',
  ChevronDown: () => 'ChevronDown',
  ChevronRight: () => 'ChevronRight',
  Plus: () => 'Plus',
  Search: () => 'Search',
  Activity: () => 'Activity',
  CheckCircle2: () => 'CheckCircle2',
  ListTodo: () => 'ListTodo',
  MoreHorizontal: () => 'MoreHorizontal',
  Pin: () => 'Pin',
  PinOff: () => 'PinOff',
  Clipboard: () => 'Clipboard',
  // Add more icons as needed
}))

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))