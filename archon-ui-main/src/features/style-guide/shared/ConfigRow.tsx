import { Label } from '@/features/ui/primitives/label';
import { cn } from '@/features/ui/primitives/styles';

interface ConfigRowProps {
  label: string;
  children: React.ReactNode;
  className?: string;
}

export const ConfigRow = ({ label, children, className }: ConfigRowProps) => (
  <div className={cn("flex items-center justify-between", className)}>
    <Label className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</Label>
    <div className="flex-shrink-0">
      {children}
    </div>
  </div>
);