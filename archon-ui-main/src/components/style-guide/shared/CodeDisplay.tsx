import { useState } from 'react';
import { Check, Copy } from 'lucide-react';
import { Button } from '@/features/ui/primitives/button';
import { cn } from '@/features/ui/primitives/styles';

interface CodeDisplayProps {
  code: string;
  showLineNumbers?: boolean;
  className?: string;
}

export const CodeDisplay = ({
  code,
  showLineNumbers = false,
  className
}: CodeDisplayProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = code.split('\n');

  // Basic syntax highlighting with regex
  const highlightCode = (line: string) => {
    // Escape HTML
    line = line.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // Keywords
    line = line.replace(
      /\b(import|export|from|const|let|var|function|return|if|else|interface|type|class|extends|implements)\b/g,
      '<span class="text-purple-400">$1</span>'
    );

    // Strings
    line = line.replace(
      /(["'`])([^"'`]*)\1/g,
      '<span class="text-green-400">$1$2$1</span>'
    );

    // Comments
    line = line.replace(
      /(\/\/.*$|\/\*.*\*\/)/g,
      '<span class="text-gray-500">$1</span>'
    );

    // JSX tags
    line = line.replace(
      /&lt;([A-Z][A-Za-z0-9]*)(\s|&gt;|\/&gt;)/g,
      '&lt;<span class="text-cyan-400">$1</span>$2'
    );

    // Props
    line = line.replace(
      /(\w+)=/g,
      '<span class="text-orange-400">$1</span>='
    );

    return line;
  };

  return (
    <div className={cn(
      "relative rounded-lg overflow-hidden",
      "bg-gray-900 border border-gray-800",
      className
    )}>
      {/* Copy Button */}
      <Button
        size="icon"
        variant="ghost"
        onClick={handleCopy}
        className="absolute top-2 right-2 z-10 text-gray-400 hover:text-white"
      >
        {copied ? (
          <Check className="w-4 h-4 text-green-400" />
        ) : (
          <Copy className="w-4 h-4" />
        )}
      </Button>

      {/* Code Content */}
      <pre className="p-4 overflow-x-auto">
        <code className="text-sm font-mono">
          {lines.map((line, index) => (
            <div key={index} className="flex">
              {showLineNumbers && (
                <span className="text-gray-500 mr-4 select-none w-8 text-right">
                  {index + 1}
                </span>
              )}
              <span
                dangerouslySetInnerHTML={{
                  __html: highlightCode(line) || '&nbsp;'
                }}
              />
            </div>
          ))}
        </code>
      </pre>
    </div>
  );
};