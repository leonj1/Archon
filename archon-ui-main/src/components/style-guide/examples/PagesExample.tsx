import { Card } from '@/features/ui/primitives/card';
import { CodeDisplay } from '../shared/CodeDisplay';

export const PagesExample = () => {
  const generateCode = () => {
    return `/**
 * 🤖 AI CONTEXT: Complete Page Examples
 *
 * PURPOSE: Full page layouts using Archon's design system
 * WHEN TO USE: Reference for building new pages with consistent styling
 * WHEN NOT TO USE: Component-level implementation
 *
 * PAGE TYPES:
 * - Landing pages with hero sections
 * - Dashboard pages with data visualization
 * - Settings pages with form layouts
 * - Profile pages with user information
 * - Error pages with helpful messaging
 *
 * COMPOSITION PRINCIPLES:
 * - Consistent spacing and typography
 * - Proper use of glassmorphism effects
 * - Responsive grid layouts
 * - Accessible navigation patterns
 */

// Example: Landing Page
export const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      {/* Hero Section */}
      <section className="py-20 text-center">
        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          Welcome to Archon
        </h1>
        <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
          Build beautiful applications with our glassmorphism design system
        </p>
        <Button size="lg" glowColor="purple">
          Get Started
        </Button>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {features.map((feature) => (
            <Card key={feature.id} glowColor="cyan" className="p-8 text-center">
              <feature.icon className="w-12 h-12 mx-auto mb-4" />
              <h3 className="text-xl font-bold mb-4">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
};`;
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Page Examples</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Complete page layouts demonstrating how to compose components into full user interfaces.
        </p>
      </div>

      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Coming Soon</h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          This section will include complete page examples such as:
        </p>
        <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1 mb-6">
          <li>Landing pages with hero sections and feature grids</li>
          <li>Dashboard pages with navigation and data visualization</li>
          <li>Settings pages with form layouts and preferences</li>
          <li>Profile pages with user information and actions</li>
          <li>Error pages with helpful messaging and navigation</li>
        </ul>
      </Card>

      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Example Code Structure</h3>
        <CodeDisplay
          code={generateCode()}
          
          showLineNumbers
        />
      </Card>
    </div>
  );
};