//frontend/src/components/reminders/ReminderList.jsx

import { Loader2 } from 'lucide-react';
import ReminderCard from './ReminderCard';

export default function ReminderList({ 
  reminders, 
  loading, 
  onDelete, 
  onToggleStatus, 
  onTriggerNow 
}) {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
      </div>
    );
  }

  if (reminders.length === 0) {
    return (
      <div className="text-center py-20 bg-white rounded-xl shadow-sm">
        <p className="text-gray-500 text-lg">
          No reminders found. Create your first reminder to get started!
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {reminders.map((reminder) => (
        <ReminderCard
          key={reminder.reminder_id}
          reminder={reminder}
          onDelete={onDelete}
          onToggleStatus={onToggleStatus}
          onTriggerNow={onTriggerNow}
        />
      ))}
    </div>
  );
}