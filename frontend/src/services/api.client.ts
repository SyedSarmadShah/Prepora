import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { API_CONFIG, API_ENDPOINTS } from '../constants/api.constants';
import { RefreshTokenResponse } from '../types/auth.types';

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

export interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

let inMemoryAccessToken: string | null = null;

export const setAccessToken = (token: string | null): void => {
  inMemoryAccessToken = token;
};

export const getAccessToken = (): string | null => {
  return inMemoryAccessToken;
};

export interface AuthHandlers {
  getRefreshToken: () => string | null;
  onTokensRefreshed: (accessToken: string, refreshToken?: string) => void;
  onAuthFailed: () => void;
}

let authHandlers: AuthHandlers | null = null;

export const setAuthHandlers = (handlers: AuthHandlers): void => {
  authHandlers = handlers;
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

// State management for queueing concurrent 401 requests during a single refresh call
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

const processQueue = (error: unknown | null, token: string | null = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else if (token) {
      promise.resolve(token);
    }
  });
  failedQueue = [];
};

const formatFallbackError = (error: AxiosError<ApiErrorEnvelope>): ApiErrorEnvelope => {
  if (error.response?.data?.error) {
    return error.response.data;
  }
  return {
    success: false,
    error: {
      code: error.code || 'NETWORK_ERROR',
      message: error.message || 'A network error occurred. Please check your connection.',
      status_code: error.response?.status || 500,
    },
  };
};

// Response Interceptor: Transparent 401 silent token refresh queue + RFC 7807 error formatting
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorEnvelope>) => {
    const originalRequest = error.config as CustomAxiosRequestConfig | undefined;

    const is401 = error.response?.status === 401;
    const isRefreshEndpoint = originalRequest?.url?.includes(API_ENDPOINTS.AUTH.REFRESH);

    // If not a 401 error, or if request is missing, or already retried, or is the refresh request itself
    if (!is401 || !originalRequest || originalRequest._retry || isRefreshEndpoint) {
      return Promise.reject(formatFallbackError(error));
    }

    const refreshToken = authHandlers?.getRefreshToken() ?? null;
    if (!refreshToken) {
      if (authHandlers?.onAuthFailed) {
        authHandlers.onAuthFailed();
      }
      return Promise.reject(formatFallbackError(error));
    }

    // Queue concurrent 401 requests while a refresh request is already in-flight
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({
          resolve: (newToken: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
            }
            resolve(apiClient(originalRequest));
          },
          reject: (err: unknown) => {
            reject(err);
          },
        });
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      // Execute single refresh request directly using isolated axios call to avoid interceptor loop
      const refreshUrl = `${API_CONFIG.BASE_URL}${API_ENDPOINTS.AUTH.REFRESH}`;
      const refreshResponse = await axios.post<RefreshTokenResponse>(
        refreshUrl,
        { refresh: refreshToken },
        { headers: API_CONFIG.HEADERS, timeout: API_CONFIG.TIMEOUT }
      );

      const newAccessToken = refreshResponse.data.access;
      const newRefreshToken = refreshResponse.data.refresh;

      setAccessToken(newAccessToken);

      if (authHandlers?.onTokensRefreshed) {
        authHandlers.onTokensRefreshed(newAccessToken, newRefreshToken);
      }

      processQueue(null, newAccessToken);

      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      }
      return apiClient(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      if (authHandlers?.onAuthFailed) {
        authHandlers.onAuthFailed();
      }

      const formattedAuthError: ApiErrorEnvelope = {
        success: false,
        error: {
          code: 'UNAUTHENTICATED',
          message: 'Session expired. Please log in again.',
          status_code: 401,
        },
      };
      return Promise.reject(formattedAuthError);
    } finally {
      isRefreshing = false;
    }
  }
);
