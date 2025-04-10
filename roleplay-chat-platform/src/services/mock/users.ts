import { User } from '@/types/auth';

// Mock users for testing - in a real app, this would come from a database
export const mockUsers: User[] = [
  {
    id: 'user_1',
    username: 'admin',
    email: 'admin@roleplayhub.com',
    avatar: null,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    is_verified: true,
    is_admin: true,
    timezone: 'UTC',
    last_login: '2024-04-01T15:30:00Z'
  },
  {
    id: 'user_2',
    username: 'player123',
    email: 'player123@example.com',
    avatar: null,
    created_at: '2023-02-15T18:30:00Z',
    updated_at: '2023-02-15T18:30:00Z',
    is_verified: true,
    is_admin: false,
    timezone: 'America/New_York',
    last_login: '2024-04-09T22:45:00Z'
  },
  {
    id: 'user_3',
    username: 'fantasy_lover',
    email: 'fantasy@example.com',
    avatar: 'https://ext.same-assets.com/2421641290/avatar1.jpg',
    created_at: '2023-05-22T09:15:00Z',
    updated_at: '2023-08-10T14:20:00Z',
    is_verified: true,
    is_admin: false,
    timezone: 'Europe/London',
    last_login: '2024-04-08T13:15:00Z'
  },
  {
    id: 'user_4',
    username: 'dragon_tamer',
    email: 'dragons@example.com',
    avatar: 'https://ext.same-assets.com/2421641290/avatar2.jpg',
    created_at: '2023-07-18T11:45:00Z',
    updated_at: '2024-01-05T16:30:00Z',
    is_verified: true,
    is_admin: false,
    timezone: 'Asia/Tokyo',
    last_login: '2024-04-10T02:30:00Z'
  },
  {
    id: 'user_5',
    username: 'elvish_bard',
    email: 'bard@example.com',
    avatar: 'https://ext.same-assets.com/2421641290/avatar3.jpg',
    created_at: '2023-09-30T20:00:00Z',
    updated_at: '2023-11-12T08:45:00Z',
    is_verified: true,
    is_admin: false,
    timezone: 'Europe/Paris',
    last_login: '2024-04-05T19:20:00Z'
  }
];
