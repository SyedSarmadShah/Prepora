import { apiClient } from '../../../services/api.client';
import { API_ENDPOINTS } from '../../../constants/api.constants';
import {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  RefreshTokenRequest,
  RefreshTokenResponse,
  LogoutRequest,
} from '../../../types/auth.types';

export const authService = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      credentials
    );
    return response.data;
  },

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await apiClient.post<RegisterResponse>(
      API_ENDPOINTS.AUTH.REGISTER,
      data
    );
    return response.data;
  },

  async refreshToken(refresh: string): Promise<RefreshTokenResponse> {
    const payload: RefreshTokenRequest = { refresh };
    const response = await apiClient.post<RefreshTokenResponse>(
      API_ENDPOINTS.AUTH.REFRESH,
      payload
    );
    return response.data;
  },

  async logout(refresh: string): Promise<void> {
    const payload: LogoutRequest = { refresh };
    await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT, payload);
  },
};
