//frontend/src/components/reminders/ReminderCard.jsx

import { Mail, Clock, Trash2, Power, Play, ExternalLink } from 'lucide-react';

export default function ReminderCard({ reminder, onDelete, onToggleStatus, onTriggerNow }) {
  const getDomainFromUrl = (url) => {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname;
    } catch {
      return url;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden card-hover">
      {/* Header */}
      <div className="p-6 bg-gradient-to-br from-purple-500 to-pink-500">
        <div className="flex justify-between items-start mb-2">
          <div className="flex-1">
            <h3 className="text-lg font-bold text-white truncate">
              {getDomainFromUrl(reminder.url)}
            </h3>
            <a
              href={reminder.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-purple-100 text-xs hover:text-white transition-colors flex items-center space-x-1 mt-1"
            >
              <span className="truncate">{reminder.url}</span>
              <ExternalLink className="w-3 h-3 flex-shrink-0" />
            </a>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold ml-2 flex-shrink-0 ${
              reminder.is_active
                ? 'bg-green-400 text-green-900'
                : 'bg-gray-400 text-gray-900'
            }`}
          >
            {reminder.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-4">
        {/* Info */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Mail className="w-4 h-4 text-purple-500" />
            <span className="truncate">{reminder.email}</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Clock className="w-4 h-4 text-purple-500" />
            <span>Check every {reminder.interval_hours}h</span>
          </div>
        </div>

        {/* Last Scraped */}
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-xs text-gray-600 mb-1 font-medium">
            Last Checked
          </div>
          <p className="text-sm font-semibold text-gray-900">
            {reminder.last_scraped
              ? new Date(reminder.last_scraped).toLocaleString()
              : 'Never'}
          </p>
        </div>

        {/* Selectors */}
        {(reminder.css_selector || reminder.xpath) && (
          <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
            {reminder.css_selector && (
              <div>CSS: {reminder.css_selector}</div>
            )}
            {reminder.xpath && (
              <div>XPath: {reminder.xpath}</div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="space-y-2">
          <button
            onClick={() => onTriggerNow(reminder.reminder_id)}
            disabled={!reminder.is_active}
            className="w-full px-4 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all duration-300 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="w-5 h-5" />
            <span>Check Now</span>
          </button>

          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => onToggleStatus(reminder.reminder_id, reminder.is_active)}
              className={`px-3 py-2 rounded-lg transition-colors flex items-center justify-center space-x-1 ${
                reminder.is_active
                  ? 'bg-orange-50 text-orange-600 hover:bg-orange-100'
                  : 'bg-green-50 text-green-600 hover:bg-green-100'
              }`}
              title={reminder.is_active ? 'Deactivate' : 'Activate'}
            >
              <Power className="w-4 h-4" />
              <span className="text-sm font-medium">
                {reminder.is_active ? 'Pause' : 'Activate'}
              </span>
            </button>
            <button
              onClick={() => onDelete(reminder.reminder_id)}
              className="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors flex items-center justify-center space-x-1"
              title="Delete"
            >
              <Trash2 className="w-4 h-4" />
              <span className="text-sm font-medium">Delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}