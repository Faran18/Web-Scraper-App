//frontend/src/hooks/useToast.js

import toast from 'react-hot-toast';

export function useToast() {
  const success = (message) => {
    toast.success(message, {
      duration: 3000,
      position: 'top-right',
    });
  };

  const error = (message) => {
    toast.error(message, {
      duration: 4000,
      position: 'top-right',
    });
  };

  const loading = (message, id) => {
    return toast.loading(message, {
      id,
      position: 'top-right',
    });
  };

  const dismiss = (id) => {
    toast.dismiss(id);
  };

  const promise = (promise, messages) => {
    return toast.promise(
      promise,
      {
        loading: messages.loading,
        success: messages.success,
        error: messages.error,
      },
      {
        position: 'top-right',
      }
    );
  };

  return { success, error, loading, dismiss, promise };
}