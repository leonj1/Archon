import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/features/ui/primitives/select';
import { Input } from '@/features/ui/primitives/input';
import { CodeDisplay } from '../shared/CodeDisplay';
import { cn } from '@/features/ui/primitives/styles';
import type { GlowColor, GlowType, EdgePosition, EdgeColor, CardSize, Transparency, BlurLevel, GlassTint } from '../types';

interface GlassCardConfig {
  blur: BlurLevel;
  transparency: Transparency;
  glassTint: GlassTint;
  glowColor: GlowColor;
  glowType: GlowType;
  edgePosition: EdgePosition;
  edgeColor: EdgeColor;
  size: CardSize;
  content: string;
}

// Glass card showcase examples
const GLASS_CARD_EXAMPLES = [
  {
    name: 'Clear Glass',
    transparency: 'light' as const,
    glassTint: 'none' as const,
    glowColor: 'none' as const,
    edgePosition: 'none' as const,
    description: 'Pure transparent glass',
    usage: 'Default containers, neutral elements'
  },
  {
    name: 'Purple Glass',
    transparency: 'medium' as const,
    glassTint: 'purple' as const,
    glowColor: 'none' as const,
    edgePosition: 'none' as const,
    description: 'Purple-tinted transparent glass',
    usage: 'Primary content areas'
  },
  {
    name: 'Cyan Inner Glow',
    transparency: 'light' as const,
    glassTint: 'none' as const,
    glowColor: 'cyan' as const,
    edgePosition: 'none' as const,
    description: 'Glass with cyan inner glow',
    usage: 'Active/selected states'
  },
  {
    name: 'Purple Outer Glow',
    transparency: 'light' as const,
    glassTint: 'none' as const,
    glowColor: 'purple' as const,
    edgePosition: 'none' as const,
    description: 'Glass with purple outer glow',
    usage: 'Featured content, CTAs'
  },
  {
    name: 'Purple Edge',
    transparency: 'light' as const,
    glassTint: 'none' as const,
    glowColor: 'none' as const,
    edgePosition: 'top' as const,
    description: 'Glass with purple top edge',
    usage: 'Knowledge cards, headers'
  },
  {
    name: 'Blue Left Edge',
    transparency: 'light' as const,
    glassTint: 'blue' as const,
    glowColor: 'none' as const,
    edgePosition: 'left' as const,
    description: 'Light blue glass with blue left edge',
    usage: 'Task cards, side content'
  }
];

export const GlassCardConfigurator = () => {
  const [activeView, setActiveView] = useState<'showcase' | 'configurator'>('showcase');
  const [config, setConfig] = useState<GlassCardConfig>({
    blur: 'xl',
    transparency: 'light',
    glassTint: 'none',
    glowColor: 'none',
    glowType: 'none',
    edgePosition: 'none',
    edgeColor: 'cyan',
    size: 'lg',
    content: 'Your glass card content here'
  });

  const generateCode = (config: GlassCardConfig) => {
    const props: string[] = [];
    if (config.blur !== 'xl') props.push(`blur="${config.blur}"`);
    if (config.transparency !== 'medium') props.push(`transparency="${config.transparency}"`);
    if (config.glassTint !== 'none') props.push(`glassTint="${config.glassTint}"`);
    if (config.glowColor !== 'none' && config.glowType === 'inner') props.push(`glowColor="${config.glowColor}"`);
    if (config.edgePosition !== 'none') props.push(`edgePosition="${config.edgePosition}"`);
    if (config.edgePosition !== 'none' && config.edgeColor !== 'cyan') props.push(`edgeColor="${config.edgeColor}"`);
    if (config.size !== 'md') props.push(`size="${config.size}"`);

    let additionalClasses = '';
    if (config.glowType === 'outer' && config.glowColor !== 'none') {
      additionalClasses = `\n      className="shadow-[0_0_30px_${config.glowColor}-500/80,_0_0_60px_${config.glowColor}-500/40]"`;
    } else if (config.glowType === 'inner' && config.glowColor !== 'none') {
      additionalClasses = `\n      className="bg-${config.glowColor}-500/40 border border-${config.glowColor}-500 shadow-[inset_0_0_20px_${config.glowColor}-500/60]"`;
    }

    return `import { Card } from '@/features/ui/primitives/card';

export const MyCard = () => {
  return (
    <Card${props.length > 0 ? '\n      ' + props.join('\n      ') : ''}${additionalClasses}>
      ${config.content}
    </Card>
  );
};`;
  };

  return (
    <div className="space-y-8">
      {/* Small Pill Navigation */}
      <div className="flex justify-center">
        <div className="backdrop-blur-sm bg-white/40 dark:bg-white/5 border border-white/30 dark:border-white/15 rounded-full p-1 shadow-lg">
          <div className="flex gap-1 items-center">
            <button
              onClick={() => setActiveView('showcase')}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-200",
                "text-sm font-medium whitespace-nowrap",
                activeView === 'showcase'
                  ? "bg-cyan-500/20 dark:bg-cyan-400/20 text-cyan-700 dark:text-cyan-300 border border-cyan-400/50 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                  : "text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5"
              )}
            >
              Showcase
            </button>
            <button
              onClick={() => setActiveView('configurator')}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-200",
                "text-sm font-medium whitespace-nowrap",
                activeView === 'configurator'
                  ? "bg-cyan-500/20 dark:bg-cyan-400/20 text-cyan-700 dark:text-cyan-300 border border-cyan-400/50 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                  : "text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5"
              )}
            >
              Configurator
            </button>
          </div>
        </div>
      </div>

      {/* Content based on active view */}
      {activeView === 'showcase' ? (
        <Card className="p-6">
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Glass Card Showcase</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {GLASS_CARD_EXAMPLES.map((example) => (
                <div key={example.name}>
                  {/* Apply proper effects based on example type */}
                  {example.name === 'Cyan Inner Glow' ? (
                    <Card
                      transparency={example.transparency}
                      glassTint={example.glassTint}
                      edgePosition="none"
                      className={cn(
                        "hover:scale-105 transition-transform duration-300",
                        "bg-cyan-500/40 border border-cyan-500 shadow-[inset_0_0_20px_rgba(34,211,238,0.6)]"
                      )}
                    >
                      <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{example.name}</h4>
                      <p className="text-gray-700 dark:text-gray-300 text-sm mb-2">{example.description}</p>
                      <p className="text-gray-600 dark:text-gray-400 text-xs">{example.usage}</p>
                    </Card>
                  ) : example.name === 'Purple Outer Glow' ? (
                    <div className="shadow-[0_0_30px_rgba(147,51,234,0.8),_0_0_60px_rgba(147,51,234,0.4)] transition-all duration-200 hover:scale-105 rounded-lg">
                      <Card
                        transparency={example.transparency}
                        glassTint={example.glassTint}
                        edgePosition="none"
                        className="transition-transform duration-300"
                      >
                        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{example.name}</h4>
                        <p className="text-gray-700 dark:text-gray-300 text-sm mb-2">{example.description}</p>
                        <p className="text-gray-600 dark:text-gray-400 text-xs">{example.usage}</p>
                      </Card>
                    </div>
                  ) : example.name === 'Purple Edge' ? (
                    <Card
                      transparency={example.transparency}
                      glassTint={example.glassTint}
                      edgePosition={example.edgePosition}
                      edgeColor="purple"
                      className="hover:scale-105 transition-transform duration-300"
                    >
                      <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{example.name}</h4>
                      <p className="text-gray-700 dark:text-gray-300 text-sm mb-2">{example.description}</p>
                      <p className="text-gray-600 dark:text-gray-400 text-xs">{example.usage}</p>
                    </Card>
                  ) : example.name === 'Blue Left Edge' ? (
                    <Card
                      transparency={example.transparency}
                      glassTint={example.glassTint}
                      edgePosition={example.edgePosition}
                      edgeColor="blue"
                      className="hover:scale-105 transition-transform duration-300"
                    >
                      <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{example.name}</h4>
                      <p className="text-gray-700 dark:text-gray-300 text-sm mb-2">{example.description}</p>
                      <p className="text-gray-600 dark:text-gray-400 text-xs">{example.usage}</p>
                    </Card>
                  ) : (
                    <Card
                      transparency={example.transparency}
                      glassTint={example.glassTint}
                      glowColor={example.glowColor}
                      edgePosition={example.edgePosition}
                      edgeColor="cyan"
                      className="hover:scale-105 transition-transform duration-300"
                    >
                      <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{example.name}</h4>
                      <p className="text-gray-700 dark:text-gray-300 text-sm mb-2">{example.description}</p>
                      <p className="text-gray-600 dark:text-gray-400 text-xs">{example.usage}</p>
                    </Card>
                  )}
                </div>
              ))}
            </div>
          </div>
        </Card>
      ) : (
        <div className="space-y-8">
          {/* Configurator with side-by-side layout */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Card Configurator</h3>

            <div className="grid grid-cols-2 gap-8">
              {/* Left: Configuration Controls */}
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium mb-1">Blur</label>
                    <Select
                      value={config.blur}
                      onValueChange={(value) => setConfig({...config, blur: value as BlurLevel})}
                    >
                      <SelectTrigger className="text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        <SelectItem value="sm">Minimal</SelectItem>
                        <SelectItem value="md">Subtle</SelectItem>
                        <SelectItem value="lg">Light</SelectItem>
                        <SelectItem value="xl">Standard</SelectItem>
                        <SelectItem value="2xl">Noticeable</SelectItem>
                        <SelectItem value="3xl">Maximum</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Transparency</label>
                    <Select
                      value={config.transparency}
                      onValueChange={(value) => setConfig({...config, transparency: value as Transparency})}
                    >
                      <SelectTrigger className="text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="clear">Clear</SelectItem>
                        <SelectItem value="light">Light</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="frosted">Frosted</SelectItem>
                        <SelectItem value="solid">Solid</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Glass Tint</label>
                    <Select
                      value={config.glassTint}
                      onValueChange={(value) => setConfig({...config, glassTint: value as GlassTint})}
                    >
                      <SelectTrigger className="text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        <SelectItem value="purple">🟣 Purple</SelectItem>
                        <SelectItem value="blue">🔵 Blue</SelectItem>
                        <SelectItem value="cyan">🔷 Cyan</SelectItem>
                        <SelectItem value="green">🟢 Green</SelectItem>
                        <SelectItem value="orange">🟠 Orange</SelectItem>
                        <SelectItem value="pink">🩷 Pink</SelectItem>
                        <SelectItem value="red">🔴 Red</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Glow Type</label>
                    <Select
                      value={config.glowType}
                      onValueChange={(value) => setConfig({...config, glowType: value as GlowType, glowColor: value === 'none' ? 'none' : config.glowColor || 'cyan'})}
                      disabled={config.edgePosition !== 'none'}
                    >
                      <SelectTrigger className="text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        <SelectItem value="inner">Inner</SelectItem>
                        <SelectItem value="outer">Outer</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Glow Color</label>
                    <Select
                      value={config.glowColor}
                      onValueChange={(value) => setConfig({...config, glowColor: value as GlowColor})}
                      disabled={config.glowType === 'none'}
                    >
                      <SelectTrigger className="text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="purple">🟣 Purple</SelectItem>
                        <SelectItem value="blue">🔵 Blue</SelectItem>
                        <SelectItem value="cyan">🔷 Cyan</SelectItem>
                        <SelectItem value="green">🟢 Green</SelectItem>
                        <SelectItem value="orange">🟠 Orange</SelectItem>
                        <SelectItem value="pink">🩷 Pink</SelectItem>
                        <SelectItem value="red">🔴 Red</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Edge Position</label>
                    <Select
                      value={config.edgePosition}
                      onValueChange={(value) => {
                        setConfig({
                          ...config,
                          edgePosition: value as EdgePosition,
                          glowType: value !== 'none' ? 'none' : config.glowType
                        });
                      }}
                    >
                      <SelectTrigger className="text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        <SelectItem value="top">↑ Top</SelectItem>
                        <SelectItem value="left">← Left</SelectItem>
                        <SelectItem value="right">→ Right</SelectItem>
                        <SelectItem value="bottom">↓ Bottom</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Edge Color</label>
                    <Select
                      value={config.edgeColor}
                      onValueChange={(value) => setConfig({...config, edgeColor: value as EdgeColor})}
                      disabled={config.edgePosition === 'none'}
                    >
                      <SelectTrigger className="text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="purple">🟣 Purple</SelectItem>
                        <SelectItem value="blue">🔵 Blue</SelectItem>
                        <SelectItem value="cyan">🔷 Cyan</SelectItem>
                        <SelectItem value="green">🟢 Green</SelectItem>
                        <SelectItem value="orange">🟠 Orange</SelectItem>
                        <SelectItem value="pink">🩷 Pink</SelectItem>
                        <SelectItem value="red">🔴 Red</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium mb-1">Content</label>
                    <Input
                      value={config.content}
                      onChange={(e) => setConfig({...config, content: e.target.value})}
                      placeholder="Card content..."
                      className="text-xs"
                    />
                  </div>
                </div>
              </div>

              {/* Right: Live Preview on grid background */}
              <div className="flex items-center justify-center">
                <div
                  className={cn(
                    "transition-all duration-200",
                    // Apply outer glow effect if selected
                    config.glowType === 'outer' && config.glowColor !== 'none' &&
                    `shadow-[0_0_30px_${config.glowColor}-500/80,_0_0_60px_${config.glowColor}-500/40]`
                  )}
                >
                  <Card
                    blur={config.blur}
                    transparency={config.transparency}
                    glassTint={config.glassTint}
                    glowColor={config.glowType === 'inner' ? config.glowColor : 'none'}
                    edgePosition={config.edgePosition}
                    edgeColor={config.edgeColor}
                    size={config.size}
                    className={cn(
                      // Apply inner glow effect with enhanced visibility
                      config.glowType === 'inner' && config.glowColor !== 'none' && [
                        `bg-${config.glowColor}-500/40 border border-${config.glowColor}-500`,
                        `shadow-[inset_0_0_20px_${config.glowColor}-500/60]`
                      ]
                    )}
                  >
                    <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Glass Card</h4>
                    <p className="text-gray-700 dark:text-gray-300 text-sm">
                      {config.content}
                    </p>
                  </Card>
                </div>
              </div>
            </div>
          </Card>

          {/* Generated Code - Full Width Bottom */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Generated Code</h3>
            <CodeDisplay
              code={generateCode(config)}
              showLineNumbers
            />
          </Card>
        </div>
      )}
    </div>
  );
};