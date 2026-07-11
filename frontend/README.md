# AssetOptima Command Center

Enterprise IT Asset & License Optimizer — Frontend.

A modern enterprise SaaS frontend built with Next.js, designed in the style of Vercel, Linear, and Notion — not an admin template.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Next.js 16 | React framework with App Router |
| TypeScript | Type safety |
| Tailwind CSS v4 | Utility-first styling |
| shadcn/ui | Component primitives (Radix UI + CVA) |
| TanStack Query | Server state management |
| Zustand | Client state management |
| Axios | HTTP client with JWT interceptors |
| React Hook Form + Zod | Form validation |
| Framer Motion | Animations |
| next-themes | Light/dark/system theme |
| Lucide React | Icons |
| ESLint + Prettier | Code quality |

## Design System

### Philosophy

Minimal, modern, premium B2B SaaS. Inspired by Vercel, Linear, Supabase, and Clerk.

- Generous whitespace
- Clean typography hierarchy
- Subtle interactions and micro-animations
- Focus on content, not chrome
- Professional but approachable

### Color Palette

| Token | Light | Dark |
|-------|-------|------|
| `background` | `#F8FAFC` | `#0F172A` |
| `foreground` | `#0F172A` | `#F1F5F9` |
| `primary` | `#2563EB` | `#3B82F6` |
| `card` | `#FFFFFF` | `#1E293B` |
| `border` | `#E5E7EB` | `#334155` |
| `muted-foreground` | `#64748B` | `#94A3B8` |
| `success` | `#16A34A` | `#22C55E` |
| `warning` | `#F59E0B` | `#FBBF24` |
| `danger` | `#DC2626` | `#EF4444` |
| `ai` | `#7C3AED` | `#8B5CF6` |

### Typography

- **Font:** Geist (Sans + Mono via `next/font`)
- **Weights:** 400, 500, 600, 700
- **Scale:** System `text-xs` through `text-3xl`

### Spacing & Corners

- Rounded corners: `6px` (sm), `8px` (md), `12px` (lg), `16px` (xl)
- Card shadows: subtle `shadow-card`, elevated `shadow-elevated`, modal `shadow-modal`
- Generous padding: `px-6 py-5` for card bodies

## Project Structure

```
frontend/
├── public/                       # Static assets
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/               # Auth route group
│   │   │   ├── layout.tsx        # Auth layout (minimal, centered)
│   │   │   └── login/page.tsx    # Login page with RHF + Zod
│   │   ├── (dashboard)/          # Dashboard route group
│   │   │   ├── layout.tsx        # App shell (sidebar + topnav + footer)
│   │   │   ├── dashboard/        # Executive dashboard
│   │   │   ├── assets/           # Asset management placeholder
│   │   │   ├── software/         # Software catalog placeholder
│   │   │   ├── ai-assistant/     # AI assistant placeholder
│   │   │   ├── analytics/        # Analytics placeholder
│   │   │   ├── settings/         # Settings page
│   │   │   ├── profile/          # User profile page
│   │   │   └── loading/          # Session verification page
│   │   ├── 403/page.tsx          # Forbidden
│   │   ├── 404/page.tsx          # Not found
│   │   ├── not-found.tsx         # Next.js default 404
│   │   ├── unauthorized/page.tsx # Access denied
│   │   ├── layout.tsx            # Root layout (fonts + providers)
│   │   ├── page.tsx              # Root → redirects to /dashboard
│   │   ├── providers.tsx         # Client providers
│   │   └── globals.css           # Tailwind + design tokens
│   ├── components/
│   │   ├── ui/                   # shadcn/ui primitives
│   │   │   ├── button.tsx        # Button with CVA variants
│   │   │   ├── card.tsx          # Card + Header + Content + Footer
│   │   │   ├── badge.tsx         # Badge with semantic colors
│   │   │   ├── avatar.tsx        # Avatar with fallback
│   │   │   ├── skeleton.tsx      # Loading skeleton
│   │   │   ├── separator.tsx     # Radix UI separator
│   │   │   ├── page-header.tsx   # Page title + description + actions
│   │   │   ├── empty-state.tsx   # Empty data placeholder
│   │   │   ├── error-state.tsx   # Error state with retry
│   │   │   ├── alert.tsx         # Animated alert banner
│   │   │   └── index.ts          # Barrel exports
│   │   └── layout/               # App shell components
│   │       ├── Sidebar.tsx       # Collapsible nav with RBAC
│   │       ├── TopNav.tsx        # Search, theme, notifications, profile
│   │       └── Footer.tsx        # Minimal footer
│   ├── features/
│   │   ├── dashboard/            # Executive dashboard (feature-based)
│   │   │   ├── types/dashboard.ts
│   │   │   ├── api/useDashboard.ts
│   │   │   └── components/       # 8 section components
│   │   ├── auth/                 # Authentication architecture
│   │   │   ├── AuthGuard.tsx     # Route guard with RBAC
│   │   │   ├── AuthProvider.tsx  # TanStack Query provider
│   │   │   ├── TokenStorage.ts   # JWT storage abstraction
│   │   │   └── rbac.ts           # Role-permission definitions
│   │   └── theme/                # Theme system
│   │       └── ThemeProvider.tsx # next-themes wrapper
│   ├── hooks/
│   │   ├── useAuth.ts            # Auth operations + session restore
│   │   ├── useTheme.ts           # Theme toggle via next-themes
│   │   └── useNotifications.ts  # Notification state
│   ├── services/
│   │   ├── api.ts                # Axios with JWT interceptors
│   │   └── auth.ts               # Auth API service
│   ├── store/
│   │   ├── authStore.ts          # Auth state (Zustand)
│   │   ├── themeStore.ts         # Sidebar collapse state
│   │   ├── notificationStore.ts  # Notifications state
│   │   └── profileStore.ts       # User profile state
│   ├── types/
│   │   ├── api.ts                # API contracts
│   │   ├── auth.ts               # Auth domain types
│   │   ├── theme.ts              # Theme types
│   │   └── user.ts               # User re-exports
│   └── lib/
│       └── utils.ts              # cn(), formatDate(), etc.
└── components.json               # shadcn/ui configuration
```

## Application Shell

### Layout Architecture

```
┌──────────────────────────────────────────┐
│  Sidebar (w-60 / w-16 collapsed)         │
│  ┌─────────┐  TopNav (h-16)             │
│  │ Logo     │  [Search] [🌙] [🔔] [👤]  │
│  │          │────────────────────────────│
│  │ Dashboard│                           │
│  │ Assets   │  Main Content Area         │
│  │ Software │                           │
│  │ AI Asst. │  (flex-1 overflow-y-auto)  │
│  │ Analytics│                           │
│  │ Settings │                           │
│  │          │                           │
│  │ ──────── │                           │
│  │ Profile  │                           │
│  │ Sign Out │                           │
│  │ Collapse │────────────────────────────│
│  └─────────┘  Footer                     │
└──────────────────────────────────────────┘
```

### Sidebar

- Fixed desktop sidebar, mobile overlay
- Collapsible (`w-60` ↔ `w-16`)
- Active route highlighted with `primary` color
- User profile section at bottom
- Sign out and collapse controls

### TopNav

- Breadcrumb indicator
- Global search with ⌘K hint
- Dark mode toggle
- Notification bell with unread badge
- Profile dropdown with avatar, name, role

## Authentication Flow

```
User → Login Form → POST /auth/login → JWT pair
  ↓
TokenStorage (localStorage)
  ↓
Axios interceptor attaches `Authorization: Bearer <token>`
  ↓
401 response → POST /auth/refresh (one retry)
  ↓
Expired refresh → clear tokens → redirect /login
```

### Route Protection

- `AuthGuard` wraps dashboard routes
- Checks: authentication → token expiry → RBAC permission
- Routes mapped to permissions in `rbac.ts`
- Three roles: `super_admin`, `it_manager`, `it_support`

## State Management

| Store | State | Purpose |
|-------|-------|---------|
| `authStore` | tokens, user, role, loading | Authentication state |
| `themeStore` | sidebarCollapsed | UI preferences |
| `notificationStore` | notifications, unreadCount, isOpen | Notification panel |
| `profileStore` | profile | User profile data |

## API Layer

- **Axios** instance with `baseURL` from `NEXT_PUBLIC_API_URL`
- **Request interceptor** attaches JWT
- **Response interceptor** handles 401 → refresh → retry
- **Error handler** converts Axios errors to typed `AuthError`
- Default: `http://localhost:8000`

## Executive Dashboard

### Architecture

The dashboard is feature-based under `src/features/dashboard/` with a clear separation of concerns:

```
src/features/dashboard/
├── types/
│   └── dashboard.ts           # Dashboard domain types
├── api/
│   └── useDashboard.ts        # TanStack Query hooks with placeholder data
└── components/
    ├── DashboardHeader.tsx     # Greeting + date + quick action buttons
    ├── StatCard.tsx            # KPI metric card with icon + trend indicator
    ├── AssetStatusChart.tsx    # Donut chart (Recharts Pie) — asset distribution
    ├── SoftwareUsageChart.tsx  # Horizontal bar chart (Recharts Bar) — license usage
    ├── AiInsightCard.tsx       # AI-powered license optimization card
    ├── ActivityTimeline.tsx    # Icon-per-event timeline
    ├── NotificationPanel.tsx   # Priority-coded notification list
    └── QuickActions.tsx        # Navigable shortcut grid
```

### Data Flow

All data flows through TanStack Query hooks. Currently each hook simulates a 800–1400 ms delay and returns rich placeholder data so the UI is fully interactive. When a backend is available, replace the `queryFn` in each hook with a real API call:

```ts
// Before (placeholder):
queryFn: async () => {
  await delay(1000);
  return PLACEHOLDER_DATA;
}

// After (real API):
queryFn: async () => {
  const { data } = await api.get<DashboardKpi[]>("/dashboard/kpis");
  return data;
}
```

### Section Breakdown

| Section | Component | States | Annotations |
|---------|-----------|--------|-------------|
| Welcome Header | `DashboardHeader` | loading, data | Time-based greeting, formatted date, 3 quick-action buttons |
| KPI Grid (×6) | `StatCard` | loading, data | Icon + value + trend arrow, staggered Framer Motion entrance |
| Asset Status | `AssetStatusChart` | loading, error, empty, data | Donut chart with custom tooltip + color-coded legend |
| Software Usage | `SoftwareUsageChart` | loading, error, empty, data | Horizontal bar chart with percentage axis |
| AI Insight | `AiInsightCard` | loading, error, empty, data | 3-metric grid + risk badge + recommendation box + "Open AI" CTA |
| Activity Feed | `ActivityTimeline` | loading, error, empty, data | 5 activity types with unique icons/colors, relative times |
| Notifications | `NotificationPanel` | loading, error, empty, data | Critical/warning/info badges, unread dot, "Mark all read" |
| Quick Actions | `QuickActions` | loading, data | 5-card grid linking to /assets, /ai-assistant, /software |

### Component States

Every dashboard component handles four states consistently:

- **Loading**: Skeleton placeholders matching the content shape
- **Error**: `ErrorState` component with a "Try Again" retry button wired to `refetch()`
- **Empty**: `EmptyState` component with contextual icon and message
- **Data**: Fully rendered content with Framer Motion entrance animations

### Composition

The dashboard page (`src/app/(dashboard)/dashboard/page.tsx`) destructures every hook and passes props to the eight section components. A unified `handleRefresh` callback triggers `refetch()` on all data hooks simultaneously.

## Getting Started

```bash
# Install
cd frontend && npm install

# Environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Development
npm run dev          # → http://localhost:3000

# Build
npm run build && npm start

# Code Quality
npm run lint         # ESLint + Prettier
npm run typecheck    # tsc --noEmit
```

## Component States

Every data-bound component implements four states:

| State | Behavior |
|-------|----------|
| Loading | Skeleton placeholders |
| Error | Error card with retry button |
| Empty | Descriptive empty state |
| Data | Fully rendered content |

## Theming

- `next-themes` manages light/dark/system mode
- `ThemeProvider` adds `class` attribute strategy to `<html>`
- Tailwind `dark:` variant + CSS custom properties switch based on `.dark` class
- Preference persisted to `localStorage`

## Code Quality

- Strict TypeScript (`strict: true` in tsconfig)
- ESLint with `eslint-config-next` + Prettier
- Tailwind class sorting via `prettier-plugin-tailwindcss`
- `class-variance-authority` for component variants
- `tailwind-merge` for conflict-free class composition
