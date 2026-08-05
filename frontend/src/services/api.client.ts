import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { API_CONFIG } from '../constants/api.constants';

export interface ApiErrorEnvelope {
  success: false;
  error: {
    code: string;
    message: string;
    status_code: number;
    details?: Array<{ field?: string; code?: string; message: string }>;
    request_id?: string;
  };
}

let inMemoryAccessToken: string | null = null;

export const setAccessToken = (token: string | null): void => {
  inMemoryAccessToken = token;
};

export const getAccessToken = (): string | null => {
  return inMemoryAccessToken;
};

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: API_CONFIG.HEADERS,
});

// Request Interceptor: Attach Bearer token to outgoing requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (inMemoryAccessToken && config.headers) {
      config.headers.Authorization = `Bearer ${inMemoryAccessToken}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Format error responses into RFC 7807 compliant ApiErrorEnvelope structures
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorEnvelope>) => {
    if (error.response?.data?.error) {
      return Promise.reject(error.response.data);
    }

    const fallbackError: ApiErrorEnvelope = {
      success: false,
      error: {
        code: error.code || 'NETWORK_ERROR',
        message: error.message || 'A network error occurred. Please check your connection.',
        status_code: error.response?.status || 500,
      },
    };

    return Promise.reject(fallbackError);
  }
);
