import { defineStore } from 'pinia'
import apiClient from '../api/axios'
import type { Room } from '../types'

export const useRoomStore = defineStore('room', {
    state: () => ({
        rooms: [] as Room[],
        loading: false
    }),
    actions: {
        async fetchRooms() {
            this.loading = true
            try {
                const res = await apiClient.get<Room[]>('room/')
                this.rooms = res.data
            } finally {
                this.loading = false
            }
        },
        async createRoom(payload: Room) {
            const res = await apiClient.post<Room>('room/', payload)
            this.rooms.push(res.data)
        },
        async updateRoom(id: number, payload: Room) {
            const res = await apiClient.put<Room>(`room/${id}/`, payload)
            const index = this.rooms.findIndex((r) => r.id === id)
            if (index !== -1) this.rooms[index] = res.data
        },
        async deleteRoom(id: number) {
            await apiClient.delete(`room/${id}/`)
            this.rooms = this.rooms.filter((r) => r.id !== id)
        }
    }
})