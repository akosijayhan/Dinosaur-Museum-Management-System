import { defineStore } from 'pinia'
import apiClient from '../api/axios'

interface User {
    username: string
    isStaff?: boolean
}

interface UserState {
    token: string | null
    isStaff: boolean
    user: User | null
}

export const useAuthStore = defineStore('auth', {
    state: (): UserState => ({
        token: localStorage.getItem('access_token'),
        isStaff: localStorage.getItem('is_staff') === 'true',
        user: localStorage.getItem('username')
            ? { username: localStorage.getItem('username') || '', isStaff: localStorage.getItem('is_staff') === 'true' }
            : null,
    }),
    getters: {
        isAuthenticated: (state) => !!state.token,
        isAdmin: (state) => state.isStaff,
    },
    actions: {
        setAuthData(token: string, isStaff: boolean, username: string) {
            this.token = token
            this.isStaff = isStaff
            this.user = { username, isStaff }

            localStorage.setItem('access_token', token)
            localStorage.setItem('is_staff', String(isStaff))
            localStorage.setItem('username', username)
        },
        async login(usernameVal: string, passwordVal: string) {
            const res = await apiClient.post('accounts/token/', {
                username: usernameVal,
                password: passwordVal,
            })

            const token = res.data.access
            const isStaff = res.data.is_staff ?? false

            this.setAuthData(token, isStaff, usernameVal)
            return res.data
        },
        logout() {
            this.token = null
            this.isStaff = false
            this.user = null

            localStorage.removeItem('access_token')
            localStorage.removeItem('is_staff')
            localStorage.removeItem('username')
        },
    },
})