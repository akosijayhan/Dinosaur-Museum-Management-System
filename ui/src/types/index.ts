export interface UserCredentials {
    username: string
    password: string
}

export interface Dinosaur {
    id?: number
    name: string
    species: string
    period: string
    diet: string
    description?: string
    image?: string | null
    room?: number | null
    created_by?: string | null
    created_at?: string
}

export interface Discovery {
    id?: number
    dinosaur: number
    location: string
    discovery_date: string
    discovered_by: string
    description?: string
    created_by?: string | null
    created_at?: string
}

export interface ExtinctionEvent {
    id?: number
    name: string
    period: string
    estimated_date: string
    description?: string
    dinosaur?: number | null
    image?: string | null
    created_by?: string | null
    created_at?: string
}
export interface MapItem {
    id?: number
    name: string
    floor_level: number

}
export interface Room {
    id?: number
    name: string
    floor: number
    description?: string
    image?: string | null
    created_at?: string
}