import React from "react";
import { cn, glassCard } from "./styles";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  // Glass properties
  blur?: "none" | "sm" | "md" | "lg" | "xl" | "2xl" | "3xl";
  transparency?: "clear" | "light" | "medium" | "frosted" | "solid";
  glassTint?: "none" | "purple" | "blue" | "cyan" | "green" | "orange" | "pink" | "red";

  // Glow properties (uses pre-defined static classes from styles.ts)
  glowColor?: "none" | "purple" | "blue" | "cyan" | "green" | "orange" | "pink" | "red";
  glowType?: "outer" | "inner";
  glowSize?: "sm" | "md" | "lg" | "xl";

  // Edge-lit properties
  edgePosition?: "none" | "top" | "left" | "right" | "bottom";
  edgeColor?: "purple" | "blue" | "cyan" | "green" | "orange" | "pink" | "red";

  // Size (padding)
  size?: "none" | "sm" | "md" | "lg" | "xl";
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      className,
      blur = "md",
      transparency = "light",
      glassTint = "none",
      glowColor = "none",
      glowType = "outer",
      glowSize = "md",
      edgePosition = "none",
      edgeColor = "cyan",
      size = "md",
      children,
      ...props
    },
    ref,
  ) => {
    const hasEdge = edgePosition !== "none";
    const hasGlow = glowColor !== "none";

    // Use pre-defined static classes from styles.ts
    const glowVariant = glassCard.variants[glowColor] || glassCard.variants.none;

    // Get glow class from static lookups in styles.ts
    const getGlowClass = () => {
      if (!hasGlow || hasEdge) return "";

      if (glowType === "inner") {
        return glassCard.innerGlowSizes?.[glowColor]?.[glowSize] || "";
      }

      // Outer glow
      return glassCard.outerGlowSizes?.[glowColor]?.[glowSize] || glowVariant.glow;
    };

    // Get size-matched hover glow class
    const getHoverGlowClass = () => {
      if (!hasGlow || hasEdge) return "";

      if (glowType === "inner") {
        return glassCard.innerGlowHover?.[glowColor]?.[glowSize] || "";
      }

      // Outer glow hover
      return glassCard.outerGlowHover?.[glowColor]?.[glowSize] || glowVariant.hover;
    };

    // Edge color mappings
    const edgeColors = {
      purple: { solid: "bg-purple-500", gradient: "from-purple-500/40", border: "border-purple-500/30" },
      blue: { solid: "bg-blue-500", gradient: "from-blue-500/40", border: "border-blue-500/30" },
      cyan: { solid: "bg-cyan-500", gradient: "from-cyan-500/40", border: "border-cyan-500/30" },
      green: { solid: "bg-green-500", gradient: "from-green-500/40", border: "border-green-500/30" },
      orange: { solid: "bg-orange-500", gradient: "from-orange-500/40", border: "border-orange-500/30" },
      pink: { solid: "bg-pink-500", gradient: "from-pink-500/40", border: "border-pink-500/30" },
      red: { solid: "bg-red-500", gradient: "from-red-500/40", border: "border-red-500/30" },
    };

    const edgeStyle = edgeColors[edgeColor];

    // Tint backgrounds for edge-lit cards
    const tintBackgrounds = {
      purple: "bg-gradient-to-br from-purple-500/15 to-purple-600/5",
      blue: "bg-gradient-to-br from-blue-500/15 to-blue-600/5",
      cyan: "bg-gradient-to-br from-cyan-500/15 to-cyan-600/5",
      green: "bg-gradient-to-br from-green-500/15 to-green-600/5",
      orange: "bg-gradient-to-br from-orange-500/15 to-orange-600/5",
      pink: "bg-gradient-to-br from-pink-500/15 to-pink-600/5",
      red: "bg-gradient-to-br from-red-500/15 to-red-600/5",
    };

    if (hasEdge) {
      // Edge-lit card with actual div elements (not pseudo-elements)
      // Extract flex/layout classes from className to apply to inner content div
      const flexClasses =
        className?.match(/(flex|flex-col|flex-row|flex-1|items-\S+|justify-\S+|gap-\S+)/g)?.join(" ") || "";
      const otherClasses =
        className?.replace(/(flex|flex-col|flex-row|flex-1|items-\S+|justify-\S+|gap-\S+)/g, "").trim() || "";

      // Edge line and glow configuration per position
      const edgeConfig = {
        top: {
          line: "absolute inset-x-0 top-0 h-[2px]",
          glow: "absolute inset-x-0 top-0 h-16 bg-gradient-to-b to-transparent",
        },
        bottom: {
          line: "absolute inset-x-0 bottom-0 h-[2px]",
          glow: "absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t to-transparent",
        },
        left: {
          line: "absolute inset-y-0 left-0 w-[2px]",
          glow: "absolute inset-y-0 left-0 w-16 bg-gradient-to-r to-transparent",
        },
        right: {
          line: "absolute inset-y-0 right-0 w-[2px]",
          glow: "absolute inset-y-0 right-0 w-16 bg-gradient-to-l to-transparent",
        },
      };

      const config = edgeConfig[edgePosition];

      return (
        <div ref={ref} className={cn("relative rounded-xl overflow-hidden", edgeStyle.border, otherClasses)} {...props}>
          {/* Edge light bar */}
          <div className={cn(config.line, "pointer-events-none z-10", edgeStyle.solid)} />
          {/* Glow bleeding into card */}
          <div className={cn(config.glow, "blur-lg pointer-events-none z-10", edgeStyle.gradient)} />
          {/* Content with tinted background - INHERIT flex classes */}
          <div className={cn("backdrop-blur-sm", tintBackgrounds[edgeColor], glassCard.sizes[size], flexClasses)}>
            {children}
          </div>
        </div>
      );
    }

    // Standard card (no edge-lit) - use static classes from styles.ts
    return (
      <div
        ref={ref}
        className={cn(
          glassCard.base,
          glassCard.blur[blur],
          glassTint !== "none" ? glassCard.tints[glassTint][transparency] : glassCard.transparency[transparency],
          glassCard.sizes[size],
          // Border and glow classes from static lookups
          !hasEdge && glowVariant.border,
          !hasEdge && getGlowClass(),
          !hasEdge && getHoverGlowClass(), // Size-matched hover
          className,
        )}
        {...props}
      >
        {children}
      </div>
    );
  },
);

Card.displayName = "Card";
