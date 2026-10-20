import { defineStore } from 'pinia'
import apiClient from '../api/axios'
import type { MapItem } from '../types'

export const useMapStore = defineStore('map', {
    state: () => ({
        maps: [] as MapItem[],
        loading: false
    }),
    actions: {
        async fetchMaps() {
            this.loading = true
            try {
                const res = await apiClient.get<MapItem[]>('map/')
                this.maps = res.data
            } finally {
                this.loading = false
            }
        },
        async createMap(payload: MapItem) {
            const res = await apiClient.post<MapItem>('map/', payload)
            this.maps.push(res.data)
        },
        async updateMap(id: number, payload: MapItem) {
            const res = await apiClient.put<MapItem>(`map/${id}/`, payload)
            const index = this.maps.findIndex((m) => m.id === id)
            if (index !== -1) this.maps[index] = res.data
        },
        async deleteMap(id: number) {
            await apiClient.delete(`map/${id}/`)
            this.maps = this.maps.filter((m) => m.id !== id)
        }
    }
})