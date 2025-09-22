import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { CodeDisplay } from '../shared/CodeDisplay';
import { cn, glassmorphism } from '@/features/ui/primitives/styles';
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  X,
  Loader2,
  AlertCircle,
  HelpCircle
} from 'lucide-react';

interface FeedbackPattern {
  id: string;
  name: string;
  description: string;
  usage: string;
  component: React.ComponentType;
}

// Alert Component
const AlertsDemo = () => {
  const alerts = [
    {
      type: 'success',
      icon: <CheckCircle className="w-5 h-5" />,
      title: 'Success',
      message: 'Your project has been created successfully.',
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      borderColor: 'border-green-200 dark:border-green-800',
      textColor: 'text-green-800 dark:text-green-200',
      iconColor: 'text-green-600 dark:text-green-400'
    },
    {
      type: 'error',
      icon: <XCircle className="w-5 h-5" />,
      title: 'Error',
      message: 'There was an error processing your request. Please try again.',
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      borderColor: 'border-red-200 dark:border-red-800',
      textColor: 'text-red-800 dark:text-red-200',
      iconColor: 'text-red-600 dark:text-red-400'
    },
    {
      type: 'warning',
      icon: <AlertTriangle className="w-5 h-5" />,
      title: 'Warning',
      message: 'This action cannot be undone. Please proceed with caution.',
      bgColor: 'bg-orange-50 dark:bg-orange-900/20',
      borderColor: 'border-orange-200 dark:border-orange-800',
      textColor: 'text-orange-800 dark:text-orange-200',
      iconColor: 'text-orange-600 dark:text-orange-400'
    },
    {
      type: 'info',
      icon: <Info className="w-5 h-5" />,
      title: 'Information',
      message: 'New features have been added to your dashboard.',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      borderColor: 'border-blue-200 dark:border-blue-800',
      textColor: 'text-blue-800 dark:text-blue-200',
      iconColor: 'text-blue-600 dark:text-blue-400'
    }
  ];

  return (
    <div className="space-y-4">
      {alerts.map((alert) => (
        <div
          key={alert.type}
          className={cn(
            'p-4 rounded-lg border backdrop-blur-sm',
            alert.bgColor,
            alert.borderColor
          )}
        >
          <div className="flex items-start gap-3">
            <div className={alert.iconColor}>
              {alert.icon}
            </div>
            <div className="flex-1 min-w-0">
              <h4 className={cn('font-medium text-sm', alert.textColor)}>
                {alert.title}
              </h4>
              <p className={cn('text-sm mt-1', alert.textColor)}>
                {alert.message}
              </p>
            </div>
            <Button variant="ghost" size="sm" className={cn('p-1', alert.textColor)}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
};

// Loading States Demo
const LoadingStatesDemo = () => {
  const loadingStates = [
    {
      name: 'Spinner',
      component: (
        <div className="flex items-center justify-center p-8">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
        </div>
      )
    },
    {
      name: 'Spinner with Text',
      component: (
        <div className="flex items-center justify-center gap-3 p-8">
          <Loader2 className="w-5 h-5 animate-spin text-cyan-500" />
          <span className="text-sm text-gray-600 dark:text-gray-400">Loading...</span>
        </div>
      )
    },
    {
      name: 'Progress Bar',
      component: (
        <div className="p-8 space-y-3">
          <div className="flex justify-between text-sm">
            <span>Uploading files...</span>
            <span>67%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div className="bg-cyan-500 h-2 rounded-full transition-all duration-300" style={{ width: '67%' }} />
          </div>
        </div>
      )
    },
    {
      name: 'Skeleton Loading',
      component: (
        <div className="p-8 space-y-4">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-3/4 mb-3" />
            <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-1/2 mb-3" />
            <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-5/6" />
          </div>
        </div>
      )
    },
    {
      name: 'Pulsing Card',
      component: (
        <div className="p-8">
          <Card className="animate-pulse opacity-60">
            <div className="h-20 bg-gray-300 dark:bg-gray-700 rounded" />
          </Card>
        </div>
      )
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {loadingStates.map((state) => (
        <Card key={state.name} className="text-center">
          <h4 className="font-medium text-sm mb-2 p-4 pb-0">{state.name}</h4>
          {state.component}
        </Card>
      ))}
    </div>
  );
};

// Toast Notifications Demo
const ToastDemo = () => {
  const [toasts, setToasts] = useState<Array<{
    id: number;
    type: string;
    title: string;
    message: string;
  }>>([]);

  const addToast = (type: string) => {
    const toastData = {
      success: { title: 'Success!', message: 'Action completed successfully.' },
      error: { title: 'Error!', message: 'Something went wrong.' },
      warning: { title: 'Warning!', message: 'Please review your action.' },
      info: { title: 'Info', message: 'Here\'s some useful information.' }
    };

    const newToast = {
      id: Date.now(),
      type,
      ...toastData[type as keyof typeof toastData]
    };

    setToasts(prev => [...prev, newToast]);

    // Auto-remove after 3 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== newToast.id));
    }, 3000);
  };

  const removeToast = (id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  const getToastStyles = (type: string) => {
    const styles = {
      success: {
        bg: glassmorphism.background.card,
        border: 'border-green-500',
        glow: glassmorphism.shadow.glow.green,
        icon: <CheckCircle className="w-5 h-5 text-green-500" />
      },
      error: {
        bg: glassmorphism.background.card,
        border: 'border-red-500',
        glow: glassmorphism.shadow.glow.red,
        icon: <XCircle className="w-5 h-5 text-red-500" />
      },
      warning: {
        bg: glassmorphism.background.card,
        border: 'border-orange-500',
        glow: glassmorphism.shadow.glow.orange,
        icon: <AlertTriangle className="w-5 h-5 text-orange-500" />
      },
      info: {
        bg: glassmorphism.background.card,
        border: 'border-blue-500',
        glow: glassmorphism.shadow.glow.blue,
        icon: <Info className="w-5 h-5 text-blue-500" />
      }
    };
    return styles[type as keyof typeof styles];
  };

  return (
    <div>
      {/* Controls */}
      <div className="flex gap-2 mb-6">
        <Button onClick={() => addToast('success')} size="sm" variant="outline">
          Success Toast
        </Button>
        <Button onClick={() => addToast('error')} size="sm" variant="outline">
          Error Toast
        </Button>
        <Button onClick={() => addToast('warning')} size="sm" variant="outline">
          Warning Toast
        </Button>
        <Button onClick={() => addToast('info')} size="sm" variant="outline">
          Info Toast
        </Button>
      </div>

      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
        {toasts.map((toast) => {
          const styles = getToastStyles(toast.type);
          return (
            <div
              key={toast.id}
              className={cn(
                'p-4 rounded-lg border backdrop-blur-md animate-in slide-in-from-right',
                styles.bg,
                styles.border,
                styles.glow
              )}
            >
              <div className="flex items-start gap-3">
                {styles.icon}
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm">{toast.title}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {toast.message}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="p-1"
                  onClick={() => removeToast(toast.id)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Static Example */}
      <Card className="p-4">
        <h4 className="font-medium mb-3">Static Toast Example</h4>
        <div
          className={cn(
            'p-4 rounded-lg border backdrop-blur-md max-w-sm',
            glassmorphism.background.card,
            'border-green-500',
            glassmorphism.shadow.glow.green
          )}
        >
          <div className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <div className="flex-1 min-w-0">
              <h4 className="font-medium text-sm">Project Created</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Your new project has been created successfully.
              </p>
            </div>
            <Button variant="ghost" size="sm" className="p-1">
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

// Empty States Demo
const EmptyStatesDemo = () => {
  const emptyStates = [
    {
      name: 'No Data',
      icon: <HelpCircle className="w-12 h-12 mx-auto mb-4 text-gray-400" />,
      title: 'No projects found',
      description: 'Get started by creating your first project.',
      action: <Button size="sm">Create Project</Button>
    },
    {
      name: 'No Search Results',
      icon: <AlertCircle className="w-12 h-12 mx-auto mb-4 text-gray-400" />,
      title: 'No results found',
      description: 'Try adjusting your search criteria or filters.',
      action: <Button size="sm" variant="outline">Clear Filters</Button>
    },
    {
      name: 'Coming Soon',
      icon: <Info className="w-12 h-12 mx-auto mb-4 text-cyan-500" />,
      title: 'Feature coming soon',
      description: 'This feature is currently under development.',
      action: null
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {emptyStates.map((state) => (
        <Card key={state.name} className="text-center p-8">
          <h4 className="font-medium text-xs mb-4 text-gray-500 uppercase">
            {state.name}
          </h4>
          {state.icon}
          <h3 className="font-semibold text-lg mb-2">{state.title}</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {state.description}
          </p>
          {state.action}
        </Card>
      ))}
    </div>
  );
};

const FEEDBACK_PATTERNS: FeedbackPattern[] = [
  {
    id: 'alerts',
    name: 'Alerts & Messages',
    description: 'Contextual feedback messages with different severity levels',
    usage: 'Form validation, system notifications, user feedback',
    component: AlertsDemo
  },
  {
    id: 'loading',
    name: 'Loading States',
    description: 'Visual indicators for loading and processing states',
    usage: 'Data fetching, file uploads, long-running operations',
    component: LoadingStatesDemo
  },
  {
    id: 'toasts',
    name: 'Toast Notifications',
    description: 'Temporary notifications that appear and disappear automatically',
    usage: 'Action confirmations, real-time updates, background processes',
    component: ToastDemo
  },
  {
    id: 'empty',
    name: 'Empty States',
    description: 'Helpful messaging when no content is available',
    usage: 'Empty lists, no search results, feature placeholders',
    component: EmptyStatesDemo
  }
];

const generateCode = (patternId: string) => {
  const codeExamples = {
    alerts: `import { Card } from '@/features/ui/primitives/card';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';

/**
 * 🤖 AI CONTEXT: Alert Pattern
 *
 * PURPOSE: Contextual feedback with appropriate visual treatment
 * WHEN TO USE: Form validation, system notifications, important messages
 * WHEN NOT TO USE: Temporary messages (use toasts), blocking dialogs (use modals)
 *
 * SEVERITY LEVELS:
 * - Success: Green - Positive outcomes, completions
 * - Error: Red - Critical errors, validation failures
 * - Warning: Orange - Cautions, potential issues
 * - Info: Blue - Neutral information, tips
 *
 * ACCESSIBILITY:
 * - Use semantic colors consistently
 * - Include icons for visual clarity
 * - Provide clear, actionable text
 * - Support dismissal with keyboard
 */

interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  onDismiss?: () => void;
}

export const Alert = ({ type, title, message, onDismiss }: AlertProps) => {
  const config = {
    success: {
      icon: <CheckCircle className="w-5 h-5" />,
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      borderColor: 'border-green-200 dark:border-green-800',
      textColor: 'text-green-800 dark:text-green-200',
      iconColor: 'text-green-600 dark:text-green-400'
    },
    error: {
      icon: <XCircle className="w-5 h-5" />,
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      borderColor: 'border-red-200 dark:border-red-800',
      textColor: 'text-red-800 dark:text-red-200',
      iconColor: 'text-red-600 dark:text-red-400'
    },
    warning: {
      icon: <AlertTriangle className="w-5 h-5" />,
      bgColor: 'bg-orange-50 dark:bg-orange-900/20',
      borderColor: 'border-orange-200 dark:border-orange-800',
      textColor: 'text-orange-800 dark:text-orange-200',
      iconColor: 'text-orange-600 dark:text-orange-400'
    },
    info: {
      icon: <Info className="w-5 h-5" />,
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      borderColor: 'border-blue-200 dark:border-blue-800',
      textColor: 'text-blue-800 dark:text-blue-200',
      iconColor: 'text-blue-600 dark:text-blue-400'
    }
  };

  const styles = config[type];

  return (
    <div className={cn(
      'p-4 rounded-lg border backdrop-blur-sm',
      styles.bgColor,
      styles.borderColor
    )}>
      <div className="flex items-start gap-3">
        <div className={styles.iconColor}>
          {styles.icon}
        </div>
        <div className="flex-1 min-w-0">
          <h4 className={cn('font-medium text-sm', styles.textColor)}>
            {title}
          </h4>
          <p className={cn('text-sm mt-1', styles.textColor)}>
            {message}
          </p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className={cn('p-1 hover:opacity-70', styles.textColor)}
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};`,

    loading: `import { Loader2 } from 'lucide-react';
import { Card } from '@/features/ui/primitives/card';

/**
 * 🤖 AI CONTEXT: Loading States Pattern
 *
 * PURPOSE: Visual feedback during async operations
 * WHEN TO USE: Data fetching, file uploads, processing operations
 * WHEN NOT TO USE: Instant operations, already completed actions
 *
 * LOADING TYPES:
 * - Spinner: Quick operations (< 5 seconds)
 * - Progress: Trackable operations with known duration
 * - Skeleton: Content loading with known structure
 * - Pulse: Unknown duration, maintaining layout
 *
 * UX GUIDELINES:
 * - Show immediately for operations > 500ms
 * - Provide progress feedback when possible
 * - Maintain layout during loading states
 * - Include descriptive text for clarity
 */

// Spinner Loading
export const SpinnerLoader = ({ text }: { text?: string }) => (
  <div className="flex items-center justify-center gap-3 p-8">
    <Loader2 className="w-5 h-5 animate-spin text-cyan-500" />
    {text && (
      <span className="text-sm text-gray-600 dark:text-gray-400">
        {text}
      </span>
    )}
  </div>
);

// Progress Loading
export const ProgressLoader = ({
  progress,
  text
}: {
  progress: number;
  text?: string;
}) => (
  <div className="p-4 space-y-3">
    {text && (
      <div className="flex justify-between text-sm">
        <span>{text}</span>
        <span>{progress}%</span>
      </div>
    )}
    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
      <div
        className="bg-cyan-500 h-2 rounded-full transition-all duration-300"
        style={{ width: \`\${progress}%\` }}
      />
    </div>
  </div>
);

// Skeleton Loading
export const SkeletonLoader = () => (
  <div className="animate-pulse space-y-4">
    <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-3/4" />
    <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-1/2" />
    <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-5/6" />
  </div>
);

// Card Loading
export const CardLoader = () => (
  <Card className="animate-pulse opacity-60">
    <div className="h-20 bg-gray-300 dark:bg-gray-700 rounded" />
  </Card>
);`,

    toasts: `import { useState, useEffect } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { glassmorphism } from '@/features/ui/primitives/styles';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';

/**
 * 🤖 AI CONTEXT: Toast Notifications Pattern
 *
 * PURPOSE: Temporary, non-blocking feedback messages
 * WHEN TO USE: Action confirmations, background updates, quick feedback
 * WHEN NOT TO USE: Critical errors (use alerts), complex messages (use modals)
 *
 * TOAST CHARACTERISTICS:
 * - Auto-dismiss after 3-5 seconds
 * - Non-blocking, can be dismissed manually
 * - Stack vertically in corner of screen
 * - Use glassmorphism for modern feel
 *
 * POSITIONING:
 * - Top-right: Most common, non-intrusive
 * - Top-center: Important announcements
 * - Bottom-right: Mobile-friendly alternative
 */

interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
}

export const useToast = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (toast: Omit<Toast, 'id'>) => {
    const id = Date.now().toString();
    const newToast = { ...toast, id };

    setToasts(prev => [...prev, newToast]);

    // Auto-remove
    setTimeout(() => {
      removeToast(id);
    }, toast.duration || 4000);

    return id;
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return { toasts, addToast, removeToast };
};

export const ToastContainer = ({
  toasts,
  onRemove
}: {
  toasts: Toast[];
  onRemove: (id: string) => void;
}) => {
  const getToastStyles = (type: string) => {
    const styles = {
      success: {
        border: 'border-green-500',
        glow: glassmorphism.shadow.glow.green,
        icon: <CheckCircle className="w-5 h-5 text-green-500" />
      },
      error: {
        border: 'border-red-500',
        glow: glassmorphism.shadow.glow.red,
        icon: <XCircle className="w-5 h-5 text-red-500" />
      },
      warning: {
        border: 'border-orange-500',
        glow: glassmorphism.shadow.glow.orange,
        icon: <AlertTriangle className="w-5 h-5 text-orange-500" />
      },
      info: {
        border: 'border-blue-500',
        glow: glassmorphism.shadow.glow.blue,
        icon: <Info className="w-5 h-5 text-blue-500" />
      }
    };
    return styles[type as keyof typeof styles];
  };

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {toasts.map((toast) => {
        const styles = getToastStyles(toast.type);
        return (
          <div
            key={toast.id}
            className={cn(
              'p-4 rounded-lg border backdrop-blur-md',
              'animate-in slide-in-from-right duration-300',
              glassmorphism.background.card,
              styles.border,
              styles.glow
            )}
          >
            <div className="flex items-start gap-3">
              {styles.icon}
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-sm">{toast.title}</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {toast.message}
                </p>
              </div>
              <button
                onClick={() => onRemove(toast.id)}
                className="p-1 hover:opacity-70"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};`,

    empty: `import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { HelpCircle, AlertCircle, Info } from 'lucide-react';

/**
 * 🤖 AI CONTEXT: Empty States Pattern
 *
 * PURPOSE: Helpful guidance when no content is available
 * WHEN TO USE: Empty lists, no search results, disabled features
 * WHEN NOT TO USE: Loading states, error conditions, temporary states
 *
 * EMPTY STATE TYPES:
 * - No Data: First-time use, empty collections
 * - No Results: Search/filter yielded nothing
 * - Feature Disabled: Functionality not available
 * - Coming Soon: Planned but not implemented
 *
 * CONTENT GUIDELINES:
 * - Clear, descriptive title
 * - Helpful explanation or next steps
 * - Primary action when applicable
 * - Appropriate icon for context
 */

interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState = ({
  icon,
  title,
  description,
  action,
  className
}: EmptyStateProps) => (
  <Card className={cn('text-center p-12', className)}>
    <div className="mx-auto mb-4">
      {icon}
    </div>
    <h3 className="font-semibold text-lg mb-2">{title}</h3>
    <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
      {description}
    </p>
    {action}
  </Card>
);

// Predefined empty states
export const NoDataState = ({
  onAction
}: {
  onAction?: () => void;
}) => (
  <EmptyState
    icon={<HelpCircle className="w-16 h-16 text-gray-400" />}
    title="No projects found"
    description="Get started by creating your first project. You can organize your work and collaborate with your team."
    action={
      onAction && (
        <Button onClick={onAction}>
          Create Your First Project
        </Button>
      )
    }
  />
);

export const NoSearchResultsState = ({
  onClearFilters
}: {
  onClearFilters?: () => void;
}) => (
  <EmptyState
    icon={<AlertCircle className="w-16 h-16 text-gray-400" />}
    title="No results found"
    description="We couldn't find any projects matching your search criteria. Try adjusting your filters or search terms."
    action={
      onClearFilters && (
        <Button variant="outline" onClick={onClearFilters}>
          Clear All Filters
        </Button>
      )
    }
  />
);

export const ComingSoonState = ({ feature }: { feature: string }) => (
  <EmptyState
    icon={<Info className="w-16 h-16 text-cyan-500" />}
    title={\`\${feature} coming soon\`}
    description="This feature is currently under development. We'll notify you when it becomes available."
  />
);`
  };

  return codeExamples[patternId as keyof typeof codeExamples] || '';
};

export const FeedbackPattern = () => {
  const [selectedPattern, setSelectedPattern] = useState<string>('alerts');

  const currentPattern = FEEDBACK_PATTERNS.find(p => p.id === selectedPattern);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Feedback Patterns</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          User feedback patterns including alerts, loading states, notifications, and empty states.
        </p>
      </div>

      {/* Pattern Selector */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Select Feedback Pattern</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {FEEDBACK_PATTERNS.map((pattern) => (
            <Card
              key={pattern.id}
              className={cn(
                "p-4 cursor-pointer transition-all duration-200",
                selectedPattern === pattern.id
                  ? "border-cyan-500 shadow-[0_0_10px_rgba(34,211,238,0.3)]"
                  : "hover:shadow-lg"
              )}
              onClick={() => setSelectedPattern(pattern.id)}
            >
              <h4 className="font-medium mb-2">{pattern.name}</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                {pattern.description}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                <strong>Use for:</strong> {pattern.usage}
              </p>
            </Card>
          ))}
        </div>
      </Card>

      {/* Live Preview */}
      {currentPattern && (
        <Card className="p-6 max-w-none">
          <h3 className="text-lg font-semibold mb-4">
            {currentPattern.name} - Examples
          </h3>
          <currentPattern.component />
        </Card>
      )}

      {/* Generated Code */}
      {currentPattern && (
        <Card className="p-6 max-w-none">
          <h3 className="text-lg font-semibold mb-4">Generated Code</h3>
          <CodeDisplay
            code={generateCode(selectedPattern)}
            
            showLineNumbers
          />
        </Card>
      )}
    </div>
  );
};