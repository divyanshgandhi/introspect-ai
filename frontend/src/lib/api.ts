// API endpoints
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Types for API requests and responses
export interface UserContext {
  interests: string;
  goals: string;
  background: string;
}

export interface Insight {
  point: string;
  type: 'actionable' | 'fact' | 'quote';
}

export interface ExtractedData {
  title: string;
  summary: string;
  insights: Insight[];
}

export interface PersonalizeRequest {
  extracted_data: ExtractedData;
  user_context: UserContext;
}

export interface PromptResponse {
  prompt: string;
}

export interface ProcessResponse {
  extracted_data: ExtractedData;
  prompt: string;
}

export interface APIError {
  status: number;
  message: string;
  detail?: string;
}

/**
 * Parse the error response from the API
 */
async function parseErrorResponse(response: Response): Promise<APIError> {
  let errorMessage = 'An unexpected error occurred';
  let detail: string | undefined;
  
  try {
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || 'Server error';
      detail = errorData.detail;
    } else {
      errorMessage = await response.text() || `Error: ${response.status} ${response.statusText}`;
    }
  } catch (e) {
    errorMessage = `Error: ${response.status} ${response.statusText}`;
  }
  
  return {
    status: response.status,
    message: errorMessage,
    detail
  };
}

/**
 * Extract insights from content (file or YouTube URL)
 */
export async function extractContent(file?: File, youtubeUrl?: string): Promise<ExtractedData> {
  try {
    const formData = new FormData();
    
    if (file) {
      formData.append('file', file);
    }
    
    if (youtubeUrl) {
      formData.append('youtube_url', youtubeUrl);
    }
    
    const response = await fetch(`${API_URL}/api/extract`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const error = await parseErrorResponse(response);
      throw new Error(error.message);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error extracting content:', error);
    if (error instanceof Error) {
      throw error;
    } else {
      throw new Error('Failed to extract content from the provided source');
    }
  }
}

/**
 * Generate a personalized prompt from extracted insights and user context
 */
export async function personalizeContent(
  extractedData: ExtractedData, 
  userContext: UserContext
): Promise<PromptResponse> {
  try {
    const response = await fetch(`${API_URL}/api/personalize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        extracted_data: extractedData,
        user_context: userContext,
      }),
    });
    
    if (!response.ok) {
      const error = await parseErrorResponse(response);
      throw new Error(error.message);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error personalizing content:', error);
    if (error instanceof Error) {
      throw error;
    } else {
      throw new Error('Failed to personalize content with your information');
    }
  }
}

/**
 * Process content in a single API call (extract and personalize)
 */
export async function processContent(
  file: File | null, 
  youtubeUrl: string | null, 
  userContext: UserContext
): Promise<ProcessResponse> {
  try {
    const formData = new FormData();
    
    if (file) {
      formData.append('file', file);
    }
    
    if (youtubeUrl) {
      formData.append('youtube_url', youtubeUrl);
    }
    
    // Add user context fields
    formData.append('interests', userContext.interests);
    formData.append('goals', userContext.goals);
    formData.append('background', userContext.background);
    
    const response = await fetch(`${API_URL}/api/process`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const error = await parseErrorResponse(response);
      if (response.status === 500) {
        throw new Error('The server encountered an error while processing your content. Please try again later or use a different YouTube link.');
      }
      throw new Error(error.message);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error processing content:', error);
    if (error instanceof Error) {
      throw error;
    } else {
      throw new Error('Failed to process content. Please try again with a different link.');
    }
  }
} 