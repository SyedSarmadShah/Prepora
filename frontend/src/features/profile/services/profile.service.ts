import { apiClient } from '../../../services/api.client';
import { API_ENDPOINTS } from '../../../constants/api.constants';
import { UserProfile, ProfileUpdateRequest } from '../../../types/user.types';

export const profileService = {
  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>(
      API_ENDPOINTS.USERS.PROFILE
    );
    return response.data;
  },

  async updateProfile(data: ProfileUpdateRequest): Promise<UserProfile> {
    const response = await apiClient.patch<UserProfile>(
      API_ENDPOINTS.USERS.PROFILE,
      data
    );
    return response.data;
  },
};
