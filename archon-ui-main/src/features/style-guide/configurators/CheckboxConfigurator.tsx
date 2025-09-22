import React, { useState } from "react";
import { Checkbox, type CheckboxColor } from "../../../features/ui/primitives/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "../../../features/ui/primitives/select";
import { ConfiguratorCard } from "../shared/ConfiguratorCard";
import { Label } from "../../../features/ui/primitives/label";

const colorOptions = [
  { value: "purple", label: "Purple" },
  { value: "blue", label: "Blue" },
  { value: "green", label: "Green" },
  { value: "pink", label: "Pink" },
  { value: "orange", label: "Orange" },
  { value: "cyan", label: "Cyan" },
];

const stateOptions = [
  { value: "unchecked", label: "Unchecked" },
  { value: "checked", label: "Checked" },
  { value: "indeterminate", label: "Indeterminate" },
];

/**
 * 🤖 AI CONTEXT: Checkbox Configurator
 *
 * CONFIGURATION OPTIONS:
 * 1. COLOR - Six accent colors with neon glow
 *    - Each color has associated glow effects
 *    - Glow intensity increases on check
 *
 * 2. STATE - Three checkbox states
 *    - Unchecked: Empty glass box
 *    - Checked: Check icon with glow
 *    - Indeterminate: Minus icon (partial selection)
 *
 * 3. LABEL - Optional label positioning
 *    - Can be placed left or right
 *    - Click target includes label
 *
 * 4. DISABLED - Interactive state control
 */
export function CheckboxConfigurator() {
  const [color, setColor] = useState<CheckboxColor>("cyan");
  const [state, setState] = useState<"unchecked" | "checked" | "indeterminate">("checked");
  const [disabled, setDisabled] = useState(false);
  const [showLabel, setShowLabel] = useState(true);

  const getCheckedState = () => {
    if (state === "indeterminate") return "indeterminate";
    return state === "checked";
  };

  const generateCode = () => {
    const props: string[] = [];

    if (color !== "cyan") props.push(`color="${color}"`);
    if (state === "indeterminate") {
      props.push(`indeterminate`);
      props.push(`checked="indeterminate"`);
    } else if (state === "checked") {
      props.push(`checked={true}`);
    } else {
      props.push(`checked={false}`);
    }
    if (disabled) props.push(`disabled`);
    props.push(`onCheckedChange={(checked) => console.log(checked)}`);

    const checkboxCode = `<Checkbox
  ${props.join("\n  ")}
/>`;

    if (showLabel) {
      return `import { Checkbox } from "@/features/ui/primitives/checkbox";
import { Label } from "@/features/ui/primitives/label";

/**
 * 🤖 AI CONTEXT: Checkbox with Label
 *
 * STATE: ${state}
 * COLOR: ${color} - Neon glow effect
 *
 * GLASS PROPERTIES:
 * - Transparency: bg-white/10 backdrop-blur
 * - Glow: ${color} shadow on checked state
 * - Animation: Zoom in/out on check
 * ${state === "indeterminate" ? "* Indeterminate: Partial selection state" : ""}
 */

<div className="flex items-center space-x-2">
  <Checkbox
    id="terms"
    ${props.join("\n    ")}
  />
  <Label
    htmlFor="terms"
    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
  >
    Accept terms and conditions
  </Label>
</div>`;
    }

    return `import { Checkbox } from "@/features/ui/primitives/checkbox";

/**
 * 🤖 AI CONTEXT: Standalone Checkbox
 *
 * STATE: ${state}
 * COLOR: ${color} - Neon glow effect
 *
 * GLASS PROPERTIES:
 * - Transparency: bg-white/10 backdrop-blur
 * - Glow: ${color} shadow on checked state
 * - Animation: Zoom in/out on check
 * ${state === "indeterminate" ? "* Indeterminate: Partial selection state" : ""}
 */

${checkboxCode}`;
  };

  return (
    <ConfiguratorCard
      title="Checkbox"
      description="Checkboxes with neon glow effects and indeterminate state support"
      code={generateCode()}
    >
      <div className="space-y-6">
        {/* Preview */}
        <div className="flex items-center justify-center p-8 rounded-lg bg-black/5 dark:bg-white/5">
          {showLabel ? (
            <div className="flex items-center space-x-2">
              <Checkbox
                id="preview"
                color={color}
                checked={getCheckedState()}
                indeterminate={state === "indeterminate"}
                disabled={disabled}
                onCheckedChange={() => {
                  // Cycle through states
                  if (state === "unchecked") setState("checked");
                  else if (state === "checked") setState("indeterminate");
                  else setState("unchecked");
                }}
              />
              <Label
                htmlFor="preview"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
              >
                Accept terms and conditions
              </Label>
            </div>
          ) : (
            <Checkbox
              color={color}
              checked={getCheckedState()}
              indeterminate={state === "indeterminate"}
              disabled={disabled}
              onCheckedChange={() => {
                // Cycle through states
                if (state === "unchecked") setState("checked");
                else if (state === "checked") setState("indeterminate");
                else setState("unchecked");
              }}
            />
          )}
        </div>

        {/* Configuration */}
        <div className="grid grid-cols-2 gap-4">
          {/* Color */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Color
            </label>
            <Select value={color} onValueChange={(v) => setColor(v as CheckboxColor)}>
              <SelectTrigger color={color}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent color={color}>
                {colorOptions.map(option => (
                  <SelectItem key={option.value} value={option.value} color={color}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* State */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              State
            </label>
            <Select value={state} onValueChange={(v) => setState(v as any)}>
              <SelectTrigger color={color}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent color={color}>
                {stateOptions.map(option => (
                  <SelectItem key={option.value} value={option.value} color={color}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Label */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Label
            </label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <Checkbox
                  color={color}
                  checked={showLabel}
                  onCheckedChange={setShowLabel}
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">Show Label</span>
              </label>
            </div>
          </div>

          {/* Disabled */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              State
            </label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <Checkbox
                  color={color}
                  checked={disabled}
                  onCheckedChange={setDisabled}
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">Disabled</span>
              </label>
            </div>
          </div>
        </div>

        {/* Examples */}
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Examples</h4>

          {/* Color Grid */}
          <div className="space-y-2">
            <p className="text-xs text-gray-500 dark:text-gray-400">All Colors</p>
            <div className="flex gap-3">
              {colorOptions.map(opt => (
                <Checkbox
                  key={opt.value}
                  color={opt.value as CheckboxColor}
                  defaultChecked
                />
              ))}
            </div>
          </div>

          {/* States */}
          <div className="space-y-2">
            <p className="text-xs text-gray-500 dark:text-gray-400">States</p>
            <div className="flex gap-6">
              <div className="flex items-center gap-2">
                <Checkbox color={color} checked={false} />
                <span className="text-xs text-gray-500">Unchecked</span>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox color={color} checked={true} />
                <span className="text-xs text-gray-500">Checked</span>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox color={color} indeterminate />
                <span className="text-xs text-gray-500">Indeterminate</span>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox color={color} checked={true} disabled />
                <span className="text-xs text-gray-500">Disabled</span>
              </div>
            </div>
          </div>

          {/* List Example */}
          <div className="space-y-2">
            <p className="text-xs text-gray-500 dark:text-gray-400">List Example</p>
            <div className="space-y-2 p-4 rounded-lg bg-black/5 dark:bg-white/5">
              <div className="flex items-center space-x-2">
                <Checkbox id="option1" color={color} defaultChecked />
                <Label htmlFor="option1" className="text-sm cursor-pointer">Enable notifications</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="option2" color={color} />
                <Label htmlFor="option2" className="text-sm cursor-pointer">Show preview pane</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="option3" color={color} defaultChecked />
                <Label htmlFor="option3" className="text-sm cursor-pointer">Auto-save drafts</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="option4" color={color} indeterminate />
                <Label htmlFor="option4" className="text-sm cursor-pointer">Sync across devices (partial)</Label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ConfiguratorCard>
  );
}