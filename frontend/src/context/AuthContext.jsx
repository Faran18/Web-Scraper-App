import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthed, setIsAuthed] = useState(false);
  const [loading, setLoading] = useState(true);

  const refreshMe = async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      setUser(null);
      setIsAuthed(false);
      setLoading(false);
      return;
    }

    try {
      const res = await authService.me();
      const u = res?.user || null;
      setUser(u);
      setIsAuthed(!!u);
    } catch (e) {
      localStorage.removeItem('auth_token');
      setUser(null);
      setIsAuthed(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshMe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = async (email, password) => {
    const res = await authService.login(email, password);
    if (res?.token) localStorage.setItem('auth_token', res.token);
    await refreshMe();
    return res;
  };

  const signup = async (email, password, full_name) => {
    const res = await authService.signup(email, password, full_name);
    if (res?.token) localStorage.setItem('auth_token', res.token);
    await refreshMe();
    return res;
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch {
      // ignore
    }
    localStorage.removeItem('auth_token');
    setUser(null);
    setIsAuthed(false);
  };

  const deleteAccount = async () => {
    // ✅ FIX: call service (service uses api internally)
    await authService.deleteMe();

    // clear local state after delete
    localStorage.removeItem('auth_token');
    setUser(null);
    setIsAuthed(false);
  };

  const value = useMemo(
    () => ({
      user,
      isAuthed,
      loading,
      refreshMe,
      login,
      signup,
      logout,
      deleteAccount,
    }),
    [user, isAuthed, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
