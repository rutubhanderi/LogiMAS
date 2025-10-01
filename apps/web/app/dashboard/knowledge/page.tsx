import { AgentChat } from "../../../components/ui/AgentChat";

export default function KnowledgeBasePage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        Knowledge Base & General Queries
      </h1>

      <p className="mb-6 text-gray-600 max-w-3xl">
        This chat interface is connected to the LogiMAS multi-agent system. You
        can ask general questions that will be answered by our RAG-enabled
        agents using the knowledge base of incident reports and other documents.
      </p>

      <AgentChat />
    </div>
  );
}
