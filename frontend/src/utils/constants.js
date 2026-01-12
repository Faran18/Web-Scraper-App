export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

export const AGENT_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
};

export const REMINDER_INTERVALS = [
  { value: 1, label: '1 hour' },
  { value: 6, label: '6 hours' },
  { value: 12, label: '12 hours' },
  { value: 24, label: '24 hours (1 day)' },
  { value: 48, label: '48 hours (2 days)' },
  { value: 168, label: '1 week' },
];

export const ROUTES = {
  HOME: '/',
  AGENTS: '/agents',
  REMINDERS: '/reminders',
  CHAT: (agentId) => `/agents/${agentId}/chat`,
};