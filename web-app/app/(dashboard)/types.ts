export interface UserProfileType {
  id: number;
  email: string;
  username: string;
  fullname: string;
  preferred_language: string;
  profile_picture: string | null;
  is_email_verified: boolean;
}
