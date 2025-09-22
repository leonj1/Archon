import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/features/ui/primitives/select';
import { Input } from '@/features/ui/primitives/input';
import { Button } from '@/features/ui/primitives/button';
import { LivePreview } from '../shared/LivePreview';
import { CodeDisplay } from '../shared/CodeDisplay';
import { ConfigPanel } from '../shared/ConfigPanel';
import { ConfigRow } from '../shared/ConfigRow';
import { Eye, Code } from 'lucide-react';
import type { GlowColor, EdgePosition, EdgeColor, CardSize, Transparency, BlurLevel, GlassTint } from '../types';

interface GlassCardConfig {
  blur: BlurLevel;
  transparency: Transparency;
  glassTint: GlassTint;
  glowColor: GlowColor;
  edgePosition: EdgePosition;
  edgeColor: EdgeColor;
  size: CardSize;
  content: string;
}

export const GlassCardConfigurator = () => {
  const [config, setConfig] = useState<GlassCardConfig>({
    blur: 'xl',  // Standard glass (3px) - subtle effect
    transparency: 'light',  // 3% opacity for true glass
    glassTint: 'none',
    glowColor: 'none',
    edgePosition: 'none',
    edgeColor: 'cyan',
    size: 'lg',
    content: 'Your content here'
  });
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');

  const generateCode = (config: GlassCardConfig) => {
    const imports = `import { Card } from '@/features/ui/primitives/card';`;

    const aiContext = `/**
 * 🤖 AI CONTEXT: Glass Card Component
 *
 * GLASS PROPERTIES for true glassmorphism:
 *
 * 1. TRANSPARENCY - How much you can see through the glass
 *    - clear: Almost invisible (0.01 opacity)
 *    - light: Subtle frosting (0.03 opacity) ← BEST FOR TRUE GLASS
 *    - medium: Standard glass (0.05 opacity)
 *    - frosted: Heavy frosting (0.08 opacity)
 *    - solid: Maximum opacity (0.12 opacity)
 *
 * 2. GLASS TINT - Adds color to the glass itself
 *    - none: Pure transparent
 *    - purple/blue/cyan/green/orange/pink/red: Colored glass
 *
 * 3. GLOW EFFECTS - Choose ONE:
 *    a) glowColor - Full perimeter neon backlight
 *       - none: No glow
 *       - purple/blue/cyan/green/orange/pink/red: Neon glow
 *
 *    b) edgePosition + edgeColor - Single edge accent (like original cards!)
 *       - edgePosition: top/left/right/bottom
 *       - edgeColor: purple/blue/cyan/green/orange/pink/red
 *
 * USAGE PATTERNS:
 * - Default glass: transparency="light" blur="xl"
 * - Knowledge cards: edgePosition="top" edgeColor="purple"
 * - Task cards: edgePosition="left" edgeColor based on priority
 * - Featured content: glowColor="purple" (full perimeter)
 * - Subtle containers: transparency="clear" glassTint="none"
 *
 * DECISION TREE:
 * - Navigation/headers → edgePosition="top"
 * - Sidebars/lists → edgePosition="left"
 * - Actions/CTAs → edgePosition="right"
 * - Status/footers → edgePosition="bottom"
 * - Featured/selected → glowColor (full perimeter)
 */`;

    const props: string[] = [];
    if (config.blur !== 'xl') props.push(`blur="${config.blur}"`);
    if (config.transparency !== 'medium') props.push(`transparency="${config.transparency}"`);
    if (config.glassTint !== 'none') props.push(`glassTint="${config.glassTint}"`);
    if (config.glowColor !== 'none') props.push(`glowColor="${config.glowColor}"`);
    if (config.edgePosition !== 'none') props.push(`edgePosition="${config.edgePosition}"`);
    if (config.edgePosition !== 'none' && config.edgeColor !== 'cyan') props.push(`edgeColor="${config.edgeColor}"`);
    if (config.size !== 'md') props.push(`size="${config.size}"`);

    const component = `export const MyCard = ({ children }) => {
  return (
    <Card${props.length > 0 ? '\n      ' + props.join('\n      ') : ''}>
      {children}
    </Card>
  );
};`;

    return `${imports}\n\n${aiContext}\n\n${component}`;
  };

  return (
    <div className="grid grid-cols-4 gap-6 h-full">
      {/* LEFT: Configuration Panel (1/4 width) */}
      <div className="col-span-1">
        <ConfigPanel title="Glass Card Configuration">
          <div className="space-y-3">
            <ConfigRow label="Blur">
              <Select
                value={config.blur}
                onValueChange={(value) => setConfig({...config, blur: value as BlurLevel})}
              >
                <SelectTrigger className="w-24 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None (0px)</SelectItem>
                  <SelectItem value="sm">Minimal (0.5px)</SelectItem>
                  <SelectItem value="md">Subtle (1px)</SelectItem>
                  <SelectItem value="lg">Light (2px)</SelectItem>
                  <SelectItem value="xl">Standard (3px)</SelectItem>
                  <SelectItem value="2xl">Noticeable (5px)</SelectItem>
                  <SelectItem value="3xl">Maximum (8px)</SelectItem>
                </SelectContent>
              </Select>
            </ConfigRow>

            <ConfigRow label="Transparency">
              <Select
                value={config.transparency}
                onValueChange={(value) => setConfig({...config, transparency: value as Transparency})}
              >
                <SelectTrigger className="w-24 text-xs">
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
            </ConfigRow>

            <ConfigRow label="Glass Tint">
              <Select
                value={config.glassTint}
                onValueChange={(value) => setConfig({...config, glassTint: value as GlassTint})}
              >
                <SelectTrigger className="w-24 text-xs">
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
            </ConfigRow>

            <ConfigRow label="Glow Color">
              <Select
                value={config.glowColor}
                onValueChange={(value) => setConfig({...config, glowColor: value as GlowColor})}
                disabled={config.edgePosition !== 'none'}
              >
                <SelectTrigger className="w-24 text-xs">
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
            </ConfigRow>

            <ConfigRow label="Edge Position">
              <Select
                value={config.edgePosition}
                onValueChange={(value) => {
                  setConfig({
                    ...config,
                    edgePosition: value as EdgePosition,
                    glowColor: value !== 'none' ? 'none' : config.glowColor
                  });
                }}
              >
                <SelectTrigger className="w-24 text-xs">
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
            </ConfigRow>

            <ConfigRow label="Edge Color">
              <Select
                value={config.edgeColor}
                onValueChange={(value) => setConfig({...config, edgeColor: value as EdgeColor})}
                disabled={config.edgePosition === 'none'}
              >
                <SelectTrigger className="w-24 text-xs">
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
            </ConfigRow>

            <ConfigRow label="Size">
              <Select
                value={config.size}
                onValueChange={(value) => setConfig({...config, size: value as CardSize})}
              >
                <SelectTrigger className="w-24 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sm">Small</SelectItem>
                  <SelectItem value="md">Medium</SelectItem>
                  <SelectItem value="lg">Large</SelectItem>
                  <SelectItem value="xl">XLarge</SelectItem>
                </SelectContent>
              </Select>
            </ConfigRow>

            <ConfigRow label="Content">
              <Input
                value={config.content}
                onChange={(e) => setConfig({...config, content: e.target.value})}
                placeholder="Card content..."
                className="w-24 text-xs"
              />
            </ConfigRow>
          </div>

          {/* Preview/Code Tabs INSIDE configurator */}
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex gap-2">
              <Button
                size="sm"
                variant={activeTab === 'preview' ? 'default' : 'outline'}
                onClick={() => setActiveTab('preview')}
                className="flex items-center gap-2"
              >
                <Eye className="w-4 h-4" />
                Preview
              </Button>
              <Button
                size="sm"
                variant={activeTab === 'code' ? 'default' : 'outline'}
                onClick={() => setActiveTab('code')}
                className="flex items-center gap-2"
              >
                <Code className="w-4 h-4" />
                Code
              </Button>
            </div>
          </div>
        </ConfigPanel>
      </div>

      {/* RIGHT: Preview or Code Content (3/4 width) */}
      <div className="col-span-3">
        {activeTab === 'preview' ? (
          <LivePreview>
            <Card
              blur={config.blur}
              transparency={config.transparency}
              glassTint={config.glassTint}
              glowColor={config.glowColor}
              edgePosition={config.edgePosition}
              edgeColor={config.edgeColor}
              size={config.size}
            >
              <h4 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Glass Card Example</h4>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                {config.content}
              </p>
              <div className="text-xs text-gray-600 dark:text-gray-400 p-3 bg-white/20 dark:bg-black/20 rounded border border-gray-300 dark:border-gray-600">
                <div><strong>Blur:</strong> {config.blur}</div>
                <div><strong>Transparency:</strong> {config.transparency}</div>
                <div><strong>Glass Tint:</strong> {config.glassTint}</div>
                {config.edgePosition === 'none' ? (
                  <div><strong>Glow Color:</strong> {config.glowColor}</div>
                ) : (
                  <>
                    <div><strong>Edge Position:</strong> {config.edgePosition}</div>
                    <div><strong>Edge Color:</strong> {config.edgeColor}</div>
                  </>
                )}
                <div><strong>Size:</strong> {config.size}</div>
              </div>
            </Card>
          </LivePreview>
        ) : (
          <CodeDisplay
            code={generateCode(config)}
            showLineNumbers
          />
        )}
      </div>
    </div>
  );
};