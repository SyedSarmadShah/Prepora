import { create } from 'zustand';
import { User } from '../types/user.types';
import { setAccessToken } from '../services/api.client';

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;

  setAuth: (user: User, accessToken: string, refreshToken?: string) => void;
  clearAuth: () => void;
  hasRole: (roleCode: string) => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,

  setAuth: (user: User, accessToken: string, refreshToken?: string) => {
    setAccessToken(accessToken);
    set({
      user,
      accessToken,
      refreshToken: refreshToken ?? null,
      isAuthenticated: true,
    });
  },

  clearAuth: () => {
    setAccessToken(null);
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    });
  },

  hasRole: (roleCode: string) => {
    const user = get().user;
    if (!user || !user.roles) {
      return false;
    }
    return user.roles.includes(roleCode);
  },
}));
