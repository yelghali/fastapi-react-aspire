/**
 * Home page - landing page for the starter template.
 */

import type { MetaFunction } from "react-router";
import { Link } from "react-router";
import {
  HiOutlineCollection,
  HiOutlineCode,
  HiOutlineServer,
} from "react-icons/hi";

export const meta: MetaFunction = () => {
  return [
    { title: "FastAPI React Aspire Starter" },
    {
      name: "description",
      content:
        "A minimal starter template with FastAPI, React Router v7, and .NET Aspire",
    },
  ];
};

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-zinc-200 dark:border-zinc-800">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold">🚀 Starter Template</h1>
          <nav className="flex gap-4">
            <Link
              to="/items"
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              Items Demo
            </Link>
            <a
              href="/docs"
              className="text-blue-600 dark:text-blue-400 hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              API Docs
            </a>
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-5xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">FastAPI + React + Aspire</h2>
          <p className="text-xl text-zinc-600 dark:text-zinc-400 max-w-2xl mx-auto">
            A minimal, production-ready starter template with distributed
            tracing, type safety, and easy Azure deployment.
          </p>
        </div>

        {/* Feature cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <FeatureCard
            icon={<HiOutlineServer className="w-8 h-8" />}
            title="FastAPI Backend"
            description="Python API with OpenTelemetry tracing, Pydantic validation, and async support."
          />
          <FeatureCard
            icon={<HiOutlineCode className="w-8 h-8" />}
            title="React Router v7"
            description="Modern React with SSR, TypeScript, Tailwind CSS, and browser telemetry."
          />
          <FeatureCard
            icon={<HiOutlineCollection className="w-8 h-8" />}
            title=".NET Aspire"
            description="Local orchestration with dashboard, and one-command Azure deployment."
          />
        </div>

        {/* Quick start */}
        <div className="bg-zinc-100 dark:bg-zinc-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Quick Start</h3>
          <div className="space-y-3 font-mono text-sm">
            <CodeBlock>
              git clone https://github.com/sethjuarez/fastapi-react-aspire
            </CodeBlock>
            <CodeBlock>cd fastapi-react-aspire</CodeBlock>
            <CodeBlock>aspire run</CodeBlock>
          </div>
          <p className="mt-4 text-zinc-600 dark:text-zinc-400 text-sm">
            Open the Aspire dashboard to see traces, logs, and metrics from both
            frontend and backend.
          </p>
        </div>

        {/* CTA */}
        <div className="text-center mt-12">
          <Link
            to="/items"
            className="inline-block px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try the Items Demo →
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-200 dark:border-zinc-800 py-6">
        <div className="max-w-5xl mx-auto px-4 text-center text-zinc-500 dark:text-zinc-400 text-sm">
          Built with FastAPI, React Router v7, and .NET Aspire
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="border border-zinc-200 dark:border-zinc-700 rounded-lg p-6">
      <div className="text-blue-600 dark:text-blue-400 mb-3">{icon}</div>
      <h3 className="font-semibold mb-2">{title}</h3>
      <p className="text-sm text-zinc-600 dark:text-zinc-400">{description}</p>
    </div>
  );
}

function CodeBlock({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-zinc-900 text-zinc-100 px-4 py-2 rounded">
      <code>$ {children}</code>
    </div>
  );
}

