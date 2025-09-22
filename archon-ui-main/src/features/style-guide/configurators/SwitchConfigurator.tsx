import { useState } from "react";
import {
  Moon, Sun, Power, Wifi, WifiOff,
  Volume2, VolumeX, Bell, BellOff,
  Eye, EyeOff, Lock, Unlock
} from "lucide-react";
import { Switch, type SwitchSize, type SwitchColor } from "../../../features/ui/primitives/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "../../../features/ui/primitives/select";
import { ConfiguratorCard } from "../shared/ConfiguratorCard";

const sizeOptions = [
  { value: "sm", label: "Small (16px)" },
  { value: "md", label: "Medium (24px)" },
  { value: "lg", label: "Large (32px)" },
];

const colorOptions = [
  { value: "purple", label: "Purple" },
  { value: "blue", label: "Blue" },
  { value: "green", label: "Green" },
  { value: "pink", label: "Pink" },
  { value: "orange", label: "Orange" },
  { value: "cyan", label: "Cyan" },
];

const iconOptions = [
  { value: "none", label: "No Icon", iconOn: null, iconOff: null },
  { value: "theme", label: "Theme", iconOn: <Moon className="w-full h-full" />, iconOff: <Sun className="w-full h-full" /> },
  { value: "power", label: "Power", iconOn: <Power className="w-full h-full" />, iconOff: <Power className="w-full h-full" /> },
  { value: "wifi", label: "WiFi", iconOn: <Wifi className="w-full h-full" />, iconOff: <WifiOff className="w-full h-full" /> },
  { value: "sound", label: "Sound", iconOn: <Volume2 className="w-full h-full" />, iconOff: <VolumeX className="w-full h-full" /> },
  { value: "notifications", label: "Notifications", iconOn: <Bell className="w-full h-full" />, iconOff: <BellOff className="w-full h-full" /> },
  { value: "visibility", label: "Visibility", iconOn: <Eye className="w-full h-full" />, iconOff: <EyeOff className="w-full h-full" /> },
  { value: "lock", label: "Lock", iconOn: <Lock className="w-full h-full" />, iconOff: <Unlock className="w-full h-full" /> },
];

/**
 * 🤖 AI CONTEXT: Switch Configurator
 *
 * CONFIGURATION OPTIONS:
 * 1. SIZE - Three variants for different use cases
 *    - Small: Clean minimal switches for dense UIs
 *    - Medium: Standard switches with optional icons
 *    - Large: Feature toggles with prominent icons
 *
 * 2. COLOR - Six accent colors matching the design system
 *    - Each color has associated glow effects
 *
 * 3. ICONS - Dynamic icon switching
 *    - Different icons for on/off states
 *    - Icons scale based on size variant
 *
 * 4. STATE - Interactive toggle preview
 *    - Live preview updates as configuration changes
 */
export function SwitchConfigurator() {
  const [checked, setChecked] = useState(false);
  const [size, setSize] = useState<SwitchSize>("lg");
  const [color, setColor] = useState<SwitchColor>("cyan");
  const [iconOption, setIconOption] = useState("theme");
  const [disabled, setDisabled] = useState(false);
  const [transparency, setTransparency] = useState("medium");
  const [glowIntensity, setGlowIntensity] = useState("normal");
  const [iconColorSync, setIconColorSync] = useState(true);

  const selectedIcon = iconOptions.find(opt => opt.value === iconOption);

  const generateCode = () => {
    const imports = ["Switch"];
    const props: string[] = [];

    if (size !== "md") props.push(`size="${size}"`);
    if (color !== "cyan") props.push(`color="${color}"`);
    if (selectedIcon?.iconOn && selectedIcon?.iconOff) {
      if (selectedIcon.value === "theme") {
        imports.push("Moon", "Sun");
        props.push(`iconOn={<Moon className="w-full h-full" />}`);
        props.push(`iconOff={<Sun className="w-full h-full" />}`);
      } else if (selectedIcon.value === "power") {
        imports.push("Power");
        props.push(`icon={<Power className="w-full h-full" />}`);
      } else if (selectedIcon.value === "wifi") {
        imports.push("Wifi", "WifiOff");
        props.push(`iconOn={<Wifi className="w-full h-full" />}`);
        props.push(`iconOff={<WifiOff className="w-full h-full" />}`);
      }
      // Add other icon cases as needed
    }
    if (disabled) props.push(`disabled`);
    props.push(`checked={checked}`);
    props.push(`onCheckedChange={setChecked}`);

    const iconImports = imports.filter(i => i !== "Switch").length > 0
      ? `import { ${imports.filter(i => i !== "Switch").join(", ")} } from "lucide-react";\n`
      : "";

    return `${iconImports}import { Switch } from "@/features/ui/primitives/switch";

/**
 * 🤖 AI CONTEXT: Switch Component
 *
 * SIZE: ${size} - ${sizeOptions.find(s => s.value === size)?.label}
 * COLOR: ${color} - Neon glow effect
 * ICONS: ${iconOption === "none" ? "No icons" : `${selectedIcon?.label} icons`}
 * ${size === "sm" ? "* Note: Small switches don't display icons" : ""}
 *
 * GLASS PROPERTIES:
 * - Transparency: bg-white/10 backdrop-blur
 * - Glow: ${color} shadow on checked state
 * - Transition: 500ms cubic-bezier animation
 */

<Switch
  ${props.join("\n  ")}
/>`;
  };

  return (
    <ConfiguratorCard
      title="Switch"
      description="Toggle switches with size variants, icons, and neon glow effects"
      code={generateCode()}
    >
      <div className="space-y-6">
        {/* Preview */}
        <div className="flex items-center justify-center p-8 rounded-lg bg-black/5 dark:bg-white/5">
          <Switch
            size={size}
            color={color}
            iconOn={selectedIcon?.iconOn}
            iconOff={selectedIcon?.iconOff}
            checked={checked}
            onCheckedChange={setChecked}
            disabled={disabled}
          />
        </div>

        {/* Configuration */}
        <div className="grid grid-cols-2 gap-4">
          {/* Size */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Size
            </label>
            <Select value={size} onValueChange={(v) => setSize(v as SwitchSize)}>
              <SelectTrigger color={color}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent color={color}>
                {sizeOptions.map(option => (
                  <SelectItem key={option.value} value={option.value} color={color}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Color */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Color
            </label>
            <Select value={color} onValueChange={(v) => setColor(v as SwitchColor)}>
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

          {/* Icon */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Icon {size === "sm" && "(Not shown for small)"}
            </label>
            <Select value={iconOption} onValueChange={setIconOption}>
              <SelectTrigger color={color}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent color={color}>
                {iconOptions.map(option => (
                  <SelectItem key={option.value} value={option.value} color={color}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Transparency */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Transparency
            </label>
            <Select value={transparency} onValueChange={setTransparency}>
              <SelectTrigger color={color}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent color={color}>
                <SelectItem value="low" color={color}>Low (More opaque)</SelectItem>
                <SelectItem value="medium" color={color}>Medium</SelectItem>
                <SelectItem value="high" color={color}>High (More transparent)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Glow Intensity */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Glow Intensity
            </label>
            <Select value={glowIntensity} onValueChange={setGlowIntensity}>
              <SelectTrigger color={color}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent color={color}>
                <SelectItem value="none" color={color}>None</SelectItem>
                <SelectItem value="subtle" color={color}>Subtle</SelectItem>
                <SelectItem value="normal" color={color}>Normal</SelectItem>
                <SelectItem value="intense" color={color}>Intense</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* State & Icon Color */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Options
            </label>
            <div className="flex flex-col gap-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={disabled}
                  onChange={(e) => setDisabled(e.target.checked)}
                  className="sr-only"
                />
                <Switch
                  size="sm"
                  color={color}
                  checked={disabled}
                  onCheckedChange={setDisabled}
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">Disabled</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={iconColorSync}
                  onChange={(e) => setIconColorSync(e.target.checked)}
                  className="sr-only"
                />
                <Switch
                  size="sm"
                  color={color}
                  checked={iconColorSync}
                  onCheckedChange={setIconColorSync}
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">Icon color syncs</span>
              </label>
            </div>
          </div>
        </div>

        {/* Examples */}
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Examples</h4>
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <p className="text-xs text-gray-500 dark:text-gray-400">Small</p>
              <div className="flex gap-2">
                {colorOptions.slice(0, 3).map(opt => (
                  <Switch
                    key={opt.value}
                    size="sm"
                    color={opt.value as SwitchColor}
                    defaultChecked
                  />
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <p className="text-xs text-gray-500 dark:text-gray-400">Medium with Icons</p>
              <div className="flex gap-2">
                <Switch size="md" color="purple" iconOn={<Moon />} iconOff={<Sun />} defaultChecked />
                <Switch size="md" color="green" icon={<Wifi />} />
              </div>
            </div>
            <div className="space-y-2">
              <p className="text-xs text-gray-500 dark:text-gray-400">Large Feature</p>
              <div className="flex gap-2">
                <Switch
                  size="lg"
                  color="blue"
                  iconOn={<Power />}
                  iconOff={<Power />}
                  defaultChecked
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </ConfiguratorCard>
  );
}