/**
 * Knowledge Card Status Badge
 * Displays crawl status with appropriate icon and color
 */

import { CheckCircle, Clock, XCircle } from "lucide-react";
import { cn } from "../../ui/primitives/styles";
import { SimpleTooltip } from "../../ui/primitives/tooltip";

interface KnowledgeCardStatusProps {
  status: "active" | "processing" | "error";
  crawlStatus?: "pending" | "completed" | "failed";
  className?: string;
}

export const KnowledgeCardStatus: React.FC<KnowledgeCardStatusProps> = ({
  status,
  // biome-ignore lint/correctness/noUnusedFunctionParameters: Reserved for future use when mapping crawl_status directly
  crawlStatus,
  className,
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case "error":
        return {
          label: "Failed",
          icon: <XCircle className="w-3.5 h-3.5" />,
          bgColor: "bg-red-100 dark:bg-red-500/10",
          textColor: "text-red-700 dark:text-red-400",
          borderColor: "border-red-200 dark:border-red-500/20",
          tooltip: "Crawl failed - click refresh to retry",
        };
      case "processing":
        return {
          label: "Pending",
          icon: <Clock className="w-3.5 h-3.5" />,
          bgColor: "bg-yellow-100 dark:bg-yellow-500/10",
          textColor: "text-yellow-700 dark:text-yellow-400",
          borderColor: "border-yellow-200 dark:border-yellow-500/20",
          tooltip: "Crawl not yet completed",
        };
      case "active":
      default:
        return {
          label: "Completed",
          icon: <CheckCircle className="w-3.5 h-3.5" />,
          bgColor: "bg-green-100 dark:bg-green-500/10",
          textColor: "text-green-700 dark:text-green-400",
          borderColor: "border-green-200 dark:border-green-500/20",
          tooltip: "Successfully crawled and indexed",
        };
    }
  };

  const config = getStatusConfig();

  return (
    <SimpleTooltip content={config.tooltip}>
      <div
        className={cn(
          "inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium border",
          config.bgColor,
          config.textColor,
          config.borderColor,
          className,
        )}
      >
        {config.icon}
        <span>{config.label}</span>
      </div>
    </SimpleTooltip>
  );
};
