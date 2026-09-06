import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { User, Project } from './api'

// ─── Notification Type ────────────────────────────────────────────────────────
export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'danger' | 'ai'
  title: string
  message: string
  read: boolean
  created_at: string
  link?: string
}

// ─── Auth Slice ───────────────────────────────────────────────────────────────
interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  setAuth: (user: User, token: string) => void
  clearAuth: () => void
  updateUser: (updates: Partial<User>) => void
}

// ─── Project Slice ────────────────────────────────────────────────────────────
interface ProjectState {
  selectedProject: Project | null
  projects: Project[]
  setSelectedProject: (project: Project) => void
  setProjects: (projects: Project[]) => void
}

// ─── Notifications Slice ──────────────────────────────────────────────────────
interface NotificationsState {
  notifications: Notification[]
  unreadCount: number
  addNotification: (n: Omit<Notification, 'id' | 'created_at'>) => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  removeNotification: (id: string) => void
}

// ─── UI Slice ─────────────────────────────────────────────────────────────────
interface UIState {
  sidebarCollapsed: boolean
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
}

// ─── Combined Store ───────────────────────────────────────────────────────────
type StoreState = AuthState & ProjectState & NotificationsState & UIState

export const useStore = create<StoreState>()(
  persist(
    (set, get) => ({
      // ── Auth ──────────────────────────────────────────────────────────────
      user: null,
      token: null,
      isAuthenticated: false,

      setAuth: (user: User, token: string) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('nexus_token', token)
          localStorage.setItem('nexus_user', JSON.stringify(user))
        }
        set({ user, token, isAuthenticated: true })
      },

      clearAuth: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('nexus_token')
          localStorage.removeItem('nexus_user')
        }
        set({ user: null, token: null, isAuthenticated: false })
      },

      updateUser: (updates: Partial<User>) => {
        const currentUser = get().user
        if (currentUser) {
          set({ user: { ...currentUser, ...updates } })
        }
      },

      // ── Projects ──────────────────────────────────────────────────────────
      selectedProject: null,
      projects: [],

      setSelectedProject: (project: Project) => {
        set({ selectedProject: project })
      },

      setProjects: (projects: Project[]) => {
        const { selectedProject } = get()
        set({
          projects,
          // Auto-select first project if none selected
          selectedProject: selectedProject ?? (projects[0] || null),
        })
      },

      // ── Notifications ─────────────────────────────────────────────────────
      notifications: [
        {
          id: '1',
          type: 'warning',
          title: 'Schedule Alert',
          message: 'Pipeline Welding (Reach 3) is 3 days behind schedule',
          read: false,
          created_at: new Date(Date.now() - 3600000).toISOString(),
          link: '/schedule',
        },
        {
          id: '2',
          type: 'ai',
          title: 'AI Forecast Updated',
          message: 'Delay oracle predicts +12 day overrun — see Analytics',
          read: false,
          created_at: new Date(Date.now() - 7200000).toISOString(),
          link: '/analytics',
        },
        {
          id: '3',
          type: 'info',
          title: 'New Submissions',
          message: '8 field reports processed and ready for review',
          read: true,
          created_at: new Date(Date.now() - 86400000).toISOString(),
          link: '/review',
        },
      ],
      unreadCount: 2,

      addNotification: (n) => {
        const newNotif: Notification = {
          ...n,
          id: crypto.randomUUID(),
          created_at: new Date().toISOString(),
        }
        set((state) => ({
          notifications: [newNotif, ...state.notifications],
          unreadCount: state.unreadCount + (n.read ? 0 : 1),
        }))
      },

      markAsRead: (id: string) => {
        set((state) => ({
          notifications: state.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n
          ),
          unreadCount: Math.max(0, state.unreadCount - 1),
        }))
      },

      markAllAsRead: () => {
        set((state) => ({
          notifications: state.notifications.map((n) => ({ ...n, read: true })),
          unreadCount: 0,
        }))
      },

      removeNotification: (id: string) => {
        set((state) => {
          const notif = state.notifications.find((n) => n.id === id)
          return {
            notifications: state.notifications.filter((n) => n.id !== id),
            unreadCount: notif && !notif.read
              ? Math.max(0, state.unreadCount - 1)
              : state.unreadCount,
          }
        })
      },

      // ── UI ────────────────────────────────────────────────────────────────
      sidebarCollapsed: false,

      toggleSidebar: () => {
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }))
      },

      setSidebarCollapsed: (collapsed: boolean) => {
        set({ sidebarCollapsed: collapsed })
      },
    }),
    {
      name: 'nexus-pm-store',
      storage: createJSONStorage(() =>
        typeof window !== 'undefined' ? localStorage : ({} as Storage)
      ),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
        selectedProject: state.selectedProject,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
)

// ─── Selector Hooks ───────────────────────────────────────────────────────────
export const useAuth = () => useStore((s) => ({ user: s.user, token: s.token, isAuthenticated: s.isAuthenticated, setAuth: s.setAuth, clearAuth: s.clearAuth }))
export const useSelectedProject = () => useStore((s) => s.selectedProject)
export const useNotifications = () => useStore((s) => ({ notifications: s.notifications, unreadCount: s.unreadCount, addNotification: s.addNotification, markAsRead: s.markAsRead, markAllAsRead: s.markAllAsRead }))
export const useSidebar = () => useStore((s) => ({ collapsed: s.sidebarCollapsed, toggle: s.toggleSidebar }))
