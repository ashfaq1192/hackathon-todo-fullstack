// API Client with Retry Logic and JWT Authentication
// Production-ready HTTP client with exponential backoff retry (3 attempts: 1s, 2s, 4s)

class APIClient {
  private baseURL: string;
  private getAuthToken: () => string | null;

  constructor(baseURL: string, getAuthToken: () => string | null) {
    this.baseURL = baseURL;
    this.getAuthToken = getAuthToken;
  }

  /**
   * Make HTTP request with retry logic (3 attempts, exponential backoff)
   * Retries only on network errors, NOT on HTTP error status codes
   */
  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const token = this.getAuthToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options?.headers,
    };

    // Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)
    const maxRetries = 3;
    const retryDelays = [1000, 2000, 4000]; // milliseconds

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
          ...options,
          headers,
        });

        // Handle 401 Unauthorized - redirect to login
        if (response.status === 401) {
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          throw new Error('Unauthorized');
        }

        // Handle other HTTP errors
        if (!response.ok) {
          const error = await response.json().catch(() => ({
            detail: 'API request failed',
          }));
          throw new Error(error.detail || 'API request failed');
        }

        // Handle 204 No Content
        if (response.status === 204) {
          return null as T;
        }

        return response.json();
      } catch (error) {
        // Only retry on network errors, not on HTTP errors
        const isNetworkError =
          error instanceof TypeError && error.message === 'Failed to fetch';

        if (attempt < maxRetries && isNetworkError) {
          await new Promise(resolve =>
            setTimeout(resolve, retryDelays[attempt])
          );
          continue;
        }

        throw error;
      }
    }

    // This should never be reached due to the throw in the loop
    throw new Error('Max retries exceeded');
  }

  // Example CRUD methods

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async patch<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

// Helper function to get JWT token from localStorage
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('api_token');
}

// Export singleton instance
export const apiClient = new APIClient(
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  getAuthToken
);

/**
 * Initialize API token after login
 * Fetches JWT token from Better Auth session and stores in localStorage
 */
export async function initializeApiToken(): Promise<{ token: string; user_id: string } | null> {
  try {
    const response = await fetch('/api/token');
    if (!response.ok) {
      throw new Error('Failed to get API token');
    }

    const data = await response.json();

    // Store token in localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('api_token', data.token);
      localStorage.setItem('user_id', data.user_id);
    }

    return data;
  } catch (error) {
    console.error('Failed to initialize API token:', error);
    return null;
  }
}

/**
 * Clear stored API token (call on logout)
 */
export function clearApiToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('api_token');
    localStorage.removeItem('user_id');
  }
}

/**
 * Get stored user ID
 */
export function getUserId(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('user_id');
}

export default apiClient;
