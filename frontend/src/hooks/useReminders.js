//frontend/src/hooks/useReminders.js

import { useState, useEffect } from 'react';
import { reminderService } from '../services/reminderService';
import toast from 'react-hot-toast';

export function useReminders(activeOnly = true) {
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReminders = async () => {
    try {
      setLoading(true);
      const response = await reminderService.getReminders(activeOnly);
      setReminders(response.reminders || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      toast.error('Failed to fetch reminders');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReminders();
  }, [activeOnly]);

  return { reminders, loading, error, refetch: fetchReminders };
}