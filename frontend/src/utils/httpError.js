export function getApiErrorMessage(err, fallback = 'Something went wrong') {
  const data = err?.response?.data;

  if (typeof data === 'string') return data;
  if (data?.detail) {
    if (typeof data.detail === 'string') return data.detail;
    return JSON.stringify(data.detail);
  }

  if (data?.message) return data.message;

  return err?.message || fallback;
}
