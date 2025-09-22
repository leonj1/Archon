import React, { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { Switch } from '@/features/ui/primitives/switch';
import { Input } from '@/features/ui/primitives/input';
import { Label } from '@/features/ui/primitives/label';
import { CodeDisplay } from '../shared/CodeDisplay';
import {
  ArrowRight, Zap, Shield, Sparkles,
  BarChart, Users, DollarSign, TrendingUp,
  User, Bell, Lock, Palette, Globe, Database
} from 'lucide-react';

// Landing Page Example
const LandingPageExample = () => {
  return (
    <div className="relative overflow-hidden rounded-lg">
      <div className="bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 p-8">
        {/* Hero Section */}
        <section className="text-center py-12">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            Welcome to Archon
          </h1>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            Build beautiful applications with our glassmorphism design system
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" className="shadow-[0_0_20px_rgba(168,85,247,0.5)]">
              Get Started <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
            <Button variant="outline" size="lg">
              Learn More
            </Button>
          </div>
        </section>

        {/* Features Grid */}
        <section className="mt-12 grid grid-cols-3 gap-6">
          <Card accentColor="purple" className="p-6 text-center hover:scale-105 transition-transform">
            <Zap className="w-12 h-12 mx-auto mb-4 text-purple-400" />
            <h3 className="font-semibold mb-2">Lightning Fast</h3>
            <p className="text-sm text-gray-400">Optimized performance for modern applications</p>
          </Card>
          <Card accentColor="cyan" className="p-6 text-center hover:scale-105 transition-transform">
            <Shield className="w-12 h-12 mx-auto mb-4 text-cyan-400" />
            <h3 className="font-semibold mb-2">Secure by Default</h3>
            <p className="text-sm text-gray-400">Enterprise-grade security features built-in</p>
          </Card>
          <Card accentColor="pink" className="p-6 text-center hover:scale-105 transition-transform">
            <Sparkles className="w-12 h-12 mx-auto mb-4 text-pink-400" />
            <h3 className="font-semibold mb-2">Beautiful UI</h3>
            <p className="text-sm text-gray-400">Glassmorphic design that stands out</p>
          </Card>
        </section>
      </div>
    </div>
  );
};

// Dashboard Page Example
const DashboardPageExample = () => {
  return (
    <div className="p-6 space-y-6 bg-gray-900/50 rounded-lg">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Dashboard</h2>
          <p className="text-sm text-gray-400">Welcome back, Admin</p>
        </div>
        <Button>Download Report</Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card accentColor="green" className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Total Revenue</p>
              <p className="text-2xl font-bold">$45,231</p>
              <p className="text-xs text-green-400">+12.5% from last month</p>
            </div>
            <DollarSign className="w-8 h-8 text-green-400" />
          </div>
        </Card>
        <Card accentColor="blue" className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Active Users</p>
              <p className="text-2xl font-bold">2,543</p>
              <p className="text-xs text-blue-400">+23 new today</p>
            </div>
            <Users className="w-8 h-8 text-blue-400" />
          </div>
        </Card>
        <Card accentColor="purple" className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Conversion Rate</p>
              <p className="text-2xl font-bold">3.2%</p>
              <p className="text-xs text-purple-400">+0.5% this week</p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-400" />
          </div>
        </Card>
        <Card accentColor="orange" className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Active Projects</p>
              <p className="text-2xl font-bold">12</p>
              <p className="text-xs text-orange-400">3 pending review</p>
            </div>
            <BarChart className="w-8 h-8 text-orange-400" />
          </div>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        <Card className="col-span-2 p-6">
          <h3 className="font-semibold mb-4">Revenue Chart</h3>
          <div className="h-48 bg-gradient-to-t from-cyan-500/10 to-transparent rounded-lg flex items-end justify-around">
            {[40, 65, 45, 75, 55, 85, 70].map((height, i) => (
              <div
                key={i}
                className="w-8 bg-cyan-500/50 rounded-t"
                style={{ height: `${height}%` }}
              />
            ))}
          </div>
        </Card>
        <Card className="p-6">
          <h3 className="font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-green-400 rounded-full" />
              <span className="text-gray-400">New user registered</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-blue-400 rounded-full" />
              <span className="text-gray-400">Payment received</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-purple-400 rounded-full" />
              <span className="text-gray-400">Project completed</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

// Settings Page Example
const SettingsPageExample = () => {
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(true);
  const [autoSave, setAutoSave] = useState(false);

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <h2 className="text-2xl font-bold mb-6">Settings</h2>

      {/* Profile Section */}
      <Card accentColor="blue" className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <User className="w-5 h-5 text-blue-400" />
          <h3 className="text-lg font-semibold">Profile</h3>
        </div>
        <div className="space-y-4">
          <div>
            <Label htmlFor="name">Display Name</Label>
            <Input id="name" defaultValue="John Doe" className="mt-1" />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" defaultValue="john@example.com" className="mt-1" />
          </div>
        </div>
      </Card>

      {/* Preferences Section */}
      <Card accentColor="purple" className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Palette className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-semibold">Preferences</h3>
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="dark-mode">Dark Mode</Label>
              <p className="text-sm text-gray-400">Use dark theme across the application</p>
            </div>
            <Switch
              id="dark-mode"
              size="lg"
              color="purple"
              checked={darkMode}
              onCheckedChange={setDarkMode}
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="notifications">Notifications</Label>
              <p className="text-sm text-gray-400">Receive push notifications</p>
            </div>
            <Switch
              id="notifications"
              size="lg"
              color="purple"
              checked={notifications}
              onCheckedChange={setNotifications}
              iconOn={<Bell className="w-5 h-5" />}
              iconOff={<Bell className="w-5 h-5" />}
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="auto-save">Auto Save</Label>
              <p className="text-sm text-gray-400">Automatically save changes</p>
            </div>
            <Switch
              id="auto-save"
              size="lg"
              color="purple"
              checked={autoSave}
              onCheckedChange={setAutoSave}
            />
          </div>
        </div>
      </Card>

      {/* Security Section */}
      <Card accentColor="green" className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Lock className="w-5 h-5 text-green-400" />
          <h3 className="text-lg font-semibold">Security</h3>
        </div>
        <div className="space-y-4">
          <Button variant="outline" className="w-full justify-start">
            Change Password
          </Button>
          <Button variant="outline" className="w-full justify-start">
            Two-Factor Authentication
          </Button>
          <Button variant="outline" className="w-full justify-start text-red-500 hover:text-red-400">
            Delete Account
          </Button>
        </div>
      </Card>
    </div>
  );
};

export const PagesExample = () => {
  const [activeExample, setActiveExample] = useState<'landing' | 'dashboard' | 'settings'>('landing');

  const generateCode = () => {
    if (activeExample === 'dashboard') {
      return `// Dashboard Page with Stats Cards
import { Card } from '@/features/ui/primitives/card';
import { DollarSign, Users, TrendingUp, BarChart } from 'lucide-react';

export const Dashboard = () => {
  return (
    <div className="p-6 space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card accentColor="green" className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Revenue</p>
              <p className="text-2xl font-bold">$45,231</p>
            </div>
            <DollarSign className="w-8 h-8 text-green-400" />
          </div>
        </Card>
        {/* More stat cards... */}
      </div>
    </div>
  );
};`;
    } else if (activeExample === 'settings') {
      return `// Settings Page with Form Sections
import { Card } from '@/features/ui/primitives/card';
import { Switch } from '@/features/ui/primitives/switch';
import { Input } from '@/features/ui/primitives/input';

export const Settings = () => {
  const [darkMode, setDarkMode] = useState(true);

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <Card accentColor="purple" className="p-6">
        <h3 className="text-lg font-semibold mb-4">Preferences</h3>
        <div className="flex items-center justify-between">
          <Label htmlFor="dark-mode">Dark Mode</Label>
          <Switch
            id="dark-mode"
            size="lg"
            color="purple"
            checked={darkMode}
            onCheckedChange={setDarkMode}
          />
        </div>
      </Card>
    </div>
  );
};`;
    }

    return `// Landing Page with Hero Section
import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { ArrowRight, Zap, Shield, Sparkles } from 'lucide-react';

export const LandingPage = () => {
  return (
    <div className="bg-gradient-to-br from-gray-900 to-purple-900/20">
      {/* Hero Section */}
      <section className="text-center py-12">
        <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
          Welcome to Archon
        </h1>
        <Button size="lg">
          Get Started <ArrowRight className="ml-2 w-4 h-4" />
        </Button>
      </section>

      {/* Features Grid */}
      <section className="grid grid-cols-3 gap-6">
        <Card accentColor="purple" className="p-6 text-center">
          <Zap className="w-12 h-12 mx-auto mb-4 text-purple-400" />
          <h3 className="font-semibold">Lightning Fast</h3>
        </Card>
        {/* More feature cards... */}
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

      {/* Example Selector */}
      <div className="flex gap-2 mb-6">
        <Button
          variant={activeExample === 'landing' ? 'primary' : 'outline'}
          size="sm"
          onClick={() => setActiveExample('landing')}
        >
          Landing Page
        </Button>
        <Button
          variant={activeExample === 'dashboard' ? 'primary' : 'outline'}
          size="sm"
          onClick={() => setActiveExample('dashboard')}
        >
          Dashboard
        </Button>
        <Button
          variant={activeExample === 'settings' ? 'primary' : 'outline'}
          size="sm"
          onClick={() => setActiveExample('settings')}
        >
          Settings
        </Button>
      </div>

      {/* Live Example */}
      <Card className="p-0 overflow-hidden">
        <div className="max-h-96 overflow-auto">
          {activeExample === 'landing' && <LandingPageExample />}
          {activeExample === 'dashboard' && <DashboardPageExample />}
          {activeExample === 'settings' && <SettingsPageExample />}
        </div>
      </Card>

      {/* Code Example */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Implementation Code</h3>
        <CodeDisplay
          code={generateCode()}
          showLineNumbers
        />
      </Card>
    </div>
  );
};