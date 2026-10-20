import axios from 'axios'

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/',
    headers: {
        'Accept': 'application/json'
    }
})

// Request Interceptor: Attach JWT Access Token Automatically
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }

        // Let the browser automatically set the boundary header when sending FormData
        if (config.data instanceof FormData) {
            delete config.headers['Content-Type']
        }

        return config
    },
    (error) => Promise.reject(error)
)

// Response Interceptor: Provide Clean Debug Logs in Console for HTTP Errors
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            console.error(`[API Error ${error.response.status}]:`, error.response.data)
        } else if (error.request) {
            console.error('[Network Error]: Server is unreachable at http://127.0.0.1:8000')
        }
        return Promise.reject(error)
    }
)

// Helper: Resolve Media Paths to Absolute Backend URLs
export const getImageUrl = (imagePath?: string | null): string => {
    if (!imagePath) return ''

    // Full URL already points to Django server
    if (imagePath.startsWith('http://127.0.0.1:8000') || imagePath.startsWith('http://localhost:8000')) {
        return imagePath
    }

    // If path wrongly contains frontend Vite port
    if (imagePath.includes(':5173')) {
        return imagePath.replace(/http:\/\/localhost:5173|http:\/\/127.0.0.1:5173/, 'http://127.0.0.1:8000')
    }

    // Clean relative paths like "/media/rooms/pic.jpg" or "media/rooms/pic.jpg"
    const cleanPath = imagePath.startsWith('/') ? imagePath : `/${imagePath}`
    return `http://127.0.0.1:8000${cleanPath}`
}

export default apiClient