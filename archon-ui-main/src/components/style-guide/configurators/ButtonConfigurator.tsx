import { useState } from 'react';
import { Button } from '@/features/ui/primitives/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/features/ui/primitives/select';
import { Switch } from '@/features/ui/primitives/switch';
import { Input } from '@/features/ui/primitives/input';
import { LivePreview } from '../shared/LivePreview';
import { CodeDisplay } from '../shared/CodeDisplay';
import { ConfigPanel } from '../shared/ConfigPanel';
import { ConfigRow } from '../shared/ConfigRow';
import { Loader2, Download, Eye, Code } from 'lucide-react';
import type { ButtonVariant, ButtonSize } from '../types';

interface ButtonConfig {
  variant: ButtonVariant;
  size: ButtonSize;
  loading: boolean;
  disabled: boolean;
  withIcon: boolean;
  text: string;
}

export const ButtonConfigurator = () => {
  const [config, setConfig] = useState<ButtonConfig>({
    variant: 'default',
    size: 'default',
    loading: false,
    disabled: false,
    withIcon: false,
    text: 'Click me'
  });
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');

  const generateCode = (config: ButtonConfig) => {
    const imports = [`import { Button } from '@/features/ui/primitives/button';`];

    if (config.loading) {
      imports.push(`import { Loader2 } from 'lucide-react';`);
    }
    if (config.withIcon) {
      imports.push(`import { Download } from 'lucide-react';`);
    }

    const aiContext = `/**
 * 🤖 AI CONTEXT: Button Component
 *
 * VARIANT DECISION TREE:
 * - default: Primary actions, main CTAs, submit buttons
 * - destructive: Delete, remove, cancel dangerous operations
 * - outline: Secondary actions, alternative options
 * - ghost: Tertiary actions, minimal emphasis
 * - link: Navigation, text-only actions
 * - cyan: Special emphasis, Tron-themed primary
 * - knowledge: Knowledge base specific actions
 *
 * SIZE GUIDELINES:
 * - xs: Inline actions, table cells
 * - sm: Dense UI, secondary actions
 * - default: Most use cases
 * - lg: Primary CTAs, hero sections
 * - icon: Icon-only buttons
 */`;

    const props: string[] = [];
    if (config.variant !== 'default') props.push(`variant="${config.variant}"`);
    if (config.size !== 'default') props.push(`size="${config.size}"`);
    if (config.loading) props.push(`loading={true}`);
    if (config.disabled) props.push(`disabled={true}`);

    const content = config.loading
      ? `<>\n        <Loader2 className="mr-2 h-4 w-4 animate-spin" />\n        ${config.text}\n      </>`
      : config.withIcon
      ? `<>\n        <Download className="mr-2 h-4 w-4" />\n        ${config.text}\n      </>`
      : config.text;

    const component = `export const MyButton = () => {
  return (
    <Button${props.length > 0 ? '\n      ' + props.join('\n      ') : ''}>
      ${content}
    </Button>
  );
};`;

    return `${imports.join('\n')}\n\n${aiContext}\n\n${component}`;
  };

  return (
    <div className="grid grid-cols-4 gap-6 h-full">
      {/* LEFT: Configuration Panel (1/4 width) */}
      <div className="col-span-1">
        <ConfigPanel title="Button Configuration">
          <div className="space-y-3">
            <ConfigRow label="Variant">
              <Select
                value={config.variant}
                onValueChange={(value) => setConfig({...config, variant: value as ButtonVariant})}
              >
                <SelectTrigger className="w-24 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="default">Default</SelectItem>
                  <SelectItem value="destructive">Destructive</SelectItem>
                  <SelectItem value="outline">Outline</SelectItem>
                  <SelectItem value="ghost">Ghost</SelectItem>
                  <SelectItem value="link">Link</SelectItem>
                  <SelectItem value="cyan">Cyan</SelectItem>
                  <SelectItem value="knowledge">Knowledge</SelectItem>
                </SelectContent>
              </Select>
            </ConfigRow>

            <ConfigRow label="Size">
              <Select
                value={config.size}
                onValueChange={(value) => setConfig({...config, size: value as ButtonSize})}
              >
                <SelectTrigger className="w-24 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="xs">XS</SelectItem>
                  <SelectItem value="sm">SM</SelectItem>
                  <SelectItem value="default">Default</SelectItem>
                  <SelectItem value="lg">LG</SelectItem>
                  <SelectItem value="icon">Icon</SelectItem>
                </SelectContent>
              </Select>
            </ConfigRow>

            <ConfigRow label="Loading">
              <Switch
                checked={config.loading}
                onCheckedChange={(loading) => setConfig({...config, loading})}
              />
            </ConfigRow>

            <ConfigRow label="Disabled">
              <Switch
                checked={config.disabled}
                onCheckedChange={(disabled) => setConfig({...config, disabled})}
              />
            </ConfigRow>

            <ConfigRow label="With Icon">
              <Switch
                checked={config.withIcon}
                onCheckedChange={(withIcon) => setConfig({...config, withIcon})}
              />
            </ConfigRow>

            {config.size !== 'icon' && (
              <ConfigRow label="Text">
                <Input
                  value={config.text}
                  onChange={(e) => setConfig({...config, text: e.target.value})}
                  placeholder="Button text..."
                  className="w-24 text-xs"
                />
              </ConfigRow>
            )}
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
            <Button
              variant={config.variant}
              size={config.size}
              loading={config.loading}
              disabled={config.disabled}
            >
              {config.loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {!config.loading && config.withIcon && <Download className="mr-2 h-4 w-4" />}
              {config.size !== 'icon' && config.text}
              {config.size === 'icon' && !config.loading && <Download className="h-4 w-4" />}
            </Button>
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