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
    blur = 'xl',  // Default to standard glass (3px blur - subtle)
    transparency = 'light',  // Default to subtle transparency (3%)
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
    const isHorizontalEdge = edgePosition === 'top' || edgePosition === 'bottom';
    const edgeColorConfig = hasEdge ? glassCard.edgeLit.color[edgeColor] : null;

    return (
      <div
        ref={ref}
        className={cn(
          // Base glass effect
          glassCard.base,

          // Backdrop blur intensity - consistent glass effect
          glassCard.blur[blur],

          // Apply background with proper transparency
          glassTint !== 'none'
            ? glassCard.tints[glassTint][transparency]
            : glassCard.transparency[transparency],

          // Size
          glassCard.sizes[size],

          // Glow effects (border, shadow, hover) - only if no edge-lit
          !hasEdge && glowVariant.border,
          !hasEdge && glowVariant.glow,
          !hasEdge && glowVariant.hover,

          // Edge-lit effects
          hasEdge && glassCard.edgeLit.position[edgePosition],
          hasEdge && edgeColorConfig ? edgeColorConfig.glow : false,
          hasEdge && edgeColorConfig ? (
            isHorizontalEdge
              ? edgeColorConfig.gradient.horizontal
              : edgeColorConfig.gradient.vertical
          ) : false,

          // User overrides
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