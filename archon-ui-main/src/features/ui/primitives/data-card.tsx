import React from "react";
import { cn, glassCard } from "./styles";

interface DataCardProps extends React.HTMLAttributes<HTMLDivElement> {
  // Edge-lit properties
  edgePosition?: 'none' | 'top' | 'left' | 'right' | 'bottom';
  edgeColor?: 'purple' | 'blue' | 'cyan' | 'green' | 'orange' | 'pink' | 'red';

  // Glow properties
  glowColor?: 'none' | 'purple' | 'blue' | 'cyan' | 'green' | 'orange' | 'pink' | 'red';

  // Glass properties
  blur?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  transparency?: 'clear' | 'light' | 'medium' | 'frosted' | 'solid';
}

interface DataCardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}
interface DataCardContentProps extends React.HTMLAttributes<HTMLDivElement> {}
interface DataCardFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

// Edge color mappings for edge-lit cards
const edgeColors = {
  purple: { solid: 'bg-purple-500', gradient: 'from-purple-500/40', border: 'border-purple-500/30', bg: 'bg-gradient-to-br from-purple-500/15 to-purple-600/5' },
  blue: { solid: 'bg-blue-500', gradient: 'from-blue-500/40', border: 'border-blue-500/30', bg: 'bg-gradient-to-br from-blue-500/15 to-blue-600/5' },
  cyan: { solid: 'bg-cyan-500', gradient: 'from-cyan-500/40', border: 'border-cyan-500/30', bg: 'bg-gradient-to-br from-cyan-500/15 to-cyan-600/5' },
  green: { solid: 'bg-green-500', gradient: 'from-green-500/40', border: 'border-green-500/30', bg: 'bg-gradient-to-br from-green-500/15 to-green-600/5' },
  orange: { solid: 'bg-orange-500', gradient: 'from-orange-500/40', border: 'border-orange-500/30', bg: 'bg-gradient-to-br from-orange-500/15 to-orange-600/5' },
  pink: { solid: 'bg-pink-500', gradient: 'from-pink-500/40', border: 'border-pink-500/30', bg: 'bg-gradient-to-br from-pink-500/15 to-pink-600/5' },
  red: { solid: 'bg-red-500', gradient: 'from-red-500/40', border: 'border-red-500/30', bg: 'bg-gradient-to-br from-red-500/15 to-red-600/5' },
};

const blurClasses = {
  none: "backdrop-blur-none",
  sm: "backdrop-blur-sm",
  md: "backdrop-blur-md",
  lg: "backdrop-blur-lg",
  xl: "backdrop-blur-xl",
};

const transparencyClasses = {
  clear: "bg-white/[0.02] dark:bg-white/[0.01]",
  light: "bg-white/[0.08] dark:bg-white/[0.05]",
  medium: "bg-white/[0.15] dark:bg-white/[0.08]",
  frosted: "bg-white/[0.40] dark:bg-black/[0.40]",
  solid: "bg-white/[0.90] dark:bg-black/[0.95]",
};

export const DataCard = React.forwardRef<HTMLDivElement, DataCardProps>(
  ({
    className,
    edgePosition = 'none',
    edgeColor = 'cyan',
    glowColor = 'none',
    blur = 'md',
    transparency = 'light',
    children,
    ...props
  }, ref) => {
    const hasEdge = edgePosition !== 'none';
    const edgeStyle = hasEdge ? edgeColors[edgeColor] : null;

    if (hasEdge && edgePosition === 'top') {
      return (
        <div
          ref={ref}
          className={cn(
            "relative rounded-xl overflow-hidden min-h-[240px]",
            edgeStyle?.border,
            className
          )}
          {...props}
        >
          {/* Top edge light */}
          <div className={cn("absolute inset-x-0 top-0 h-[2px] pointer-events-none z-10", edgeStyle?.solid)} />
          {/* Glow bleeding down */}
          <div className={cn("absolute inset-x-0 top-0 h-16 bg-gradient-to-b to-transparent blur-lg pointer-events-none z-10", edgeStyle?.gradient)} />

          {/* Content wrapper with flex layout */}
          <div className={cn(
            "flex flex-col min-h-[240px]",
            blurClasses[blur],
            edgeStyle?.bg
          )}>
            {children}
          </div>
        </div>
      );
    }

    // Standard card (no edge-lit)
    return (
      <div
        ref={ref}
        className={cn(
          "relative rounded-xl overflow-hidden border border-gray-300/20 dark:border-white/10 min-h-[240px]",
          blurClasses[blur],
          transparencyClasses[transparency],
          "flex flex-col",
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

DataCard.displayName = "DataCard";

// Header component
export const DataCardHeader = React.forwardRef<HTMLDivElement, DataCardHeaderProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div ref={ref} className={cn("relative p-4 pb-2", className)} {...props}>
        {children}
      </div>
    );
  }
);

DataCardHeader.displayName = "DataCardHeader";

// Content component (flexible - grows to fill space)
export const DataCardContent = React.forwardRef<HTMLDivElement, DataCardContentProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div ref={ref} className={cn("flex-1 px-4", className)} {...props}>
        {children}
      </div>
    );
  }
);

DataCardContent.displayName = "DataCardContent";

// Footer component (anchored to bottom)
export const DataCardFooter = React.forwardRef<HTMLDivElement, DataCardFooterProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "px-4 py-3 bg-gray-100/50 dark:bg-black/30 border-t border-gray-200/50 dark:border-white/10",
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

DataCardFooter.displayName = "DataCardFooter";
