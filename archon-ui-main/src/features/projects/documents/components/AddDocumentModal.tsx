import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import {
  Button,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  Input,
} from "../../../ui/primitives";
import { cn } from "../../../ui/primitives/styles";

interface AddDocumentModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAdd: (title: string, type: string) => Promise<void>;
}

export const AddDocumentModal = ({ open, onOpenChange, onAdd }: AddDocumentModalProps) => {
  const [title, setTitle] = useState("");
  const [type, setType] = useState("spec");
  const [isAdding, setIsAdding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form state when modal closes
  useEffect(() => {
    if (!open) {
      setTitle("");
      setType("spec");
      setError(null);
      setIsAdding(false);
    }
  }, [open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsAdding(true);
    setError(null);

    try {
      await onAdd(title, type);
      setTitle("");
      setType("spec");
      setError(null);
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create document");
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add New Document</DialogTitle>
            <DialogDescription>Create a new document for this project</DialogDescription>
          </DialogHeader>

          <div className="space-y-4 my-6">
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-3">
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}

            <div>
              <label htmlFor="document-title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Document Title
              </label>
              <Input
                id="document-title"
                type="text"
                placeholder="Enter document title..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                disabled={isAdding}
                autoFocus
              />
            </div>

            <div>
              <label htmlFor="document-type" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Document Type
              </label>
              <select
                id="document-type"
                value={type}
                onChange={(e) => setType(e.target.value)}
                disabled={isAdding}
                className={cn(
                  "w-full px-3 py-2 rounded-md",
                  "bg-white/50 dark:bg-black/30",
                  "border border-gray-300 dark:border-gray-700",
                  "text-gray-900 dark:text-white",
                  "focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
                )}
              >
                <option value="spec">Specification</option>
                <option value="api">API Documentation</option>
                <option value="guide">Guide</option>
                <option value="note">Note</option>
                <option value="design">Design</option>
              </select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="ghost" onClick={() => onOpenChange(false)} disabled={isAdding}>
              Cancel
            </Button>
            <Button type="submit" variant="default" disabled={isAdding || !title.trim()}>
              {isAdding ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Adding...
                </>
              ) : (
                "Add Document"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
