import { useState } from "react";
import { Search, ChevronDown, ChevronRight, Code, FileText } from "lucide-react";
import { Button } from "@/features/ui/primitives/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/features/ui/primitives/dialog";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/features/ui/primitives/tabs";
import { Input } from "@/features/ui/primitives/input";

const MOCK_DOCUMENTS = [
  {
    id: "1",
    title: "Getting Started with React",
    content:
      "React is a JavaScript library for building user interfaces. It lets you compose complex UIs from small and isolated pieces of code called components. React components are JavaScript functions that return markup. Components can be as simple as a function that returns JSX, or they can have state and lifecycle methods...",
    tags: ["guide", "intro", "react"],
  },
  {
    id: "2",
    title: "API Reference - useState Hook",
    content:
      "useState is a React Hook that lets you add a state variable to your component. Call useState at the top level of your component to declare a state variable. The convention is to name state variables like [something, setSomething] using array destructuring. useState returns an array with exactly two values: the current state and the set function that lets you update it...",
    tags: ["api", "hooks", "reference"],
  },
  {
    id: "3",
    title: "Performance Optimization Guide",
    content:
      "Before you start optimizing, make sure you're actually measuring performance. React DevTools Profiler can help you identify components that are re-rendering unnecessarily. Common optimization techniques include: using React.memo for expensive components, using useMemo and useCallback hooks to memoize values and functions, code splitting with React.lazy and Suspense...",
    tags: ["performance", "optimization", "guide"],
  },
];

const MOCK_CODE = [
  {
    id: "1",
    language: "typescript",
    summary: "React functional component with useState",
    code: `const Counter = () => {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
};`,
    file_path: "src/components/Counter.tsx",
  },
  {
    id: "2",
    language: "python",
    summary: "FastAPI endpoint with dependency injection",
    code: `@app.get("/api/items/{item_id}")
async def get_item(
    item_id: str,
    db: Session = Depends(get_db)
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item`,
    file_path: "src/api/routes/items.py",
  },
  {
    id: "3",
    language: "typescript",
    summary: "Custom React hook for data fetching",
    code: `const useData = <T>(url: string) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [url]);

  return { data, loading, error };
};`,
    file_path: "src/hooks/useData.ts",
  },
];

export const DocumentBrowserExample = () => {
  const [open, setOpen] = useState(false);

  return (
    <div className="space-y-4">
      {/* Explanation Text */}
      <p className="text-sm text-gray-600 dark:text-gray-400">
        <strong>Use this pattern for:</strong> Displaying structured information in modals
        (documents, logs, code, API responses). Tabs organize different data types, search filters
        content, items expand/collapse for details.
      </p>

      {/* Button to Open Modal */}
      <Button onClick={() => setOpen(true)}>Open Document Browser Example</Button>

      {/* Document Browser Modal */}
      <DocumentBrowserModal open={open} onOpenChange={setOpen} />
    </div>
  );
};

const DocumentBrowserModal = ({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) => {
  const [activeTab, setActiveTab] = useState<"documents" | "code">("documents");
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  const toggleExpanded = (id: string) => {
    setExpandedItems((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  // Filter based on search
  const filteredDocuments = MOCK_DOCUMENTS.filter((doc) =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredCode = MOCK_CODE.filter((example) =>
    example.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
    example.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Document Browser</DialogTitle>
          <div className="flex items-center gap-2 mt-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search documents and code..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-black/30 border-white/10 focus:border-cyan-500/50"
              />
            </div>
          </div>
        </DialogHeader>

        <Tabs
          value={activeTab}
          onValueChange={(v) => setActiveTab(v as "documents" | "code")}
          className="flex-1 flex flex-col"
        >
          <TabsList>
            <TabsTrigger value="documents" className="data-[state=active]:bg-cyan-500/20">
              <FileText className="w-4 h-4 mr-2" />
              Documents ({filteredDocuments.length})
            </TabsTrigger>
            <TabsTrigger value="code" className="data-[state=active]:bg-cyan-500/20">
              <Code className="w-4 h-4 mr-2" />
              Code Examples ({filteredCode.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="documents" className="flex-1 overflow-hidden">
            <div className="h-full overflow-y-auto">
              {filteredDocuments.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  {searchQuery ? "No documents match your search" : "No documents available"}
                </div>
              ) : (
                <div className="space-y-3 p-4">
                  {filteredDocuments.map((doc) => {
                    const isExpanded = expandedItems.has(doc.id);
                    const preview = doc.content.substring(0, 200);
                    const needsExpansion = doc.content.length > 200;

                    return (
                      <div
                        key={doc.id}
                        className="bg-black/30 rounded-lg border border-white/10 p-4 hover:border-cyan-500/30 transition-colors"
                      >
                        {doc.title && (
                          <h4 className="font-medium text-white/90 mb-2 flex items-center gap-2">
                            {needsExpansion && (
                              <button
                                type="button"
                                onClick={() => toggleExpanded(doc.id)}
                                className="text-gray-400 hover:text-white transition-colors"
                              >
                                {isExpanded ? (
                                  <ChevronDown className="w-4 h-4" />
                                ) : (
                                  <ChevronRight className="w-4 h-4" />
                                )}
                              </button>
                            )}
                            {doc.title}
                          </h4>
                        )}

                        <div className="text-sm text-gray-300 whitespace-pre-wrap">
                          {isExpanded || !needsExpansion ? (
                            doc.content
                          ) : (
                            <>
                              {preview}...
                              <button
                                type="button"
                                onClick={() => toggleExpanded(doc.id)}
                                className="ml-2 text-cyan-400 hover:text-cyan-300"
                              >
                                Show more
                              </button>
                            </>
                          )}
                        </div>

                        {doc.tags && doc.tags.length > 0 && (
                          <div className="flex items-center gap-2 mt-3 flex-wrap">
                            {doc.tags.map((tag) => (
                              <span key={tag} className="px-2 py-1 text-xs border border-white/20 rounded bg-black/20">
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="code" className="flex-1 overflow-hidden">
            <div className="h-full overflow-y-auto">
              {filteredCode.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  {searchQuery ? "No code examples match your search" : "No code examples available"}
                </div>
              ) : (
                <div className="space-y-3 p-4">
                  {filteredCode.map((example) => (
                    <div
                      key={example.id}
                      className="bg-black/30 rounded-lg border border-white/10 overflow-hidden hover:border-cyan-500/30 transition-colors"
                    >
                      <div className="flex items-center justify-between p-3 border-b border-white/10 bg-black/20">
                        <div className="flex items-center gap-2">
                          <Code className="w-4 h-4 text-cyan-400" />
                          {example.language && (
                            <span className="px-2 py-1 text-xs bg-cyan-500/20 text-cyan-400 rounded">
                              {example.language}
                            </span>
                          )}
                        </div>
                        {example.file_path && <span className="text-xs text-gray-400">{example.file_path}</span>}
                      </div>

                      {example.summary && (
                        <div className="p-3 text-sm text-gray-300 border-b border-white/10">{example.summary}</div>
                      )}

                      <pre className="p-4 text-sm overflow-x-auto">
                        <code className="text-gray-300">{example.code}</code>
                      </pre>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};
