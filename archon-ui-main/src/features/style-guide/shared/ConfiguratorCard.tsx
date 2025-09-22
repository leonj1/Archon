import React, { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { Eye, Code } from 'lucide-react';

interface ConfiguratorCardProps {
  title: string;
  description?: string;
  code: string;
  children: React.ReactNode;
}

export function ConfiguratorCard({ title, description, code, children }: ConfiguratorCardProps) {
  const [showCode, setShowCode] = useState(false);

  return (
    <Card className="p-6" glassTint="none" glowColor="none">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
            {description && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{description}</p>
            )}
          </div>
          <div className="flex gap-2">
            <Button
              variant={!showCode ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowCode(false)}
            >
              <Eye className="w-4 h-4 mr-2" />
              Preview
            </Button>
            <Button
              variant={showCode ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowCode(true)}
            >
              <Code className="w-4 h-4 mr-2" />
              Code
            </Button>
          </div>
        </div>

        {showCode ? (
          <div className="rounded-lg bg-gray-900 p-4 overflow-x-auto">
            <pre className="text-xs text-gray-100">
              <code>{code}</code>
            </pre>
          </div>
        ) : (
          <div>{children}</div>
        )}
      </div>
    </Card>
  );
}