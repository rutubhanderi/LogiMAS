import { AgentChat } from "../components/ui/AgentChat";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center p-4">
      <div className="text-center mb-10">
        <h1 className="text-5xl font-extrabold tracking-tight lg:text-6xl">
          LogiMAS Platform
        </h1>
        <p className="mt-4 text-lg text-slate-400">
          The Retrieval-Augmented Multi-Agent System for Logistics Optimization
        </p>
      </div>

      <AgentChat />
    </main>
  );
}