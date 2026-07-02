// Single entry point for all backend calls. Components never touch fetch()
// directly — they call api.something() and get typed data or an ApiError.
//
// Django session-auth plumbing handled here so nothing else has to know:
//   - cookies ride along automatically (same-origin thanks to the Vite proxy)
//   - non-GET requests need the CSRF token from the csrftoken cookie
//     echoed back in the X-CSRFToken header (Django's double-submit check)

import type { Character, Exercise, Workout, WorkoutInput } from './types'

export class ApiError extends Error {
  status: number
  data: unknown

  constructor(status: number, data: unknown) {
    super(`API error ${status}`)
    this.status = status
    this.data = data
  }
}

function getCookie(name: string): string {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`))
  return match ? decodeURIComponent(match[1]) : ''
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const method = options.method ?? 'GET'
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (method !== 'GET') {
    headers['X-CSRFToken'] = getCookie('csrftoken')
  }

  const response = await fetch(path, { ...options, headers })

  if (!response.ok) {
    // Try to surface DRF's error body ({"detail": ...} or field errors).
    const data = await response.json().catch(() => null)
    throw new ApiError(response.status, data)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return response.json()
}

export const api = {
  /** Call once on app load so the csrftoken cookie exists before any POST. */
  ensureCsrf: () => request<{ detail: string }>('/api/auth/csrf/'),

  login: async (username: string, password: string) => {
    const user = await request<{ username: string }>('/api/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
    // Django rotates the CSRF token on login; grab the fresh one now.
    await api.ensureCsrf()
    return user
  },

  logout: () => request<void>('/api/auth/logout/', { method: 'POST' }),

  getCharacter: () => request<Character>('/api/characters/me/'),

  getExercises: () => request<Exercise[]>('/api/exercises/'),

  logWorkout: (workout: WorkoutInput) =>
    request<Workout>('/api/workouts/', {
      method: 'POST',
      body: JSON.stringify(workout),
    }),
}
