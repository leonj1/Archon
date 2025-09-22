import { useState } from 'react';
import { Input } from '@/features/ui/primitives/input';
import { Button } from '@/features/ui/primitives/button';
import { Label } from '@/features/ui/primitives/label';
import { Switch } from '@/features/ui/primitives/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/features/ui/primitives/select';
import { LivePreview } from '../shared/LivePreview';
import { CodeDisplay } from '../shared/CodeDisplay';
import { ConfigPanel } from '../shared/ConfigPanel';
import { Eye, Code } from 'lucide-react';
import type { InputType } from '../types';

interface FormConfig {
  error: boolean;
  disabled: boolean;
  placeholder: string;
  inputType: InputType;
}

export const FormConfigurator = () => {
  const [config, setConfig] = useState<FormConfig>({
    error: false,
    disabled: false,
    placeholder: 'Enter your text...',
    inputType: 'text'
  });
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');

  const generateCode = (config: FormConfig) => {
    const imports = `import { Input } from '@/features/ui/primitives/input';
import { Label } from '@/features/ui/primitives/label';
import { Button } from '@/features/ui/primitives/button';`;

    const aiContext = `/**
 * 🤖 AI CONTEXT: Form Input Component
 *
 * PURPOSE: Text input with glass morphism styling and validation states
 * WHEN TO USE: Forms, search bars, data entry fields
 * WHEN NOT TO USE: Large text content (use textarea), complex selections (use select)
 *
 * INPUT TYPE GUIDELINES:
 * - text: General text input, names, titles
 * - email: Email addresses (includes validation)
 * - password: Passwords (masks input)
 * - number: Numeric values (shows number pad on mobile)
 *
 * ERROR STATE:
 * - Use when validation fails
 * - Shows red border and focus ring
 * - Pair with error message below input
 *
 * DISABLED STATE:
 * - Use when input is temporarily unavailable
 * - Shows reduced opacity and prevents interaction
 * - Consider using readonly for permanent restrictions
 */`;

    const props: string[] = [];
    if (config.inputType !== 'text') props.push(`type="${config.inputType}"`);
    if (config.error) props.push(`error={true}`);
    if (config.disabled) props.push(`disabled={true}`);
    if (config.placeholder) props.push(`placeholder="${config.placeholder}"`);

    const component = `export const MyForm = () => {
  const [value, setValue] = useState('');

  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="example-input">
          ${config.inputType === 'email' ? 'Email Address' :
            config.inputType === 'password' ? 'Password' :
            config.inputType === 'number' ? 'Number' :
            'Text Input'}
        </Label>
        <Input
          id="example-input"
          value={value}
          onChange={(e) => setValue(e.target.value)}${props.length > 0 ? '\n          ' + props.join('\n          ') : ''}
        />
        ${config.error ? `<p className="text-sm text-red-600 dark:text-red-400 mt-1">
          This field is required
        </p>` : ''}
      </div>

      <Button type="submit">
        Submit
      </Button>
    </div>
  );
};`;

    return `${imports}\n\n${aiContext}\n\n${component}`;
  };

  return (
    <div className="grid grid-cols-4 gap-6 h-full">
      {/* LEFT: Configuration Panel (1/4 width) */}
      <div className="col-span-1">
        <ConfigPanel title="Form Input Configuration">
          <div className="space-y-4">
            {/* Input Type */}
            <div>
              <Label>Input Type</Label>
              <Select
                value={config.inputType}
                onValueChange={(value) => setConfig({...config, inputType: value as InputType})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="text">Text</SelectItem>
                  <SelectItem value="email">Email</SelectItem>
                  <SelectItem value="password">Password</SelectItem>
                  <SelectItem value="number">Number</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* States */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="error-state" className="text-sm">Error State</Label>
                <Switch
                  id="error-state"
                  checked={config.error}
                  onCheckedChange={(error) => setConfig({...config, error})}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="disabled-state" className="text-sm">Disabled</Label>
                <Switch
                  id="disabled-state"
                  checked={config.disabled}
                  onCheckedChange={(disabled) => setConfig({...config, disabled})}
                />
              </div>
            </div>

            {/* Placeholder */}
            <div>
              <Label htmlFor="placeholder-text" className="text-sm">Placeholder Text</Label>
              <Input
                id="placeholder-text"
                value={config.placeholder}
                onChange={(e) => setConfig({...config, placeholder: e.target.value})}
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
            <div className="space-y-4 w-full max-w-sm">
              <div>
                <Label htmlFor="preview-input">
                  {config.inputType === 'email' ? 'Email Address' :
                   config.inputType === 'password' ? 'Password' :
                   config.inputType === 'number' ? 'Number' :
                   'Text Input'}
                </Label>
                <Input
                  id="preview-input"
                  type={config.inputType}
                  placeholder={config.placeholder}
                  error={config.error}
                  disabled={config.disabled}
                />
                {config.error && (
                  <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                    This field is required
                  </p>
                )}
              </div>

              <Button type="submit" disabled={config.disabled}>
                Submit
              </Button>
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