import React from "react";
import { cn, glassCard } from "./styles";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  // Glass properties
  blur?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl';
  transparency?: 'clear' | 'light' | 'medium' | 'frosted' | 'solid';
  glassTint?: 'none' | 'purple' | 'blue' | 'cyan' | 'green' | 'orange' | 'pink' | 'red';

  // Glow properties
  glowColor?: 'none' | 'purple' | 'blue' | 'cyan' | 'green' | 'orange' | 'pink' | 'red';

  // Edge-lit properties
  edgePosition?: 'none' | 'top' | 'left' | 'right' | 'bottom';
  edgeColor?: 'purple' | 'blue' | 'cyan' | 'green' | 'orange' | 'pink' | 'red';

  // Size
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({
    className,
    blur = 'xl',
    transparency = 'light',
    glassTint = 'none',
    glowColor = 'none',
    edgePosition = 'none',
    edgeColor = 'cyan',
    size = 'md',
    children,
    ...props
  }, ref) => {
    const glowVariant = glassCard.variants[glowColor] || glassCard.variants.none;
    const hasEdge = edgePosition !== 'none';

    // Edge color mappings
    const edgeColors = {
      purple: { solid: 'bg-purple-500', gradient: 'from-purple-500/40', border: 'border-purple-500/30' },
      blue: { solid: 'bg-blue-500', gradient: 'from-blue-500/40', border: 'border-blue-500/30' },
      cyan: { solid: 'bg-cyan-500', gradient: 'from-cyan-500/40', border: 'border-cyan-500/30' },
      green: { solid: 'bg-green-500', gradient: 'from-green-500/40', border: 'border-green-500/30' },
      orange: { solid: 'bg-orange-500', gradient: 'from-orange-500/40', border: 'border-orange-500/30' },
      pink: { solid: 'bg-pink-500', gradient: 'from-pink-500/40', border: 'border-pink-500/30' },
      red: { solid: 'bg-red-500', gradient: 'from-red-500/40', border: 'border-red-500/30' },
    };

    const edgeStyle = edgeColors[edgeColor];

    // Tint backgrounds for edge-lit cards
    const tintBackgrounds = {
      purple: 'bg-gradient-to-br from-purple-500/15 to-purple-600/5',
      blue: 'bg-gradient-to-br from-blue-500/15 to-blue-600/5',
      cyan: 'bg-gradient-to-br from-cyan-500/15 to-cyan-600/5',
      green: 'bg-gradient-to-br from-green-500/15 to-green-600/5',
      orange: 'bg-gradient-to-br from-orange-500/15 to-orange-600/5',
      pink: 'bg-gradient-to-br from-pink-500/15 to-pink-600/5',
      red: 'bg-gradient-to-br from-red-500/15 to-red-600/5',
    };

    if (hasEdge && edgePosition === 'top') {
      // Edge-lit card with actual div elements (not pseudo-elements)
      return (
        <div
          ref={ref}
          className={cn(
            "relative rounded-xl overflow-hidden",
            edgeStyle.border,
            className
          )}
          {...props}
        >
          {/* Top edge light bar */}
          <div className={cn("absolute inset-x-0 top-0 h-[3px] pointer-events-none z-10", edgeStyle.solid)} />
          {/* Glow bleeding into card */}
          <div className={cn("absolute inset-x-0 top-0 h-16 bg-gradient-to-b to-transparent blur-lg pointer-events-none z-10", edgeStyle.gradient)} />
          {/* Content with tinted background */}
          <div className={cn("backdrop-blur-sm", tintBackgrounds[edgeColor], glassCard.sizes[size])}>
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
          glassCard.base,
          glassCard.blur[blur],
          glassTint !== 'none'
            ? glassCard.tints[glassTint][transparency]
            : glassCard.transparency[transparency],
          glassCard.sizes[size],
          !hasEdge && glowVariant.border,
          !hasEdge && glowVariant.glow,
          !hasEdge && glowVariant.hover,
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = "Card";