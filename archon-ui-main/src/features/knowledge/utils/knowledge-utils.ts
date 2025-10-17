/**
 * Knowledge Base Utility Functions
 */

import type { KnowledgeItem, KnowledgeItemMetadata, KnowledgeSortConfig } from "../types";

/**
 * Group knowledge items by their group_name metadata
 */
export function groupKnowledgeItems(items: KnowledgeItem[]) {
  const grouped = new Map<string, KnowledgeItem[]>();
  const ungrouped: KnowledgeItem[] = [];

  items.forEach((item) => {
    const groupName = item.metadata?.group_name;
    if (groupName) {
      const existing = grouped.get(groupName) || [];
      existing.push(item);
      grouped.set(groupName, existing);
    } else {
      ungrouped.push(item);
    }
  });

  return {
    grouped: Array.from(grouped.entries()).map(([name, items]) => ({
      name,
      items,
      count: items.length,
    })),
    ungrouped,
  };
}

/**
 * Get display type for a knowledge item
 */
export function getKnowledgeItemType(item: KnowledgeItem): string {
  if (item.metadata?.source_type === "file") {
    return item.metadata.file_type || "document";
  }
  if (item.metadata?.source_type === "group") {
    return "group";
  }
  return item.metadata?.knowledge_type || "general";
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes?: number): string {
  if (!bytes) return "0 B";

  const units = ["B", "KB", "MB", "GB"];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(1)} ${units[unitIndex]}`;
}

/**
 * Get status color for knowledge item
 */
export function getStatusColor(status?: KnowledgeItemMetadata["status"]) {
  switch (status) {
    case "active":
      return "green";
    case "processing":
      return "blue";
    case "error":
      return "red";
    default:
      return "gray";
  }
}

/**
 * Check if a knowledge item needs refresh based on update frequency
 */
export function needsRefresh(item: KnowledgeItem): boolean {
  const updateFrequency = item.metadata?.update_frequency;
  if (!updateFrequency) return false;

  const lastScraped = item.metadata?.last_scraped;
  if (!lastScraped) return true;

  const lastScrapedDate = new Date(lastScraped);
  const time = lastScrapedDate.getTime();

  // If date is invalid, force a refresh
  if (Number.isNaN(time)) return true;

  const daysSinceLastScrape = (Date.now() - time) / (1000 * 60 * 60 * 24);

  return daysSinceLastScrape >= updateFrequency;
}

/**
 * Extract domain from URL
 */
export function extractDomain(url: string): string {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname.replace("www.", "");
  } catch {
    return url;
  }
}

/**
 * Get icon for file type
 */
export function getFileTypeIcon(fileType?: string): string {
  if (!fileType) return "📄";

  const lowerType = fileType.toLowerCase();
  if (lowerType.includes("pdf")) return "📕";
  if (lowerType.includes("doc")) return "📘";
  if (lowerType.includes("txt")) return "📝";
  if (lowerType.includes("md")) return "📋";
  if (lowerType.includes("code") || lowerType.includes("json")) return "💻";

  return "📄";
}

/**
 * Status priority for sorting (processing > active > completed > error)
 */
const STATUS_PRIORITY: Record<string, number> = {
  processing: 0,
  active: 1,
  completed: 2,
  error: 3,
};

/**
 * Sort knowledge items based on sort configuration
 */
export function sortKnowledgeItems(items: KnowledgeItem[], sortConfig: KnowledgeSortConfig): KnowledgeItem[] {
  return [...items].sort((a, b) => {
    let comparison = 0;

    switch (sortConfig.field) {
      case "title":
        comparison = a.title.localeCompare(b.title);
        break;

      case "created_at":
        comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        break;

      case "updated_at":
        comparison = new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime();
        break;

      case "status": {
        const aPriority = STATUS_PRIORITY[a.status] ?? 999;
        const bPriority = STATUS_PRIORITY[b.status] ?? 999;
        comparison = aPriority - bPriority;
        break;
      }

      case "document_count":
        comparison = a.document_count - b.document_count;
        break;

      case "code_examples_count":
        comparison = a.code_examples_count - b.code_examples_count;
        break;

      default:
        comparison = 0;
    }

    return sortConfig.direction === "asc" ? comparison : -comparison;
  });
}
