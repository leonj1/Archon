import { Settings, Palette, Key, Database, Code, Globe } from "lucide-react";
import { CollapsibleSettingsCard } from "@/components/ui/CollapsibleSettingsCard";
import { Switch } from "@/features/ui/primitives/switch";
import { Input } from "@/features/ui/primitives/input";
import { Label } from "@/features/ui/primitives/label";

export const SettingsLayoutExample = () => {
  return (
    <div className="space-y-4">
      {/* Explanation Text */}
      <p className="text-sm text-gray-600 dark:text-gray-400">
        <strong>Use this layout for:</strong> Settings pages, dashboard widgets, grouped
        configuration sections. Two-column responsive grid with collapsible cards.
      </p>

      {/* Bento Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CollapsibleSettingsCard
          title="Feature Toggles"
          icon={Palette}
          accentColor="purple"
          defaultExpanded={true}
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="projects-toggle">Enable Projects</Label>
              <Switch id="projects-toggle" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="style-toggle">Style Guide</Label>
              <Switch id="style-toggle" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="dark-mode">Dark Mode</Label>
              <Switch id="dark-mode" defaultChecked />
            </div>
          </div>
        </CollapsibleSettingsCard>

        <CollapsibleSettingsCard title="API Keys" icon={Key} accentColor="cyan" defaultExpanded={true}>
          <div className="space-y-4">
            <div>
              <Label htmlFor="openai-key">OpenAI API Key</Label>
              <Input
                id="openai-key"
                type="password"
                placeholder="sk-..."
                className="mt-1"
                defaultValue="sk-example-key-hidden"
              />
            </div>
            <div>
              <Label htmlFor="anthropic-key">Anthropic API Key</Label>
              <Input
                id="anthropic-key"
                type="password"
                placeholder="sk-ant-..."
                className="mt-1"
                defaultValue="sk-ant-example-key"
              />
            </div>
          </div>
        </CollapsibleSettingsCard>

        <CollapsibleSettingsCard
          title="Database Settings"
          icon={Database}
          accentColor="blue"
          defaultExpanded={false}
        >
          <div className="space-y-4">
            <div>
              <Label htmlFor="db-url">Database URL</Label>
              <Input
                id="db-url"
                placeholder="postgresql://..."
                className="mt-1"
                defaultValue="postgresql://localhost:5432/archon"
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="auto-backup">Auto Backup</Label>
              <Switch id="auto-backup" />
            </div>
          </div>
        </CollapsibleSettingsCard>

        <CollapsibleSettingsCard
          title="Code Extraction"
          icon={Code}
          accentColor="green"
          defaultExpanded={false}
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="extract-code">Extract Code Examples</Label>
              <Switch id="extract-code" defaultChecked />
            </div>
            <div>
              <Label htmlFor="max-examples">Max Examples per Source</Label>
              <Input
                id="max-examples"
                type="number"
                placeholder="50"
                className="mt-1"
                defaultValue="50"
              />
            </div>
          </div>
        </CollapsibleSettingsCard>

        <CollapsibleSettingsCard
          title="RAG Configuration"
          icon={Settings}
          accentColor="orange"
          defaultExpanded={true}
        >
          <div className="space-y-4">
            <div>
              <Label htmlFor="match-count">Match Count</Label>
              <Input
                id="match-count"
                type="number"
                placeholder="5"
                className="mt-1"
                defaultValue="5"
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="rerank">Enable Reranking</Label>
              <Switch id="rerank" defaultChecked />
            </div>
          </div>
        </CollapsibleSettingsCard>

        <CollapsibleSettingsCard
          title="Crawling Settings"
          icon={Globe}
          accentColor="pink"
          defaultExpanded={false}
        >
          <div className="space-y-4">
            <div>
              <Label htmlFor="max-depth">Max Crawl Depth</Label>
              <Input
                id="max-depth"
                type="number"
                placeholder="3"
                className="mt-1"
                defaultValue="3"
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="follow-links">Follow External Links</Label>
              <Switch id="follow-links" />
            </div>
          </div>
        </CollapsibleSettingsCard>
      </div>
    </div>
  );
};