import { defineStore } from 'pinia'
import apiClient from '../api/axios'
import type { Discovery } from '../types'

export const useDiscoveryStore = defineStore('discovery', {
    state: () => ({
        discoveries: [] as Discovery[],
        loading: false
    }),
    actions: {
        async fetchDiscoveries() {
            this.loading = true
            try {
                const res = await apiClient.get<Discovery[]>('discoveries/')
                this.discoveries = res.data
            } finally {
                this.loading = false
            }
        },
        async createDiscovery(payload: Discovery) {
            const res = await apiClient.post<Discovery>('discoveries/', payload)
            this.discoveries.push(res.data)
        },
        async updateDiscovery(id: number, payload: Discovery) {
            const res = await apiClient.put<Discovery>(`discoveries/${id}/`, payload)
            const index = this.discoveries.findIndex((d) => d.id === id)
            if (index !== -1) this.discoveries[index] = res.data
        },
        async deleteDiscovery(id: number) {
            await apiClient.delete(`discoveries/${id}/`)
            this.discoveries = this.discoveries.filter((d) => d.id !== id)
        }
    }
})