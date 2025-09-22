import { Card } from '@/features/ui/primitives/card';
import { cn } from '@/features/ui/primitives/styles';

interface ConfigPanelProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export const ConfigPanel = ({ title, children, className }: ConfigPanelProps) => (
  <Card className={cn("space-y-4", className)}>
    {title && <h3 className="font-semibold text-lg mb-2 text-gray-900 dark:text-white">{title}</h3>}
    {children}
  </Card>
);