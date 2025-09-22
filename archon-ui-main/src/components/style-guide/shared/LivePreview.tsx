import { useState } from 'react';
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { Button } from '@/features/ui/primitives/button';
import { cn } from '@/features/ui/primitives/styles';

interface LivePreviewProps {
  children: React.ReactNode;
  className?: string;
  minHeight?: string;
}

export const LivePreview = ({ children, className, minHeight = "400px" }: LivePreviewProps) => {
  const [zoom, setZoom] = useState(100);

  return (
    <div className="relative rounded-lg overflow-hidden">
      {/* Zoom Controls */}
      <div className="absolute top-2 right-2 z-10 flex gap-1">
        <Button
          size="icon"
          variant="outline"
          onClick={() => setZoom(prev => Math.max(50, prev - 25))}
        >
          <ZoomOut className="w-4 h-4" />
        </Button>
        <Button
          size="icon"
          variant="outline"
          onClick={() => setZoom(100)}
        >
          <RotateCcw className="w-4 h-4" />
        </Button>
        <Button
          size="icon"
          variant="outline"
          onClick={() => setZoom(prev => Math.min(150, prev + 25))}
        >
          <ZoomIn className="w-4 h-4" />
        </Button>
      </div>

      {/* Grid Background */}
      <div
        className={cn(
          "bg-gray-50 dark:bg-gray-900/50",
          "bg-[linear-gradient(to_right,#8882_1px,transparent_1px),linear-gradient(to_bottom,#8882_1px,transparent_1px)]",
          "bg-[size:20px_20px]",
          "p-8 flex items-center justify-center",
          className
        )}
        style={{ minHeight }}
      >
        <div
          style={{
            transform: `scale(${zoom / 100})`,
            transformOrigin: 'center'
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
};