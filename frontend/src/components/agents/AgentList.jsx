import { Loader2 } from 'lucide-react';
import AgentCard from './AgentCard';

export default function AgentList({ 
  agents, 
  loading, 
  onDelete, 
  onToggleStatus, 
  onUpdate 
}) {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    );
  }

  if (agents.length === 0) {
    return (
      <div className="text-center py-20 bg-white rounded-xl shadow-sm">
        <p className="text-gray-500 text-lg">
          No agents found. Create your first agent to get started!
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {agents.map((agent) => (
        <AgentCard
          key={agent.agent_id}
          agent={agent}
          onDelete={onDelete}
          onToggleStatus={onToggleStatus}
          onUpdate={onUpdate}
        />
      ))}
    </div>
  );
}