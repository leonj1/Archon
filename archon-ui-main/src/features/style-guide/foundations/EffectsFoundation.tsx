import { useState, useEffect } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { CodeDisplay } from '../shared/CodeDisplay';
import { cn } from '@/features/ui/primitives/styles';
import { Loader2, Zap, Sparkles, MousePointer } from 'lucide-react';

// Add Tron animations to the page
const addTronAnimations = () => {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes dataStream {
      0%, 100% { transform: translateY(-100%); }
      50% { transform: translateY(100%); }
    }

    @keyframes progressSweep {
      0%, 100% { background: linear-gradient(to right, #3b82f6, #ef4444, #3b82f6); }
      50% { background: linear-gradient(to right, #ef4444, #3b82f6, #ef4444); }
    }

    @keyframes lightTrail {
      0% { transform: translateX(-100%); }
      100% { transform: translateX(400%); }
    }

    @keyframes energyCascade {
      0% { transform: translateX(-100%) skewX(12deg); }
      100% { transform: translateX(200%) skewX(12deg); }
    }

    @keyframes recognitionScan {
      0%, 100% { height: 0.5rem; opacity: 0.3; }
      50% { height: 2rem; opacity: 1; }
    }

    @keyframes spectrumWave {
      0%, 100% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
    }

    @keyframes sparkRace {
      0% {
        top: 0;
        left: 0;
        transform: translateX(0);
      }
      25% {
        top: 0;
        left: 100%;
        transform: translateX(-100%);
      }
      25.01% {
        top: 0;
        left: 100%;
        transform: translateY(0);
      }
      50% {
        top: 100%;
        left: 100%;
        transform: translateY(-100%);
      }
      50.01% {
        top: 100%;
        left: 100%;
        transform: translateX(0);
      }
      75% {
        top: 100%;
        left: 0;
        transform: translateX(0);
      }
      75.01% {
        top: 100%;
        left: 0;
        transform: translateY(0);
      }
      100% {
        top: 0;
        left: 0;
        transform: translateY(0);
      }
    }

    .animate-spin-reverse {
      animation: spin 1s linear infinite reverse;
    }

    .animate-dataStream {
      animation: dataStream 1.5s ease-in-out infinite;
    }

    .animate-progressSweep {
      animation: progressSweep 3s ease-in-out infinite;
    }

    .animate-lightTrail {
      animation: lightTrail 2s ease-in-out infinite;
    }

    .animate-energyCascade {
      animation: energyCascade 2s linear infinite;
    }

    .animate-recognitionScan {
      animation: recognitionScan 2s ease-in-out infinite;
    }

    .animate-spectrumWave {
      animation: spectrumWave 4s ease-in-out infinite;
    }

    .animate-borderRace {
      animation: borderRace 2s linear infinite;
    }
  `;
  document.head.appendChild(style);
  return () => style.remove();
};

const EFFECT_OPTIONS = [
  'Interaction',
  'Loading',
  'Neon',
  'Animation'
];

export const EffectsFoundation = () => {
  const [activeOption, setActiveOption] = useState('Interaction');
  const [selectedEffect, setSelectedEffect] = useState('hover-glow');

  // Add custom animations when component mounts
  useEffect(() => {
    const cleanup = addTronAnimations();
    return cleanup;
  }, []);

  // Option 1: Hover & Interaction Effects
  const renderOption1 = () => (
    <div className="space-y-8">
      <h3 className="text-lg font-semibold flex items-center gap-2">
        <MousePointer className="w-5 h-5" />
        Hover & Interaction Effects
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Racing Border Effect */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Racing Border</h4>
          <div className="w-20 h-12 mx-auto bg-black border border-gray-600 rounded-lg cursor-pointer group relative flex items-center justify-center text-xs text-gray-300">
            <span className="relative z-10">Hover Me</span>
            {/* Racing spark */}
            <div className="absolute w-2 h-0.5 bg-blue-400 shadow-[0_0_8px_rgba(59,130,246,1)] opacity-0 group-hover:opacity-100 group-hover:animate-[sparkRace_2s_linear_infinite] rounded-full"></div>
          </div>
        </Card>

        {/* Blue Glass Button */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Blue Glass</h4>
          <button className="backdrop-blur-sm bg-blue-500/20 border border-blue-500/50 hover:bg-blue-500/30 hover:border-blue-500 hover:shadow-[0_0_25px_rgba(59,130,246,0.8)] transition-all duration-300 text-blue-300 hover:text-blue-200 px-4 py-2 rounded-full text-sm font-medium">
            Glass Button
          </button>
        </Card>

        {/* Red Alert Hover */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Red Alert</h4>
          <div className="w-16 h-16 mx-auto bg-red-500/20 border border-red-500 rounded-lg cursor-pointer hover:scale-110 hover:shadow-[0_0_30px_rgba(239,68,68,0.8)] transition-all duration-200 flex items-center justify-center text-red-300 text-xs">Alert</div>
        </Card>

        {/* Neon Text Glow */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Neon Text</h4>
          <div className="text-blue-400 cursor-pointer hover:drop-shadow-[0_0_12px_rgba(59,130,246,1)] transition-all duration-300 font-bold text-lg">
            BLUE NEON
          </div>
        </Card>

        {/* Program Recognition */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Program ID</h4>
          <div className="w-20 h-12 mx-auto bg-black border border-blue-500/50 rounded-lg cursor-pointer hover:border-red-500 hover:shadow-[0_0_20px_rgba(239,68,68,0.6)] transition-all duration-500 flex items-center justify-center text-xs text-gray-300">
            ID: 7364
          </div>
        </Card>

        {/* Pulse Activation */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Pulse Hover</h4>
          <div className="w-20 h-12 mx-auto bg-purple-500/20 border border-purple-500 rounded-lg cursor-pointer hover:animate-pulse hover:shadow-[0_0_30px_rgba(168,85,247,0.8)] transition-all duration-300 flex items-center justify-center text-purple-300 text-xs font-medium">
            Pulse Me
          </div>
        </Card>
      </div>
    </div>
  );

  // Option 2: Loading & Skeleton Effects
  const renderOption2 = () => (
    <div className="space-y-8">
      <h3 className="text-lg font-semibold flex items-center gap-2">
        <Loader2 className="w-5 h-5" />
        Loading & Skeleton Effects
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Light Cycle Circuit */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Light Cycle Circuit</h4>
          <div className="w-16 h-16 mx-auto relative">
            <div className="absolute inset-0 border-2 border-transparent border-t-blue-400 border-r-red-500 rounded-full animate-spin shadow-[0_0_20px_rgba(59,130,246,0.8)]"></div>
            <div className="absolute inset-2 border-2 border-transparent border-b-red-500 border-l-blue-400 rounded-full animate-spin-reverse shadow-[0_0_20px_rgba(239,68,68,0.8)]"></div>
          </div>
        </Card>

        {/* Data Stream */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Data Stream</h4>
          <div className="w-16 h-16 mx-auto relative overflow-hidden rounded-lg border border-blue-500/30">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-blue-500/40 to-transparent animate-dataStream"></div>
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-red-500/40 to-transparent animate-dataStream" style={{animationDelay: '0.75s'}}></div>
          </div>
        </Card>

        {/* Tron Grid Progress */}
        <Card className="p-4 bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Grid Progress</h4>
          <div className="w-full bg-black border border-blue-500/30 h-4 rounded relative overflow-hidden"
               style={{
                 backgroundImage: `
                   linear-gradient(rgba(59, 130, 246, 0.1) 1px, transparent 1px),
                   linear-gradient(90deg, rgba(59, 130, 246, 0.1) 1px, transparent 1px)
                 `,
                 backgroundSize: '4px 4px'
               }}>
            <div className="h-full rounded shadow-[0_0_15px_rgba(59,130,246,0.8)] animate-progressSweep"
                 style={{width: '60%'}}></div>
          </div>
        </Card>

        {/* Light Trail Skeleton */}
        <Card className="p-4 bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Light Trails</h4>
          <div className="space-y-3">
            <div className="h-3 bg-black border border-blue-500/50 rounded relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-400 to-transparent w-1/3 animate-lightTrail shadow-[0_0_10px_rgba(59,130,246,0.8)]"></div>
            </div>
            <div className="h-3 bg-black border border-red-500/50 rounded w-3/4 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-red-500 to-transparent w-1/3 animate-lightTrail shadow-[0_0_10px_rgba(239,68,68,0.8)]" style={{animationDelay: '0.5s'}}></div>
            </div>
            <div className="h-3 bg-black border border-blue-500/50 rounded w-1/2 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-400 to-transparent w-1/3 animate-lightTrail shadow-[0_0_10px_rgba(59,130,246,0.8)]" style={{animationDelay: '1s'}}></div>
            </div>
          </div>
        </Card>

        {/* Energy Cascade */}
        <Card className="p-4 bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Energy Cascade</h4>
          <div className="w-full h-16 bg-black border border-blue-500/30 rounded-lg relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-400/60 to-transparent animate-energyCascade shadow-[0_0_20px_rgba(59,130,246,0.6)]"></div>
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-red-500/40 to-transparent animate-energyCascade shadow-[0_0_20px_rgba(239,68,68,0.4)]" style={{animationDelay: '1s'}}></div>
          </div>
        </Card>

        {/* Recognition Pattern */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Recognition Pattern</h4>
          <div className="flex gap-1 justify-center">
            {[0, 1, 2, 3, 4].map(i => (
              <div
                key={i}
                className={cn(
                  "w-2 rounded-sm animate-recognitionScan",
                  i % 2 === 0 ? "bg-blue-400 shadow-[0_0_8px_rgba(59,130,246,0.8)]" : "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]"
                )}
                style={{ animationDelay: `${i * 0.1}s` }}
              ></div>
            ))}
          </div>
        </Card>
      </div>

      {/* Custom Tron Animations CSS */}
      <Card className="p-4 bg-black border border-cyan-500/30">
        <h4 className="text-sm font-medium text-gray-100 mb-3">Tron Animation Keyframes (Add to CSS)</h4>
        <CodeDisplay
          code={`@keyframes dataStream {
  0%, 100% { transform: translateY(-100%); }
  50% { transform: translateY(100%); }
}

@keyframes progressSweep {
  0%, 100% { background: linear-gradient(to right, #3b82f6, #ef4444, #3b82f6); }
  50% { background: linear-gradient(to right, #ef4444, #3b82f6, #ef4444); }
}

@keyframes lightTrail {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(400%); }
}

@keyframes energyCascade {
  0% { transform: translateX(-100%) skewX(12deg); }
  100% { transform: translateX(200%) skewX(12deg); }
}

@keyframes recognitionScan {
  0%, 100% { height: 0.5rem; opacity: 0.3; }
  50% { height: 2rem; opacity: 1; }
}`}
          showLineNumbers={false}
        />
      </Card>
    </div>
  );

  // Option 3: Gradient & Neon Effects
  const renderOption3 = () => (
    <div className="space-y-8">
      <h3 className="text-lg font-semibold flex items-center gap-2">
        <Zap className="w-5 h-5" />
        Gradient & Neon Effects
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Multi-Color Neon Text */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Neon Typography</h4>
          <div className="space-y-2">
            <div className="text-blue-400 text-lg font-bold drop-shadow-[0_0_10px_rgba(59,130,246,0.8)]">BLUE NEON</div>
            <div className="text-pink-400 text-lg font-bold drop-shadow-[0_0_10px_rgba(244,114,182,0.8)]">PINK NEON</div>
            <div className="text-emerald-400 text-lg font-bold drop-shadow-[0_0_10px_rgba(52,211,153,0.8)]">GREEN NEON</div>
          </div>
        </Card>

        {/* Neon Orb Constellation */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Neon Orbs</h4>
          <div className="flex gap-2 justify-center items-center">
            <div className="w-8 h-8 bg-purple-500 rounded-full shadow-[0_0_20px_rgba(168,85,247,0.8)] animate-pulse"></div>
            <div className="w-6 h-6 bg-blue-500 rounded-full shadow-[0_0_15px_rgba(59,130,246,0.8)] animate-pulse" style={{animationDelay: '0.5s'}}></div>
            <div className="w-10 h-10 bg-pink-500 rounded-full shadow-[0_0_25px_rgba(244,114,182,0.8)] animate-pulse" style={{animationDelay: '1s'}}></div>
            <div className="w-7 h-7 bg-emerald-500 rounded-full shadow-[0_0_18px_rgba(52,211,153,0.8)] animate-pulse" style={{animationDelay: '1.5s'}}></div>
          </div>
        </Card>

        {/* Rainbow Laser Grid */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Laser Grid</h4>
          <div className="w-full h-16 relative overflow-hidden rounded-lg border border-purple-500/30">
            <div className="absolute top-2 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-blue-400 to-transparent shadow-[0_0_8px_rgba(59,130,246,0.8)]"></div>
            <div className="absolute top-6 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-pink-400 to-transparent shadow-[0_0_8px_rgba(244,114,182,0.8)]"></div>
            <div className="absolute top-10 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-emerald-400 to-transparent shadow-[0_0_8px_rgba(52,211,153,0.8)]"></div>
            <div className="absolute top-14 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-purple-400 to-transparent shadow-[0_0_8px_rgba(168,85,247,0.8)]"></div>
          </div>
        </Card>

        {/* Gradient Borders */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Neon Borders</h4>
          <div className="space-y-3">
            <div className="w-20 h-8 mx-auto bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 p-[2px] rounded-lg">
              <div className="w-full h-full bg-black rounded-md flex items-center justify-center text-xs text-gray-300">Purple</div>
            </div>
            <div className="w-20 h-8 mx-auto bg-gradient-to-r from-blue-500 via-emerald-500 to-blue-500 p-[2px] rounded-lg">
              <div className="w-full h-full bg-black rounded-md flex items-center justify-center text-xs text-gray-300">Blue</div>
            </div>
          </div>
        </Card>

        {/* Spectrum Wave */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Spectrum Wave</h4>
          <div className="w-full h-12 rounded-lg relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500 via-blue-500 via-emerald-500 via-pink-500 to-purple-500 animate-[spectrumWave_4s_ease-in-out_infinite] bg-[length:200%_100%]"></div>
          </div>
        </Card>

        {/* Pulsing Circuit */}
        <Card className="p-4 text-center bg-black">
          <h4 className="text-sm font-medium text-gray-100 mb-3">Pulsing Circuit</h4>
          <div className="w-16 h-16 mx-auto relative">
            <div className="absolute inset-0 border-2 border-blue-500 rounded-lg animate-pulse shadow-[0_0_20px_rgba(59,130,246,0.6)]"></div>
            <div className="absolute inset-2 border-2 border-pink-500 rounded-lg animate-pulse shadow-[0_0_15px_rgba(244,114,182,0.6)]" style={{animationDelay: '0.5s'}}></div>
            <div className="absolute inset-4 border-2 border-emerald-500 rounded-lg animate-pulse shadow-[0_0_10px_rgba(52,211,153,0.6)]" style={{animationDelay: '1s'}}></div>
          </div>
        </Card>
      </div>

      {/* Neon Animation Keyframes */}
      <Card className="p-4 bg-black border border-pink-500/30">
        <h4 className="text-sm font-medium text-gray-100 mb-3">Neon Animation Keyframes (Add to CSS)</h4>
        <CodeDisplay
          code={`@keyframes spectrumWave {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes neonPulse {
  0%, 100% {
    box-shadow: 0 0 5px currentColor, 0 0 10px currentColor, 0 0 20px currentColor;
  }
  50% {
    box-shadow: 0 0 10px currentColor, 0 0 20px currentColor, 0 0 40px currentColor;
  }
}

@keyframes colorShift {
  0% { filter: hue-rotate(0deg); }
  25% { filter: hue-rotate(90deg); }
  50% { filter: hue-rotate(180deg); }
  75% { filter: hue-rotate(270deg); }
  100% { filter: hue-rotate(360deg); }
}`}
          showLineNumbers={false}
        />
      </Card>
    </div>
  );

  // Option 4: Motion & Animation Effects
  const renderOption4 = () => (
    <div className="space-y-8">
      <h3 className="text-lg font-semibold flex items-center gap-2">
        <Sparkles className="w-5 h-5" />
        Motion & Animation Effects
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Fade In */}
        <Card className="p-4 text-center">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Fade In</h4>
          <div className="w-16 h-16 mx-auto bg-gradient-to-br from-purple-500 to-emerald-500 rounded-lg animate-[fadeIn_2s_ease-in-out_infinite] shadow-[0_0_15px_rgba(168,85,247,0.4)]"></div>
        </Card>

        {/* Slide Up */}
        <Card className="p-4 text-center">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Slide Up</h4>
          <div className="w-16 h-16 mx-auto bg-gradient-to-br from-cyan-500 to-emerald-500 rounded-lg animate-[slideUp_2s_ease-in-out_infinite] shadow-[0_0_15px_rgba(34,211,238,0.4)]"></div>
        </Card>

        {/* Bounce */}
        <Card className="p-4 text-center">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Bounce</h4>
          <div className="w-16 h-16 mx-auto bg-emerald-500 rounded-lg animate-bounce shadow-[0_0_15px_rgba(16,185,129,0.6)]"></div>
        </Card>

        {/* Wiggle */}
        <Card className="p-4 text-center">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Wiggle</h4>
          <div className="w-16 h-16 mx-auto bg-orange-500 rounded-lg animate-[wiggle_1s_ease-in-out_infinite] shadow-[0_0_15px_rgba(249,115,22,0.4)]"></div>
        </Card>

        {/* Float */}
        <Card className="p-4 text-center">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Float</h4>
          <div className="w-16 h-16 mx-auto bg-pink-500 rounded-lg animate-[float_3s_ease-in-out_infinite] shadow-[0_0_15px_rgba(236,72,153,0.4)]"></div>
        </Card>

        {/* Rotate */}
        <Card className="p-4 text-center">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Rotate</h4>
          <div className="w-16 h-16 mx-auto bg-red-500 rounded-lg animate-spin shadow-[0_0_15px_rgba(239,68,68,0.4)]"></div>
        </Card>
      </div>

      {/* Custom Animations CSS */}
      <Card className="p-4">
        <h4 className="text-sm font-medium mb-3">Custom Animations (Add to CSS)</h4>
        <CodeDisplay
          code={`@keyframes fadeIn {
  0% { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
  0%, 100% { transform: translateY(20px); }
  50% { transform: translateY(0); }
}

@keyframes wiggle {
  0%, 100% { transform: rotate(-3deg); }
  50% { transform: rotate(3deg); }
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}`}
          showLineNumbers={false}
        />
      </Card>
    </div>
  );

  const renderContent = () => {
    switch (activeOption) {
      case 'Interaction':
        return renderOption1();
      case 'Loading':
        return renderOption2();
      case 'Neon':
        return renderOption3();
      case 'Animation':
        return renderOption4();
      default:
        return renderOption1();
    }
  };

  const generateCode = () => {
    switch (activeOption) {
      case 'Interaction':
        return `// Hover & Interaction Effects
<button className="hover:shadow-[0_0_20px_rgba(34,211,238,0.6)] transition-all duration-300">
  Glow Hover
</button>

<div className="hover:scale-110 transition-transform duration-200">
  Scale Hover
</div>

<div className="hover:border-cyan-500 hover:shadow-[0_0_15px_rgba(34,211,238,0.5)] transition-all duration-300">
  Neon Border Hover
</div>

<div className="text-cyan-500 hover:drop-shadow-[0_0_8px_rgba(34,211,238,0.8)] transition-all duration-300">
  Glowing Text
</div>`;

      case 'Loading':
        return `// Tron-style Loading Effects
<div className="w-12 h-12 border-2 border-transparent border-t-cyan-500 border-r-cyan-500 rounded-full animate-spin shadow-[0_0_15px_rgba(34,211,238,0.5)]"></div>

<div className="w-full bg-gray-800 border border-gray-600 rounded-full h-3 shadow-inner">
  <div className="bg-gradient-to-r from-cyan-500 to-emerald-500 h-full rounded-full shadow-[0_0_10px_rgba(34,211,238,0.6)] animate-pulse" style="width: 60%"></div>
</div>

<div className="space-y-2">
  <div className="h-4 bg-gradient-to-r from-gray-700 to-gray-600 rounded animate-pulse shadow-[0_0_5px_rgba(34,211,238,0.3)]"></div>
  <div className="h-3 bg-gradient-to-r from-gray-700 to-gray-600 rounded w-3/4 animate-pulse shadow-[0_0_5px_rgba(34,211,238,0.3)]"></div>
</div>`;

      case 'Neon':
        return `// Gradient & Neon Effects
<div className="bg-gradient-to-r from-purple-500 via-cyan-500 to-emerald-500 p-[2px] rounded-lg">
  <div className="bg-gray-900 rounded-md p-4">Gradient Border</div>
</div>

<span className="text-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.8)] font-bold">
  NEON TEXT
</span>

<div className="w-12 h-12 bg-cyan-500 rounded-full shadow-[0_0_30px_rgba(34,211,238,0.8),_0_0_60px_rgba(34,211,238,0.4)] animate-pulse">
</div>

<div
  className="w-full h-16 rounded-lg border border-cyan-500/50"
  style={{
    backgroundImage: \`
      linear-gradient(rgba(34, 211, 238, 0.1) 1px, transparent 1px),
      linear-gradient(90deg, rgba(34, 211, 238, 0.1) 1px, transparent 1px)
    \`,
    backgroundSize: '10px 10px'
  }}
></div>`;

      case 'Animation':
        return `// Motion & Animation Effects
<div className="bg-gradient-to-br from-purple-500 to-emerald-500 rounded-lg animate-[fadeIn_2s_ease-in-out_infinite] shadow-[0_0_15px_rgba(168,85,247,0.4)]">
  Fade In
</div>

<div className="bg-gradient-to-br from-cyan-500 to-emerald-500 rounded-lg animate-[slideUp_2s_ease-in-out_infinite] shadow-[0_0_15px_rgba(34,211,238,0.4)]">
  Slide Up
</div>

<div className="bg-emerald-500 rounded-lg animate-bounce shadow-[0_0_15px_rgba(16,185,129,0.6)]">
  Bounce
</div>

<div className="bg-pink-500 rounded-lg animate-[float_3s_ease-in-out_infinite] shadow-[0_0_15px_rgba(236,72,153,0.4)]">
  Float
</div>`;

      default:
        return '';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Effects System</h2>
        <p className="text-gray-600 dark:text-gray-400 text-lg">
          Animation, interaction, and visual effects library
        </p>
      </div>

      {/* Option Tabs */}
      <div className="flex justify-center">
        <div className="backdrop-blur-sm bg-white/40 dark:bg-white/5 border border-white/30 dark:border-white/15 rounded-full p-1 shadow-lg">
          <div className="flex gap-1 items-center">
            {EFFECT_OPTIONS.map((option) => (
              <button
                key={option}
                onClick={() => setActiveOption(option)}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-200",
                  "text-sm font-medium whitespace-nowrap",
                  activeOption === option
                    ? "bg-cyan-500/20 dark:bg-cyan-400/20 text-cyan-700 dark:text-cyan-300 border border-cyan-400/50 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                    : "text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5"
                )}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <Card className="p-8">
        {renderContent()}

        {/* Generated Code */}
        <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Generated Code</h4>
          <CodeDisplay
            code={generateCode()}
            showLineNumbers={false}
          />
        </div>
      </Card>
    </div>
  );
};