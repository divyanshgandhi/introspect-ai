import { RateLimitStatus } from '@/lib/api';

interface RateLimitDisplayProps {
  rateLimitStatus: RateLimitStatus | null;
  isRateLimited?: boolean;
  className?: string;
}

const RateLimitDisplay = ({ 
  rateLimitStatus, 
  isRateLimited = false,
  className = "" 
}: RateLimitDisplayProps) => {
  if (isRateLimited) {
    return (
      <div className={`text-sm text-red-600 mt-2 ${className}`}>
        <p className="font-medium">You have exhausted your free requests.</p>
        <p className='items-center'>
          Reach out to 
          <a 
            href="https://www.x.com/divyanshgandhi" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline"
          >
            @divyanshgandhi
          </a>
        </p>
      </div>
    );
  }

  if (!rateLimitStatus) {
    return null;
  }

  const { remaining_requests, max_requests } = rateLimitStatus;

  if (remaining_requests === 0) {
    return (
      <div className={`text-sm text-red-600 mt-2 ${className}`}>
        <p className="font-medium">You have exhausted your free requests.</p>
        <p>
          Reach out to{' '}
          <a 
            href="https://www.x.com/divyanshgandhi" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline"
          >
            @divyanshgandhi
          </a>
        </p>
      </div>
    );
  }

  return (
    <div className={`text-sm text-muted-foreground mt-2 ${className}`}>
      <p>
        {remaining_requests} of {max_requests} free requests remaining
      </p>
    </div>
  );
};

export default RateLimitDisplay; 