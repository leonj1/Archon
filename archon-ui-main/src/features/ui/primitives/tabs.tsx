import * as TabsPrimitive from "@radix-ui/react-tabs";
import React from "react";
import { cn } from "./styles";

// Root
export const Tabs = TabsPrimitive.Root;

// List - styled like pill navigation
export const TabsList = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={cn(
      "backdrop-blur-sm bg-white/40 dark:bg-white/5 border border-white/30 dark:border-white/15 rounded-full p-1 shadow-lg inline-flex gap-1",
      className
    )}
    role="tablist"
    {...props}
  />
));
TabsList.displayName = TabsPrimitive.List.displayName;

// Trigger
export const TabsTrigger = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger> & {
    color?: "blue" | "purple" | "pink" | "orange" | "cyan" | "green";
  }
>(({ className, color = "blue", ...props }, ref) => {
  const colorMap = {
    blue: {
      text: "data-[state=active]:text-blue-600 dark:data-[state=active]:text-blue-400",
      glow: "data-[state=active]:bg-blue-500 data-[state=active]:shadow-[0_0_10px_2px_rgba(59,130,246,0.4)] dark:data-[state=active]:shadow-[0_0_20px_5px_rgba(59,130,246,0.7)]",
      hover: "hover:text-blue-500 dark:hover:text-blue-400/70",
    },
    purple: {
      text: "data-[state=active]:text-purple-600 dark:data-[state=active]:text-purple-400",
      glow: "data-[state=active]:bg-purple-500 data-[state=active]:shadow-[0_0_10px_2px_rgba(168,85,247,0.4)] dark:data-[state=active]:shadow-[0_0_20px_5px_rgba(168,85,247,0.7)]",
      hover: "hover:text-purple-500 dark:hover:text-purple-400/70",
    },
    pink: {
      text: "data-[state=active]:text-pink-600 dark:data-[state=active]:text-pink-400",
      glow: "data-[state=active]:bg-pink-500 data-[state=active]:shadow-[0_0_10px_2px_rgba(236,72,153,0.4)] dark:data-[state=active]:shadow-[0_0_20px_5px_rgba(236,72,153,0.7)]",
      hover: "hover:text-pink-500 dark:hover:text-pink-400/70",
    },
    orange: {
      text: "data-[state=active]:text-orange-600 dark:data-[state=active]:text-orange-400",
      glow: "data-[state=active]:bg-orange-500 data-[state=active]:shadow-[0_0_10px_2px_rgba(249,115,22,0.4)] dark:data-[state=active]:shadow-[0_0_20px_5px_rgba(249,115,22,0.7)]",
      hover: "hover:text-orange-500 dark:hover:text-orange-400/70",
    },
    cyan: {
      text: "data-[state=active]:text-cyan-600 dark:data-[state=active]:text-cyan-400",
      glow: "data-[state=active]:bg-cyan-500 data-[state=active]:shadow-[0_0_10px_2px_rgba(34,211,238,0.4)] dark:data-[state=active]:shadow-[0_0_20px_5px_rgba(34,211,238,0.7)]",
      hover: "hover:text-cyan-500 dark:hover:text-cyan-400/70",
    },
    green: {
      text: "data-[state=active]:text-emerald-600 dark:data-[state=active]:text-emerald-400",
      glow: "data-[state=active]:bg-emerald-500 data-[state=active]:shadow-[0_0_10px_2px_rgba(16,185,129,0.4)] dark:data-[state=active]:shadow-[0_0_20px_5px_rgba(16,185,129,0.7)]",
      hover: "hover:text-emerald-500 dark:hover:text-emerald-400/70",
    },
  };

  const activeClasses = {
    blue: "data-[state=active]:bg-blue-500/20 dark:data-[state=active]:bg-blue-400/20 data-[state=active]:text-blue-700 dark:data-[state=active]:text-blue-300 data-[state=active]:border data-[state=active]:border-blue-400/50 data-[state=active]:shadow-[0_0_10px_rgba(59,130,246,0.5)]",
    purple: "data-[state=active]:bg-purple-500/20 dark:data-[state=active]:bg-purple-400/20 data-[state=active]:text-purple-700 dark:data-[state=active]:text-purple-300 data-[state=active]:border data-[state=active]:border-purple-400/50 data-[state=active]:shadow-[0_0_10px_rgba(168,85,247,0.5)]",
    pink: "data-[state=active]:bg-pink-500/20 dark:data-[state=active]:bg-pink-400/20 data-[state=active]:text-pink-700 dark:data-[state=active]:text-pink-300 data-[state=active]:border data-[state=active]:border-pink-400/50 data-[state=active]:shadow-[0_0_10px_rgba(236,72,153,0.5)]",
    orange: "data-[state=active]:bg-orange-500/20 dark:data-[state=active]:bg-orange-400/20 data-[state=active]:text-orange-700 dark:data-[state=active]:text-orange-300 data-[state=active]:border data-[state=active]:border-orange-400/50 data-[state=active]:shadow-[0_0_10px_rgba(251,146,60,0.5)]",
    cyan: "data-[state=active]:bg-cyan-500/20 dark:data-[state=active]:bg-cyan-400/20 data-[state=active]:text-cyan-700 dark:data-[state=active]:text-cyan-300 data-[state=active]:border data-[state=active]:border-cyan-400/50 data-[state=active]:shadow-[0_0_10px_rgba(34,211,238,0.5)]",
    green: "data-[state=active]:bg-green-500/20 dark:data-[state=active]:bg-green-400/20 data-[state=active]:text-green-700 dark:data-[state=active]:text-green-300 data-[state=active]:border data-[state=active]:border-green-400/50 data-[state=active]:shadow-[0_0_10px_rgba(16,185,129,0.5)]",
  };

  return (
    <TabsPrimitive.Trigger
      ref={ref}
      className={cn(
        "flex items-center gap-2 px-6 py-2.5 rounded-full transition-all duration-200",
        "text-sm font-medium whitespace-nowrap",
        "text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
        "disabled:pointer-events-none disabled:opacity-50",
        activeClasses[color],
        className,
      )}
      {...props}
    >
      {props.children}
    </TabsPrimitive.Trigger>
  );
});
TabsTrigger.displayName = TabsPrimitive.Trigger.displayName;

// Content
export const TabsContent = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={cn(
      "mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
      className,
    )}
    {...props}
  />
));
TabsContent.displayName = TabsPrimitive.Content.displayName;
