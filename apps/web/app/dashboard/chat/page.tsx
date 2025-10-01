import { AgentChat } from "../../../components/ui/AgentChat";

export default function ChatPage() {
  return (
    // This div will take up the full height of the main content area
    <div className="h-full flex flex-col">
      <h1 className="text-3xl font-bold text-gray-800 mb-6 flex-shrink-0">
        Agent Chat
      </h1>

      {/* The AgentChat component will now expand to fill the remaining space */}
      <div className="flex-grow">
        <AgentChat />
      </div>
    </div>
  );
}
