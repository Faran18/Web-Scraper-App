import { useState, useEffect } from 'react';
import { Plus, Search } from 'lucide-react';
import toast from 'react-hot-toast';
import { reminderService } from '../services/reminderService';
import ReminderList from '../components/reminders/ReminderList';
import CreateReminderModal from '../components/reminders/CreateReminderModal';

export default function Reminders() {
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterActive, setFilterActive] = useState(true);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  useEffect(() => {
    fetchReminders();
  }, [filterActive]);

  const fetchReminders = async () => {
    try {
      setLoading(true);
      const response = await reminderService.getReminders(filterActive);
      setReminders(response.reminders || []);
    } catch (error) {
      toast.error('Failed to fetch reminders');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateReminder = async (data) => {
    try {
      await reminderService.createReminder(data);
      toast.success('Reminder created successfully!');
      setCreateModalOpen(false);
      fetchReminders();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create reminder');
      console.error(error);
    }
  };

  const handleDeleteReminder = async (reminderId) => {
    if (!window.confirm('Are you sure you want to delete this reminder?')) {
      return;
    }

    try {
      await reminderService.deleteReminder(reminderId);
      toast.success('Reminder deleted successfully');
      fetchReminders();
    } catch (error) {
      toast.error('Failed to delete reminder');
      console.error(error);
    }
  };

  const handleToggleStatus = async (reminderId, isActive) => {
    try {
      await reminderService.toggleReminder(reminderId, !isActive);
      toast.success(`Reminder ${!isActive ? 'activated' : 'deactivated'}`);
      fetchReminders();
    } catch (error) {
      toast.error('Failed to update status');
      console.error(error);
    }
  };

  const handleTriggerNow = async (reminderId) => {
    try {
      const loadingToast = toast.loading('Checking for changes...', { id: 'trigger' });
      
      const response = await reminderService.triggerNow(reminderId);
      
      // Dismiss loading toast
      toast.dismiss(loadingToast);
      
      // Show appropriate message based on result
      if (response.result?.status === 'changed') {
        toast.success(response.message || 'Changes detected! Email sent.', { 
          duration: 5000,
          id: 'trigger' 
        });
      } else if (response.result?.status === 'no_change') {
        toast.success(response.message || 'No changes detected.', { 
          duration: 4000,
          id: 'trigger' 
        });
      } else if (response.result?.status === 'no_content') {
        toast.error(response.message || 'Could not extract content.', { 
          duration: 4000,
          id: 'trigger' 
        });
      } else {
        toast.success(response.message || 'Check completed!', { 
          duration: 3000,
          id: 'trigger' 
        });
      }
      
      fetchReminders();
    } catch (error) {
      toast.error('Failed to trigger reminder', { id: 'trigger' });
      console.error(error);
    }
  };

  const filteredReminders = reminders.filter(reminder =>
    reminder.url.toLowerCase().includes(searchTerm.toLowerCase()) ||
    reminder.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reminders</h1>
          <p className="text-gray-600 mt-1">
            Monitor websites and get email notifications on changes
          </p>
        </div>
        <button
          onClick={() => setCreateModalOpen(true)}
          className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold hover:shadow-lg transition-all duration-300 flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Create Reminder</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-xl shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by URL or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filterActive}
                onChange={(e) => setFilterActive(e.target.checked)}
                className="w-4 h-4 text-purple-500 rounded focus:ring-purple-500"
              />
              <span className="text-gray-700">Active only</span>
            </label>
          </div>
        </div>
      </div>

      {/* Reminders List Component */}
      <ReminderList
        reminders={filteredReminders}
        loading={loading}
        onDelete={handleDeleteReminder}
        onToggleStatus={handleToggleStatus}
        onTriggerNow={handleTriggerNow}
      />

      {/* Create Modal */}
      <CreateReminderModal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSubmit={handleCreateReminder}
      />
    </div>
  );
}