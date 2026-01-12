export default function Card({ children, className = '', hover = false }) {
  return (
    <div
      className={`bg-white rounded-xl shadow-lg overflow-hidden ${
        hover ? 'card-hover' : ''
      } ${className}`}
    >
      {children}
    </div>
  );
}