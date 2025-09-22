import { useState } from "react";
import { Card } from "../../../features/ui/primitives/card";
import { Switch } from "../../../features/ui/primitives/switch";
import { Checkbox } from "../../../features/ui/primitives/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "../../../features/ui/primitives/select";
import { Label } from "../../../features/ui/primitives/label";
import { Input } from "../../../features/ui/primitives/input";
import { Brain, Cpu, Zap, Database, Search, FileText } from "lucide-react";

/**
 * 🤖 AI CONTEXT: RAG Settings Example
 *
 * DESIGN PRINCIPLES:
 * 1. GLASSMORPHISM - All components use true glass effect
 * 2. NEON ACCENTS - Color-coded sections with glow
 * 3. GROUPED LAYOUT - Related settings in glass cards
 * 4. ACCESSIBILITY - Proper labels and keyboard navigation
 *
 * This replicates the actual RAG settings UI with:
 * - Model selection dropdowns
 * - Feature toggle switches
 * - Checkbox options
 * - Number inputs with glass styling
 */
export function RAGSettingsExample() {
  const [llmProvider, setLlmProvider] = useState("openai");
  const [modelChoice, setModelChoice] = useState("gpt-4");
  const [embeddingModel, setEmbeddingModel] = useState("text-embedding-3-small");
  const [enableRAG, setEnableRAG] = useState(true);
  const [enableCache, setEnableCache] = useState(true);
  const [enableStreaming, setEnableStreaming] = useState(false);
  const [searchOptions, setSearchOptions] = useState({
    semantic: true,
    keyword: true,
    hybrid: false,
  });
  const [maxTokens, setMaxTokens] = useState("2048");
  const [temperature, setTemperature] = useState("0.7");
  const [topK, setTopK] = useState("5");

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          RAG Settings Example
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Retrieval-Augmented Generation configuration with glassmorphic components
        </p>
      </div>

      {/* LLM Configuration */}
      <Card
        glassTint="green"
        glowColor="green"
        transparency="medium"
        className="p-6"
      >
        <div className="flex items-center gap-2 mb-4">
          <Brain className="w-5 h-5 text-emerald-400 drop-shadow-[0_0_5px_rgba(16,185,129,0.7)]" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            LLM Configuration
          </h3>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* Provider Selection */}
          <div>
            <Label htmlFor="provider" className="mb-2 block">
              Provider
            </Label>
            <Select value={llmProvider} onValueChange={setLlmProvider}>
              <SelectTrigger id="provider" color="green">
                <SelectValue />
              </SelectTrigger>
              <SelectContent color="green">
                <SelectItem value="openai" color="green">OpenAI</SelectItem>
                <SelectItem value="anthropic" color="green">Anthropic</SelectItem>
                <SelectItem value="google" color="green">Google</SelectItem>
                <SelectItem value="ollama" color="green">Ollama (Local)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Model Selection */}
          <div>
            <Label htmlFor="model" className="mb-2 block">
              Model
            </Label>
            <Select value={modelChoice} onValueChange={setModelChoice}>
              <SelectTrigger id="model" color="green">
                <SelectValue />
              </SelectTrigger>
              <SelectContent color="green">
                <SelectItem value="gpt-4" color="green">GPT-4</SelectItem>
                <SelectItem value="gpt-4-turbo" color="green">GPT-4 Turbo</SelectItem>
                <SelectItem value="gpt-3.5-turbo" color="green">GPT-3.5 Turbo</SelectItem>
                <SelectItem value="claude-3" color="green">Claude 3</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Embedding Model */}
          <div>
            <Label htmlFor="embedding" className="mb-2 block">
              Embedding Model
            </Label>
            <Select value={embeddingModel} onValueChange={setEmbeddingModel}>
              <SelectTrigger id="embedding" color="green">
                <SelectValue />
              </SelectTrigger>
              <SelectContent color="green">
                <SelectItem value="text-embedding-3-small" color="green">text-embedding-3-small</SelectItem>
                <SelectItem value="text-embedding-3-large" color="green">text-embedding-3-large</SelectItem>
                <SelectItem value="text-embedding-ada-002" color="green">text-embedding-ada-002</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Max Tokens */}
          <div>
            <Label htmlFor="max-tokens" className="mb-2 block">
              Max Tokens
            </Label>
            <Input
              id="max-tokens"
              type="number"
              value={maxTokens}
              onChange={(e) => setMaxTokens(e.target.value)}
              className="backdrop-blur-xl bg-black/10 dark:bg-white/10 border-green-500/30 focus:border-green-500"
            />
          </div>
        </div>
      </Card>

      {/* Feature Toggles */}
      <Card
        glassTint="green"
        glowColor="green"
        transparency="medium"
        className="p-6"
      >
        <div className="flex items-center gap-2 mb-4">
          <Cpu className="w-5 h-5 text-emerald-400 drop-shadow-[0_0_5px_rgba(16,185,129,0.7)]" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Features
          </h3>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 rounded-lg bg-black/5 dark:bg-white/5">
            <div className="flex-1">
              <Label htmlFor="rag-toggle" className="cursor-pointer">
                Enable RAG
              </Label>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Use knowledge base for context enhancement
              </p>
            </div>
            <Switch
              id="rag-toggle"
              size="lg"
              color="green"
              checked={enableRAG}
              onCheckedChange={setEnableRAG}
              icon={<Database className="w-5 h-5" />}
            />
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-black/5 dark:bg-white/5">
            <div className="flex-1">
              <Label htmlFor="cache-toggle" className="cursor-pointer">
                Response Caching
              </Label>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Cache similar queries for faster responses
              </p>
            </div>
            <Switch
              id="cache-toggle"
              size="lg"
              color="green"
              checked={enableCache}
              onCheckedChange={setEnableCache}
              icon={<Zap className="w-5 h-5" />}
            />
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-black/5 dark:bg-white/5">
            <div className="flex-1">
              <Label htmlFor="stream-toggle" className="cursor-pointer">
                Stream Responses
              </Label>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Enable real-time streaming of LLM responses
              </p>
            </div>
            <Switch
              id="stream-toggle"
              size="lg"
              color="green"
              checked={enableStreaming}
              onCheckedChange={setEnableStreaming}
              icon={<FileText className="w-5 h-5" />}
            />
          </div>
        </div>
      </Card>

      {/* Search Options */}
      <Card
        glassTint="green"
        glowColor="green"
        transparency="medium"
        className="p-6"
      >
        <div className="flex items-center gap-2 mb-4">
          <Search className="w-5 h-5 text-emerald-400 drop-shadow-[0_0_5px_rgba(16,185,129,0.7)]" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Search Options
          </h3>
        </div>

        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="semantic"
              color="green"
              checked={searchOptions.semantic}
              onCheckedChange={(checked) =>
                setSearchOptions(prev => ({ ...prev, semantic: checked as boolean }))
              }
            />
            <Label htmlFor="semantic" className="cursor-pointer">
              Semantic Search
              <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
                (Vector similarity)
              </span>
            </Label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="keyword"
              color="green"
              checked={searchOptions.keyword}
              onCheckedChange={(checked) =>
                setSearchOptions(prev => ({ ...prev, keyword: checked as boolean }))
              }
            />
            <Label htmlFor="keyword" className="cursor-pointer">
              Keyword Search
              <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
                (Full-text matching)
              </span>
            </Label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="hybrid"
              color="green"
              checked={searchOptions.hybrid}
              onCheckedChange={(checked) =>
                setSearchOptions(prev => ({ ...prev, hybrid: checked as boolean }))
              }
            />
            <Label htmlFor="hybrid" className="cursor-pointer">
              Hybrid Search
              <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
                (Combined approach)
              </span>
            </Label>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mt-4">
          <div>
            <Label htmlFor="temperature" className="mb-2 block">
              Temperature ({temperature})
            </Label>
            <input
              id="temperature"
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
              className="w-full accent-emerald-500"
            />
          </div>

          <div>
            <Label htmlFor="top-k" className="mb-2 block">
              Top K Results
            </Label>
            <Input
              id="top-k"
              type="number"
              value={topK}
              onChange={(e) => setTopK(e.target.value)}
              className="backdrop-blur-xl bg-black/10 dark:bg-white/10 border-emerald-500/30 focus:border-emerald-500"
            />
          </div>
        </div>
      </Card>

      {/* Status Summary */}
      <Card
        glassTint="green"
        glowColor="green"
        transparency="medium"
        className="p-4"
      >
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="text-center">
            <p className="text-gray-500 dark:text-gray-400">Provider</p>
            <p className="font-semibold text-gray-900 dark:text-white">{llmProvider}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500 dark:text-gray-400">Model</p>
            <p className="font-semibold text-gray-900 dark:text-white">{modelChoice}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500 dark:text-gray-400">RAG Status</p>
            <p className={`font-semibold ${enableRAG ? 'text-emerald-400' : 'text-gray-500'}`}>
              {enableRAG ? 'Enabled' : 'Disabled'}
            </p>
          </div>
        </div>
      </Card>

      {/* Code Example */}
      <div className="mt-8 p-4 rounded-lg bg-gray-900 text-gray-100 overflow-x-auto">
        <pre className="text-xs">
{`// Example configuration object
const ragConfig = {
  provider: "${llmProvider}",
  model: "${modelChoice}",
  embedding: "${embeddingModel}",
  features: {
    rag: ${enableRAG},
    cache: ${enableCache},
    streaming: ${enableStreaming}
  },
  search: {
    semantic: ${searchOptions.semantic},
    keyword: ${searchOptions.keyword},
    hybrid: ${searchOptions.hybrid}
  },
  parameters: {
    maxTokens: ${maxTokens},
    temperature: ${temperature},
    topK: ${topK}
  }
};`}
        </pre>
      </div>
    </div>
  );
}