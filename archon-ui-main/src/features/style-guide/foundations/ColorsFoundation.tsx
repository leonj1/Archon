import { Card } from '@/features/ui/primitives/card';
import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

// Core color palette with neon variations
const CORE_COLORS = [
  {
    name: 'Cyan',
    base: '#06b6d4',
    variants: {
      50: '#ecfeff',
      100: '#cffafe',
      200: '#a5f3fc',
      300: '#67e8f9',
      400: '#22d3ee',
      500: '#06b6d4',
      600: '#0891b2',
      700: '#0e7490',
      800: '#155e75',
      900: '#164e63'
    },
    usage: 'Primary brand, active states, focus indicators'
  },
  {
    name: 'Blue',
    base: '#3b82f6',
    variants: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a'
    },
    usage: 'Information, links, secondary actions'
  },
  {
    name: 'Purple',
    base: '#a855f7',
    variants: {
      50: '#faf5ff',
      100: '#f3e8ff',
      200: '#e9d5ff',
      300: '#d8b4fe',
      400: '#c084fc',
      500: '#a855f7',
      600: '#9333ea',
      700: '#7c3aed',
      800: '#6b21a8',
      900: '#581c87'
    },
    usage: 'Secondary actions, creative elements, highlights'
  },
  {
    name: 'Emerald',
    base: '#10b981',
    variants: {
      50: '#ecfdf5',
      100: '#d1fae5',
      200: '#a7f3d0',
      300: '#6ee7b7',
      400: '#34d399',
      500: '#10b981',
      600: '#059669',
      700: '#047857',
      800: '#065f46',
      900: '#064e3b'
    },
    usage: 'Success states, positive feedback, growth indicators'
  },
  {
    name: 'Orange',
    base: '#f97316',
    variants: {
      50: '#fff7ed',
      100: '#ffedd5',
      200: '#fed7aa',
      300: '#fdba74',
      400: '#fb923c',
      500: '#f97316',
      600: '#ea580c',
      700: '#c2410c',
      800: '#9a3412',
      900: '#7c2d12'
    },
    usage: 'Warnings, notifications, energy elements'
  },
  {
    name: 'Pink',
    base: '#ec4899',
    variants: {
      50: '#fdf2f8',
      100: '#fce7f3',
      200: '#fbcfe8',
      300: '#f9a8d4',
      400: '#f472b6',
      500: '#ec4899',
      600: '#db2777',
      700: '#be185d',
      800: '#9d174d',
      900: '#831843'
    },
    usage: 'Special features, premium content, creativity'
  },
  {
    name: 'Red',
    base: '#ef4444',
    variants: {
      50: '#fef2f2',
      100: '#fee2e2',
      200: '#fecaca',
      300: '#fca5a5',
      400: '#f87171',
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c',
      800: '#991b1b',
      900: '#7f1d1d'
    },
    usage: 'Errors, dangerous actions, critical alerts'
  }
];

// Effect types for demonstration
const EFFECT_TYPES = [
  { name: 'Solid', key: 'solid' },
  { name: 'Border', key: 'border' },
  { name: 'Inner Glow', key: 'inner-glow' },
  { name: 'Outer Glow', key: 'outer-glow' },
  { name: 'Text', key: 'text' }
];

// Interactive Color Swatch with Selector and Slider
const InteractiveColorSwatch = ({ color }: { color: any }) => {
  const [selectedVariant, setSelectedVariant] = useState(500);
  const [copied, setCopied] = useState(false);

  const currentColor = color.variants[selectedVariant as keyof typeof color.variants];

  const handleCopy = () => {
    navigator.clipboard.writeText(currentColor);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{color.name}</h3>
        <div
          className="w-8 h-8 rounded-full border-2 border-gray-300 dark:border-gray-600 cursor-pointer transition-transform hover:scale-110"
          style={{ backgroundColor: currentColor }}
          onClick={handleCopy}
        />
      </div>

      <p className="text-gray-600 dark:text-gray-400 text-sm">{color.usage}</p>

      {/* Color Selector with Current Swatch */}
      <div
        className="group relative rounded-lg overflow-hidden cursor-pointer transition-transform hover:scale-105 border border-gray-200 dark:border-gray-700"
        onClick={handleCopy}
      >
        <div
          className="h-20 w-full transition-all duration-200"
          style={{ backgroundColor: currentColor }}
        />
        <div className="p-3 bg-white dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">{color.name}-{selectedVariant}</p>
              <p className="text-xs text-gray-600 dark:text-gray-400 font-mono">{currentColor}</p>
            </div>
            <div className="opacity-60 group-hover:opacity-100 transition-opacity">
              {copied ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <Copy className="w-4 h-4 text-gray-400" />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Variant Slider */}
      <div>
        <label className="block text-sm font-medium mb-2">Color Weight: {selectedVariant}</label>
        <input
          type="range"
          min="100"
          max="900"
          step="100"
          value={selectedVariant}
          onChange={(e) => setSelectedVariant(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
          style={{
            background: `linear-gradient(to right,
              ${color.variants[100]},
              ${color.variants[200]},
              ${color.variants[300]},
              ${color.variants[400]},
              ${color.variants[500]},
              ${color.variants[600]},
              ${color.variants[700]},
              ${color.variants[800]},
              ${color.variants[900]})`
          }}
        />
        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>100</span>
          <span>500</span>
          <span>900</span>
        </div>
      </div>
    </div>
  );
};

// Enhanced Effect demonstration component with improved glow
const EffectDemo = ({ color, effectType }: { color: any, effectType: string }) => {
  const getEffectStyles = () => {
    switch (effectType) {
      case 'solid':
        return {
          backgroundColor: color.base,
          color: 'white'
        };
      case 'border':
        return {
          border: `2px solid ${color.base}`,
          backgroundColor: 'transparent',
          color: color.base
        };
      case 'inner-glow':
        return {
          backgroundColor: `${color.base}40`, // More opaque for visibility
          border: `1px solid ${color.base}`,
          boxShadow: `inset 0 0 20px ${color.base}60`,
          color: color.base
        };
      case 'outer-glow':
        return {
          backgroundColor: `${color.base}20`,
          border: `1px solid ${color.base}`,
          boxShadow: `0 0 30px ${color.base}80, 0 0 60px ${color.base}40`,
          color: color.base
        };
      case 'text':
        return {
          color: color.base,
          backgroundColor: 'transparent'
        };
      default:
        return {};
    }
  };

  const getEffectName = () => {
    switch (effectType) {
      case 'solid': return 'Solid';
      case 'border': return 'Border';
      case 'inner-glow': return 'Inner Glow';
      case 'outer-glow': return 'Outer Glow';
      case 'text': return 'Text';
      default: return effectType;
    }
  };

  return (
    <div
      className="p-4 rounded-lg text-center transition-all duration-200 hover:scale-105"
      style={getEffectStyles()}
    >
      <p className="text-sm font-medium">{getEffectName()}</p>
    </div>
  );
};

export const ColorsFoundation = () => {
  const [copiedColor, setCopiedColor] = useState<string | null>(null);

  const handleColorCopy = (color: string) => {
    navigator.clipboard.writeText(color);
    setCopiedColor(color);
    setTimeout(() => setCopiedColor(null), 2000);
  };

  return (
    <div className="space-y-12">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Color System</h2>
        <p className="text-gray-600 dark:text-gray-400 text-lg max-w-3xl mx-auto">
          Neon-inspired color palette with solid fills, borders, glows, and text treatments for Tron-style interfaces.
        </p>
      </div>

      {/* Semantic Colors Overview */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-12">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto bg-gray-900 dark:bg-gray-100 rounded-lg mb-2"></div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Primary</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400">#111827</p>
        </div>
        <div className="text-center">
          <div className="w-16 h-16 mx-auto bg-gray-700 dark:bg-gray-300 rounded-lg mb-2"></div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Secondary</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400">#374151</p>
        </div>
        <div className="text-center">
          <div className="w-16 h-16 mx-auto bg-blue-500 rounded-lg mb-2 shadow-[0_0_20px_rgba(59,130,246,0.4)]"></div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Accent</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400">#3b82f6</p>
        </div>
        <div className="text-center">
          <div className="w-16 h-16 mx-auto bg-emerald-500 rounded-lg mb-2 shadow-[0_0_20px_rgba(16,185,129,0.4)]"></div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Success</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400">#10b981</p>
        </div>
        <div className="text-center">
          <div className="w-16 h-16 mx-auto bg-orange-500 rounded-lg mb-2 shadow-[0_0_20px_rgba(249,115,22,0.4)]"></div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Warning</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400">#f97316</p>
        </div>
        <div className="text-center">
          <div className="w-16 h-16 mx-auto bg-red-500 rounded-lg mb-2 shadow-[0_0_20px_rgba(239,68,68,0.4)]"></div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Error</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400">#ef4444</p>
        </div>
      </div>

      {/* Interactive Color Palette */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {CORE_COLORS.map((color) => (
          <Card key={color.name} className="p-6">
            <InteractiveColorSwatch color={color} />

            {/* Effect Demonstrations */}
            <div className="mt-6 space-y-3">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">Effects</h4>
              <div className="grid grid-cols-1 gap-3">
                {EFFECT_TYPES.map((effect) => (
                  <EffectDemo
                    key={effect.key}
                    color={color}
                    effectType={effect.key}
                  />
                ))}
              </div>
            </div>
          </Card>
        ))}
      </div>


      {/* Copy Notification */}
      {copiedColor && (
        <div className="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg">
          Copied {copiedColor} to clipboard!
        </div>
      )}
    </div>
  );
};