import api from './api';

export const authService = {
  signup: async (email, password, full_name) => {
    const response = await api.post('/auth/signup', { email, password, full_name });
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  me: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },

  deleteMe: async () => {
    const response = await api.delete('/auth/me');
    return response.data;
  },
};
