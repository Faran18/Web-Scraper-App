//frontend/src/components/reminders/CreateReminderModal.jsx

import { useState } from 'react';
import { X, Bell } from 'lucide-react';

export default function CreateReminderModal({ isOpen, onClose, onSubmit }) {
  const [url, setUrl] = useState('');
  const [email, setEmail] = useState('');
  const [intervalHours, setIntervalHours] = useState(24);
  const [cssSelector, setCssSelector] = useState('');
  const [xpath, setXpath] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!url.trim() || !email.trim()) {
      return;
    }

    setLoading(true);
    try {
      const data = {
        url: url.trim(),
        email: email.trim(),
        interval_hours: intervalHours,
      };

      if (cssSelector.trim()) {
        data.css_selector = cssSelector.trim();
      }
      if (xpath.trim()) {
        data.xpath = xpath.trim();
      }

      await onSubmit(data);
      
      // Reset form
      setUrl('');
      setEmail('');
      setIntervalHours(24);
      setCssSelector('');
      setXpath('');
      setShowAdvanced(false);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setUrl('');
    setEmail('');
    setIntervalHours(24);
    setCssSelector('');
    setXpath('');
    setShowAdvanced(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto custom-scrollbar animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 sticky top-0 bg-white z-10">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <Bell className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Create Reminder</h2>
          </div>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* URL */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Website URL *
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            />
            <p className="text-xs text-gray-500 mt-1">
              The website you want to monitor
            </p>
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Email Address *
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            />
            <p className="text-xs text-gray-500 mt-1">
              Where to send change notifications
            </p>
          </div>

          {/* Check Interval */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Check Every (hours) *
            </label>
            <input
              type="number"
              value={intervalHours}
              onChange={(e) => setIntervalHours(Math.max(1, parseInt(e.target.value) || 1))}
              min="1"
              max="168"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            />
            <p className="text-xs text-gray-500 mt-1">
              How often to check for changes (1-168 hours)
            </p>
          </div>

          {/* Advanced Options Toggle */}
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-purple-600 hover:text-purple-700 font-medium"
          >
            {showAdvanced ? '− Hide' : '+ Show'} Advanced Options
          </button>

          {/* Advanced Options */}
          {showAdvanced && (
            <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  CSS Selector (Optional)
                </label>
                <input
                  type="text"
                  value={cssSelector}
                  onChange={(e) => setCssSelector(e.target.value)}
                  placeholder=".content, #main"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Target specific elements only
                </p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  XPath (Optional)
                </label>
                <input
                  type="text"
                  value={xpath}
                  onChange={(e) => setXpath(e.target.value)}
                  placeholder="//div[@class='content']"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Alternative to CSS selector
                </p>
              </div>
            </div>
          )}

          {/* Info Box */}
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <p className="text-sm text-purple-800">
              💡 You'll receive an email whenever the content at this URL changes
            </p>
          </div>

          {/* Actions */}
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !url.trim() || !email.trim()}
              className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create Reminder'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}