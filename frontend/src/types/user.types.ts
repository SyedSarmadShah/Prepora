export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_verified: boolean;
  roles?: string[];
}

export interface UserProfile {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_verified: boolean;
  target_exam?: string | null;
  phone_number?: string | null;
  avatar?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProfileUpdateRequest {
  first_name?: string;
  last_name?: string;
  target_exam?: string | null;
  phone_number?: string | null;
}

