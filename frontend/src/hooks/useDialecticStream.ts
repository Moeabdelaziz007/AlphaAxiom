import { useEffect, useState } from 'react';

interface DialecticData {
  coreText: string;
  shadowText: string;
  decision: string | null;
}

export const useDialecticStream = () => {
  const [dialecticData, setDialecticData] = useState<DialecticData>({
    coreText: '',
    shadowText: '',
    decision: null
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Connect to the actual API endpoint
    const eventSource = new EventSource('/api/dialectic');
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'CORE_TOKEN') {
          setDialecticData(prev => ({
            ...prev,
            coreText: data.payload
          }));
        } else if (data.type === 'SHADOW_TOKEN') {
          setDialecticData(prev => ({
            ...prev,
            shadowText: data.payload
          }));
        } else if (data.type === 'DECISION') {
          setDialecticData(prev => ({
            ...prev,
            decision: data.payload
          }));
        } else if (data.type === 'CONNECTED') {
          setIsLoading(false);
        }
      } catch (err) {
        console.error('Error parsing SSE data:', err);
      }
    };
    
    eventSource.onerror = (err) => {
      console.error('SSE Error:', err);
      setError('Failed to connect to dialectic stream');
      setIsLoading(false);
    };
    
    return () => {
      eventSource.close();
    };
  }, []);

  return { ...dialecticData, isLoading, error };
};