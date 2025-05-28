import { useState, useEffect } from 'react';
import { getRateLimitStatus, RateLimitStatus } from '@/lib/api';

export function useRateLimit() {
  const [rateLimitStatus, setRateLimitStatus] = useState<RateLimitStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRateLimitStatus = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const status = await getRateLimitStatus();
      setRateLimitStatus(status);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get rate limit status';
      setError(errorMessage);
      console.error('Error fetching rate limit status:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch rate limit status on mount
  useEffect(() => {
    fetchRateLimitStatus();
  }, []);

  // Function to refresh rate limit status (call after API requests)
  const refreshRateLimitStatus = () => {
    fetchRateLimitStatus();
  };

  return {
    rateLimitStatus,
    isLoading,
    error,
    refreshRateLimitStatus,
  };
} 