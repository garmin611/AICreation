
export interface VideoSettings {
  project_name: string
  chapter_name:string
  fps?: number
  fade_duration?: number
  use_pan?: boolean
  pan_range?: [number, number]
  resolution?: [number, number]
}