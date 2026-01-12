//frontend/src/hooks/useAgents.js

import { useState, useEffect } from 'react';
import { agentService } from '../services/agentService';
import toast from 'react-hot-toast';

export function useAgents(status = null) {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const response = await agentService.getAgents(status);
      setAgents(response.agents || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      toast.error('Failed to fetch agents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, [status]);

  return { agents, loading, error, refetch: fetchAgents };
}