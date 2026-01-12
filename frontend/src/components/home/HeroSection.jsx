import { Link } from 'react-router-dom';
import { Bot, Bell } from 'lucide-react';

export default function HeroSection() {
  return (
    <section className="text-center space-y-8 py-12">
      <div className="animate-fade-in">
        <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-primary-600 via-secondary-600 to-primary-600 bg-clip-text text-transparent mb-4">
          AI-Powered Web Intelligence
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Transform any website into an intelligent agent. Monitor changes, chat with content, and automate your workflow.
        </p>
      </div>

      {/* CTA Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-slide-up">
        <Link
          to="/agents"
          className="px-8 py-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl font-semibold hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex items-center space-x-2"
        >
          <Bot className="w-5 h-5" />
          <span>Create Your First Agent</span>
        </Link>
        <Link
          to="/reminders"
          className="px-8 py-4 bg-white text-gray-700 border-2 border-gray-300 rounded-xl font-semibold hover:border-primary-500 hover:text-primary-600 transition-all duration-300 flex items-center space-x-2"
        >
          <Bell className="w-5 h-5" />
          <span>Set Up Reminders</span>
        </Link>
      </div>
    </section>
  );
}