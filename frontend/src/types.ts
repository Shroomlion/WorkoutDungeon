// Mirror of the DRF serializers — the API contract (DECISIONS.md D2) in
// TypeScript form. If the backend shape changes, change it here and the
// compiler will point at every component that needs updating.

export type StatCode = 'STR' | 'STA' | 'AGI' | 'VIT'

export interface StatValue {
  score: number
  xp: number
}

export interface Character {
  id: number
  name: string
  level: number
  stats: Record<StatCode, StatValue>
  created_at: string
}

export type Measurement = 'reps_weight' | 'reps' | 'duration' | 'distance'

export interface Exercise {
  id: number
  name: string
  measurement: Measurement
  str_weight: number
  sta_weight: number
  agi_weight: number
  vit_weight: number
}

// What we SEND when logging a set. Optional fields depend on the
// exercise's measurement type; the backend validates the combination.
export interface SetEntryInput {
  exercise: number // Exercise id
  order: number
  reps?: number
  weight_kg?: number
  duration_seconds?: number
  distance_m?: number
}

export interface WorkoutInput {
  performed_at?: string // ISO datetime; backend defaults to "now"
  notes?: string
  sets: SetEntryInput[]
}

// What we GET back — includes ids and the stat_gains reward payload.
export interface Workout {
  id: number
  performed_at: string
  notes: string
  sets: (SetEntryInput & { id: number })[]
  stat_gains: Partial<Record<StatCode, number>>
  created_at: string
}
