import { Button } from "@/features/ui/primitives/button";
import { Card } from "@/features/ui/primitives/card";
import { Checkbox } from "@/features/ui/primitives/checkbox";
import { Input } from "@/features/ui/primitives/input";
import { Label } from "@/features/ui/primitives/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/features/ui/primitives/select";
import { Switch } from "@/features/ui/primitives/switch";

export const StaticForms = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Form Elements</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">Form inputs and controls used in the application</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Text Input */}
        <Card className="p-6">
          <h4 className="text-sm font-semibold mb-3 text-gray-900 dark:text-white">Text Input</h4>
          <div className="space-y-3">
            <div>
              <Label htmlFor="example-input">Label</Label>
              <Input id="example-input" placeholder="Enter text..." className="mt-1" />
            </div>
            <div>
              <Label htmlFor="example-disabled">Disabled</Label>
              <Input id="example-disabled" placeholder="Disabled..." disabled className="mt-1" />
            </div>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-3 font-mono">{"<Input />"}</p>
        </Card>

        {/* Textarea */}
        <Card className="p-6">
          <h4 className="text-sm font-semibold mb-3 text-gray-900 dark:text-white">Textarea</h4>
          <div>
            <Label htmlFor="example-textarea">Description</Label>
            <textarea
              id="example-textarea"
              placeholder="Enter description..."
              rows={4}
              className="mt-1 w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white/50 dark:bg-black/30 px-3 py-2 text-sm backdrop-blur-sm focus:border-cyan-500 focus:outline-none"
            />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-3 font-mono">{"<textarea />"}</p>
        </Card>

        {/* Checkbox */}
        <Card className="p-6">
          <h4 className="text-sm font-semibold mb-3 text-gray-900 dark:text-white">Checkbox</h4>
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Checkbox id="check-1" defaultChecked color="cyan" />
              <Label htmlFor="check-1">Checked</Label>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox id="check-2" color="purple" />
              <Label htmlFor="check-2">Unchecked</Label>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox id="check-3" disabled defaultChecked />
              <Label htmlFor="check-3">Disabled</Label>
            </div>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-3 font-mono">{"<Checkbox />"}</p>
        </Card>

        {/* Switch Toggle */}
        <Card className="p-6">
          <h4 className="text-sm font-semibold mb-3 text-gray-900 dark:text-white">Switch Toggle</h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="switch-1">Enable Feature</Label>
              <Switch id="switch-1" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="switch-2">Dark Mode</Label>
              <Switch id="switch-2" />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="switch-3">Disabled</Label>
              <Switch id="switch-3" disabled />
            </div>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-3 font-mono">{"<Switch />"}</p>
        </Card>

        {/* Select Dropdown */}
        <Card className="p-6">
          <h4 className="text-sm font-semibold mb-3 text-gray-900 dark:text-white">Select Dropdown</h4>
          <div className="space-y-3">
            <div>
              <Label htmlFor="select-cyan">Cyan Variant</Label>
              <Select defaultValue="option2">
                <SelectTrigger id="select-cyan" color="cyan" className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="option1">Option 1</SelectItem>
                  <SelectItem value="option2">Option 2</SelectItem>
                  <SelectItem value="option3">Option 3</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="select-purple">Purple Variant</Label>
              <Select defaultValue="option1">
                <SelectTrigger id="select-purple" color="purple" className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="option1">Option 1</SelectItem>
                  <SelectItem value="option2">Option 2</SelectItem>
                  <SelectItem value="option3">Option 3</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-3 font-mono">{"<Select /> with color variants"}</p>
        </Card>

        {/* Submit Button */}
        <Card className="p-6">
          <h4 className="text-sm font-semibold mb-3 text-gray-900 dark:text-white">Form Submission</h4>
          <div className="space-y-3">
            <div>
              <Label htmlFor="form-input">Email</Label>
              <Input id="form-input" type="email" placeholder="email@example.com" className="mt-1" />
            </div>
            <Button variant="default" className="w-full">
              Submit
            </Button>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-3 font-mono">Complete form example</p>
        </Card>
      </div>
    </div>
  );
};
