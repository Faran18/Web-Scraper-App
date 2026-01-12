import { Link } from 'react-router-dom';
import { Home, AlertCircle } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
      <AlertCircle className="w-24 h-24 text-gray-300" />
      <div className="space-y-2">
        <h1 className="text-6xl font-bold text-gray-900">404</h1>
        <h2 className="text-2xl font-semibold text-gray-700">Page Not Found</h2>
        <p className="text-gray-500">
          The page you're looking for doesn't exist.
        </p>
      </div>
      <Link
        to="/"
        className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl font-semibold hover:shadow-lg transition-all duration-300 flex items-center space-x-2"
      >
        <Home className="w-5 h-5" />
        <span>Go Home</span>
      </Link>
    </div>
  );
}