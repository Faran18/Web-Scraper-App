import { useState } from "react";
import toast from "react-hot-toast";
import { authService } from "../services/authService";
import { useNavigate } from "react-router-dom";

export default function Settings() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onLogout = async () => {
    setLoading(true);
    try {
      await authService.logout();
      toast.success("Logged out");
      navigate("/login", { replace: true });
    } catch {
      toast.error("Logout failed");
    } finally {
      setLoading(false);
    }
  };

  const onDelete = async () => {
    const ok = window.confirm(
      "Delete your account permanently? This cannot be undone."
    );
    if (!ok) return;

    setLoading(true);
    try {
      await authService.deleteAccount();
      toast.success("Account deleted");
      navigate("/login", { replace: true });
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Delete failed (API not ready?)");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Account actions</p>

        <div className="mt-6 flex flex-col sm:flex-row gap-3">
          <button
            onClick={onLogout}
            disabled={loading}
            className="px-5 py-3 rounded-lg font-semibold bg-gray-900 text-white hover:bg-black disabled:opacity-60"
          >
            Logout
          </button>

          <button
            onClick={onDelete}
            disabled={loading}
            className="px-5 py-3 rounded-lg font-semibold bg-red-600 text-white hover:bg-red-700 disabled:opacity-60"
          >
            Delete Account
          </button>
        </div>
      </div>
    </div>
  );
}
