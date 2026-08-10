export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 15000, // 15 seconds
  HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
} as const;

export const API_ENDPOINTS = {
  HEALTH: '/health/',
  AUTH: {
    LOGIN: '/auth/login/',
    REGISTER: '/auth/register/',
    REFRESH: '/auth/refresh/',
    LOGOUT: '/auth/logout/',
    ME: '/auth/me/',
  },
  USERS: {
    PROFILE: '/users/me/profile/',
  },
  EXAMS: {
    TRACKS: '/exam-tracks/',
    EXAMS: '/exams/',
    SUBJECTS: '/subjects/',
    TOPICS: '/topics/',
  },
} as const;
