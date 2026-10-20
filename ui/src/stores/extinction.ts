import { defineStore } from 'pinia'
import apiClient from '../api/axios'

export interface ExtinctionEvent {
    id?: number
    title: string
    period: string
    cause: string
    dinosaur?: number | null
    created_by?: number | null
    created_at?: string
}

interface ExtinctionState {
    events: ExtinctionEvent[]
    loading: boolean
    error: string | null
}

export const useExtinctionStore = defineStore('extinction', {
    state: (): ExtinctionState => ({
        events: [],
        loading: false,
        error: null,
    }),
    actions: {
        async fetchExtinctions() {
            this.loading = true
            this.error = null
            try {
                const res = await apiClient.get<ExtinctionEvent[]>('extinction/')
                this.events = res.data
            } catch (err: any) {
                this.error = 'Failed to fetch extinction events.'
            } finally {
                this.loading = false
            }
        },
        async createExtinction(payload: ExtinctionEvent) {
            this.error = null
            try {
                const res = await apiClient.post<ExtinctionEvent>('extinction/', payload)
                await this.fetchExtinctions()
                return res.data
            } catch (err: any) {
                this.error = 'Failed to create extinction event.'
                throw err
            }
        },
        async updateExtinction(id: number, payload: ExtinctionEvent) {
            this.error = null
            try {
                const res = await apiClient.put<ExtinctionEvent>(`extinction/${id}/`, payload)
                await this.fetchExtinctions()
                return res.data
            } catch (err: any) {
                this.error = 'Failed to update extinction event.'
                throw err
            }
        },
        async deleteExtinction(id: number) {
            this.error = null
            try {
                await apiClient.delete(`extinction/${id}/`)
                // Option 1: Re-fetch updated list from Django backend
                await this.fetchExtinctions()

                // Option 2 (Alternative): Immediately remove item from reactive array
                // this.events = this.events.filter(e => e.id !== id)
            } catch (err: any) {
                this.error = 'Failed to delete extinction event.'
                throw err
            }
        }
    },
})