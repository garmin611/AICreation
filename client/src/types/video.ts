export interface VideoSettings {
  project_name: string
  chapter_name:string
  fps?: number
  fade_duration?: number
  use_pan?: boolean
  pan_range?: [number, number]
  resolution?: [number, number]
}

export interface VideoProgress {
  progress: number
  total: number
  percentage: number
  current_task: string | null
}