import { useState } from 'react';
import { Switch } from '@/features/ui/primitives/switch';
import { Button } from '@/features/ui/primitives/button';
import { Label } from '@/features/ui/primitives/label';
import { RadioGroup, RadioGroupItem } from '@/features/ui/primitives/radio-group';
import { LivePreview } from '../shared/LivePreview';
import { CodeDisplay } from '../shared/CodeDisplay';
import { ConfigPanel } from '../shared/ConfigPanel';
import { Eye, Code } from 'lucide-react';
import type { LabelPosition } from '../types';

interface ToggleConfig {
  disabled: boolean;
  size: 'sm' | 'default' | 'lg';
  labelPosition: LabelPosition;
  labelText: string;
}

export const ToggleConfigurator = () => {
  const [config, setConfig] = useState<ToggleConfig>({
    disabled: false,
    size: 'default',
    labelPosition: 'right',
    labelText: 'Enable notifications'
  });
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [toggleState, setToggleState] = useState(false);

  const generateCode = (_config: ToggleConfig) => {
    const imports = `import { Switch } from '@/features/ui/primitives/switch';
import { Label } from '@/features/ui/primitives/label';`;

    const aiContext = `/**
 * 🤖 AI CONTEXT: Switch Toggle Component
 *
 * PURPOSE: Binary on/off controls with accessible labeling
 * WHEN TO USE: Settings, preferences, feature toggles, boolean states
 * WHEN NOT TO USE: Multiple options (use RadioGroup), momentary actions (use Button)
 */`;

    return `${imports}\n\n${aiContext}\n\n// Toggle component code here...`;
  };

  const layoutClasses = {
    left: 'flex-row-reverse',
    right: 'flex-row',
    top: 'flex-col',
    bottom: 'flex-col-reverse'
  };

  const gapClasses = {
    left: 'gap-3',
    right: 'gap-3',
    top: 'gap-2',
    bottom: 'gap-2'
  };

  return (
    <div className="grid grid-cols-4 gap-6 h-full">
      {/* LEFT: Configuration Panel (1/4 width) */}
      <div className="col-span-1">
        <ConfigPanel title="Switch Toggle Configuration">
          <div className="space-y-4">
            {/* Label Position */}
            <div>
              <Label className="text-sm">Label Position</Label>
              <RadioGroup
                value={config.labelPosition}
                onValueChange={(value) => setConfig({...config, labelPosition: value as LabelPosition})}
              >
                <div className="grid grid-cols-2 gap-2">
                  {['left', 'right', 'top', 'bottom'].map(position => (
                    <div key={position} className="flex items-center space-x-2">
                      <RadioGroupItem value={position} id={`position-${position}`} />
                      <Label htmlFor={`position-${position}`} className="capitalize text-xs">
                        {position}
                      </Label>
                    </div>
                  ))}
                </div>
              </RadioGroup>
            </div>

            {/* States */}
            <div className="flex items-center justify-between">
              <Label htmlFor="disabled-toggle" className="text-sm">Disabled State</Label>
              <Switch
                id="disabled-toggle"
                checked={config.disabled}
                onCheckedChange={(disabled) => setConfig({...config, disabled})}
              />
            </div>

            {/* Label Text */}
            <div>
              <Label htmlFor="label-text" className="text-sm">Label Text</Label>
              <input
                id="label-text"
                type="text"
                value={config.labelText}
                onChange={(e) => setConfig({...config, labelText: e.target.value})}
                className="w-full mt-1 px-3 py-2 border rounded-md dark:bg-gray-800 text-sm"
              />
            </div>
          </div>

          {/* Preview/Code Tabs INSIDE configurator */}
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
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
            <div className={`flex ${layoutClasses[config.labelPosition]} ${gapClasses[config.labelPosition]} items-center`}>
              {(config.labelPosition === 'top' || config.labelPosition === 'left') ? (
                <>
                  <Label htmlFor="preview-toggle">
                    {config.labelText}
                  </Label>
                  <Switch
                    id="preview-toggle"
                    checked={toggleState}
                    onCheckedChange={setToggleState}
                    disabled={config.disabled}
                  />
                </>
              ) : (
                <>
                  <Switch
                    id="preview-toggle"
                    checked={toggleState}
                    onCheckedChange={setToggleState}
                    disabled={config.disabled}
                  />
                  <Label htmlFor="preview-toggle">
                    {config.labelText}
                  </Label>
                </>
              )}
            </div>
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