import { useNavigate } from 'react-router-dom';
import { MessageSquare, Trash2, Edit, Power, Database } from 'lucide-react';

export default function AgentCard({ agent, onDelete, onToggleStatus, onUpdate }) {
  const navigate = useNavigate();

  const handleChatClick = () => {
    navigate(`/agents/${agent.agent_id}/chat`);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden card-hover">
      {/* Header */}
      <div className="p-6 bg-gradient-to-br from-primary-500 to-secondary-500">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-xl font-bold text-white truncate">
            {agent.name}
          </h3>
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold ${
              agent.status === 'active'
                ? 'bg-green-400 text-green-900'
                : 'bg-gray-400 text-gray-900'
            }`}
          >
            {agent.status}
          </span>
        </div>
        <p className="text-primary-100 text-sm line-clamp-2">
          {agent.role}
        </p>
      </div>

      {/* Content */}
      <div className="p-6 space-y-4">
        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-center text-gray-600 mb-1">
              <Database className="w-4 h-4 mr-1" />
              <span className="text-xs font-medium">Chunks</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {agent.chunks_count || 0}
            </p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-600 mb-1 font-medium">
              Last Scraped
            </div>
            <p className="text-sm font-semibold text-gray-900">
              {agent.last_scraped
                ? new Date(agent.last_scraped).toLocaleDateString()
                : 'Never'}
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-2">
          <button
            onClick={handleChatClick}
            className="w-full px-4 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all duration-300 flex items-center justify-center space-x-2"
          >
            <MessageSquare className="w-5 h-5" />
            <span>Chat</span>
          </button>

          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => onUpdate(agent)}
              className="px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors flex items-center justify-center"
              title="Edit"
            >
              <Edit className="w-4 h-4" />
            </button>
            <button
              onClick={() => onToggleStatus(agent.agent_id, agent.status)}
              className={`px-3 py-2 rounded-lg transition-colors flex items-center justify-center ${
                agent.status === 'active'
                  ? 'bg-orange-50 text-orange-600 hover:bg-orange-100'
                  : 'bg-green-50 text-green-600 hover:bg-green-100'
              }`}
              title={agent.status === 'active' ? 'Deactivate' : 'Activate'}
            >
              <Power className="w-4 h-4" />
            </button>
            <button
              onClick={() => onDelete(agent.agent_id)}
              className="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors flex items-center justify-center"
              title="Delete"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}