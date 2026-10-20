import { defineStore } from 'pinia'
import apiClient from '../api/axios'
import type { Dinosaur } from '../types'

export const useDinosaurStore = defineStore('dinosaur', {
    state: () => ({
        dinosaurs: [] as Dinosaur[],
        loading: false
    }),
    actions: {
        async fetchDinosaurs() {
            this.loading = true
            try {
                const res = await apiClient.get<Dinosaur[]>('dinosaurs/')
                this.dinosaurs = res.data
            } finally {
                this.loading = false
            }
        },
        async createDinosaur(payload: Dinosaur) {
            const res = await apiClient.post<Dinosaur>('dinosaurs/', payload)
            this.dinosaurs.push(res.data)
        },
        async updateDinosaur(id: number, payload: Dinosaur) {
            const res = await apiClient.put<Dinosaur>(`dinosaurs/${id}/`, payload)
            const index = this.dinosaurs.findIndex((d) => d.id === id)
            if (index !== -1) this.dinosaurs[index] = res.data
        },
        async deleteDinosaur(id: number) {
            await apiClient.delete(`dinosaurs/${id}/`)
            this.dinosaurs = this.dinosaurs.filter((d) => d.id !== id)
        }
    }
})