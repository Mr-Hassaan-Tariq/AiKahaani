# My Scripts Page - New API Flow Implementation

## Overview

The `/my-scripts` page has been updated to follow the same API flow pattern as the `/settings/profile` page, implementing a **hybrid approach** that combines **Server-Side Rendering (SSR)** for initial data fetching with **Client-Side Mutations** for user interactions.

## 🔄 **New API Flow Architecture**

### **1. Server-Side Data Fetching (SSR)**

```typescript
// File: web-app/app/(dashboard)/my-scripts/actions.ts
'use server';

export async function getScriptGenerations(search?: string, type?: 'script' | 'outline') {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (type) params.append('type', type);

  const endpoint = `v1/scripts/generations/${queryString ? `?${queryString}` : ''}`;
  return await getServerDataAction<ScriptGeneration[]>(endpoint);
}
```

**Flow:**

```
Page Component → getScriptGenerations() → getServerDataAction() → Backend API
```

**API Call Details:**

- **Endpoint**: `GET /api/v1/scripts/generations/`
- **Method**: Server Action (`'use server'`)
- **Authentication**: JWT token from cookies
- **Response**: Array of script generations (outlines + scripts)

### **2. Client-Side Mutations**

#### **A. Delete Script Generation**

```typescript
// File: web-app/lib/hooks/useDeleteScriptGeneration.tsx
async function deleteScriptGeneration(uuid: string) {
  return await deleteClientDataAction(`v1/scripts/generations/${uuid}/`);
}

export default function useDeleteScriptGeneration() {
  return useMutation({
    mutationFn: deleteScriptGeneration,
    onSuccess: () => {
      toast.success('Success', 'Script deleted successfully');
      router.refresh(); // Refresh server data
    },
  });
}
```

#### **B. Update Script Generation**

```typescript
// File: web-app/lib/hooks/useUpdateScriptGeneration.tsx
async function updateScriptGeneration(uuid: string, updates: Partial<ScriptGeneration>) {
  return await patchClientDataAction<ScriptGeneration>(`v1/scripts/generations/${uuid}/`, updates);
}
```

## 🏗️ **Component Architecture**

### **Page Structure**

```
MyScriptsPage (Server Component)
├── ComponentNav
└── MyScriptsContent (Server Component)
    └── MyScriptsTabWrapper (Client Component)
        ├── ScriptsTab (Client Component)
        ├── OutlinesPage (Client Component)
        ├── ScriptsPage (Client Component)
        └── MyScriptsList (Client Component)
            └── ScriptList
                └── ScriptCard (with modals)
```

### **Data Flow**

1. **Initial Load**: Server fetches all script generations
2. **Filtering**: Client-side filtering based on type (outline/script)
3. **Mutations**: Client-side operations with server refresh
4. **Error Handling**: Comprehensive error states and retry mechanisms

## 🔧 **Key Implementation Features**

### **1. Server-Side Rendering Benefits**

- **SEO Friendly**: Data available on initial render
- **Performance**: No loading states for initial data
- **Security**: Server-side token handling
- **Caching**: Built-in Next.js caching

### **1.1. Server/Client Component Integration**

- **Function Passing**: Server components cannot pass functions to client components
- **Solution**: Use string URLs for navigation instead of functions
- **ComponentNav**: Updated to handle both function callbacks and string URLs
- **ScriptsTab**: Created MyScriptsTabWrapper client component to handle search/filter functions
- **Hook Usage**: Components using client-side hooks must be marked with 'use client'

### **2. Client-Side Mutations**

- **Real-time Updates**: Immediate UI feedback
- **Optimistic Updates**: Better UX
- **Error Handling**: Granular error management
- **Cache Invalidation**: Automatic server data refresh

### **3. Type Safety**

```typescript
// Unified type system
interface ScriptGeneration {
  uuid: string;
  title: string;
  type: 'script' | 'outline';
  status: 'draft' | 'generated' | 'saved';
  // ... other fields
}
```

## 📊 **API Endpoints Used**

### **Backend Endpoints**

- `GET /api/v1/scripts/generations/` - Fetch all script generations
- `DELETE /api/v1/scripts/generations/{uuid}/` - Delete script generation
- `PATCH /api/v1/scripts/generations/{uuid}/` - Update script generation

### **Query Parameters**

- `search` - Search by title or content
- `type` - Filter by 'script' or 'outline'

## 🔒 **Security & Performance**

### **Authentication**

- **Server-side**: JWT tokens from Next.js cookies
- **Client-side**: Cookie + localStorage fallback
- **Automatic**: Token refresh and error handling

### **Error Handling**

```typescript
// Server-side error handling
return { isError: true, error: await processError(res), data: undefined };

// Client-side error handling
onError: (error) => {
  toast.error('Something went wrong', error.message?.toString());
};
```

### **Performance Optimizations**

1. **Server-Side Rendering**: Initial data without client-side loading
2. **React Query Caching**: Efficient mutation state management
3. **Optimistic Updates**: Immediate UI feedback
4. **Suspense Boundaries**: Proper loading states

## 🚀 **Migration Benefits**

### **Before (Client-Side Only)**

- ❌ Loading states on every page load
- ❌ SEO unfriendly
- ❌ Slower initial render
- ❌ Complex state management

### **After (Hybrid SSR + Client)**

- ✅ Fast initial render with data
- ✅ SEO friendly
- ✅ Better performance
- ✅ Simplified state management
- ✅ Consistent with profile page pattern

## 🔄 **Usage Examples**

### **Server-Side Data Fetching**

```typescript
// In server component
const { data: scripts, error, isError } = await getScriptGenerations(search, type);
```

### **Client-Side Mutations**

```typescript
// In client component
const { mutate: deleteScript } = useDeleteScriptGeneration();
const { mutate: updateScript } = useUpdateScriptGeneration();

// Usage
deleteScript(scriptUuid);
updateScript({ uuid: scriptUuid, updates: { title: 'New Title' } });
```

## 🚨 **Common Issues & Solutions**

### **Server/Client Component Errors**

1. **"Functions cannot be passed directly to Client Components"**
   - **Cause**: Passing functions from server to client components
   - **Solution**: Use string URLs or create client wrapper components

2. **"Event handlers cannot be passed to Client Component props"**
   - **Cause**: Passing event handlers from server to client components
   - **Solution**: Create client wrapper components for interactive functionality

3. **"Attempted to call useScriptActions() from the server"**
   - **Cause**: Using client-side hooks in server components
   - **Solution**: Mark components with 'use client' directive

### **Best Practices**

- **Server Components**: Use for data fetching, SEO, and initial rendering
- **Client Components**: Use for interactivity, hooks, and event handlers
- **Hybrid Approach**: Server components fetch data, client components handle UI interactions

## 🔍 **Filter System Implementation**

### **Filter Types Supported**

1. **Last Edited (Ordering)**
   - Most Recent → `?ordering=created`
   - Oldest → `?ordering=modified`

2. **Word Count Range**
   - Min/Max range → `?word_count_min={min}&word_count_max={max}`
   - Example: `?word_count_min=400&word_count_max=600`

3. **Video Duration**
   - Specific durations: 20min, 40min, 60min
   - Ranges: <20min, >60min
   - Example: `?duration_min=3&duration_max=5`

### **Filter Flow**

```
User selects filters → FilterScriptModal → convertFiltersToAPI() → URL params → Server action → API call
```

### **URL Parameter Examples**

```
# Most recent scripts with word count 400-600
/my-scripts?ordering=created&word_count_min=400&word_count_max=600

# Oldest scripts with 20min duration
/my-scripts?ordering=modified&duration_min=20&duration_max=20

# Combined filters
/my-scripts?search=marketing&ordering=created&word_count_min=500&duration_min=3&duration_max=5
```

## 📝 **Next Steps**

1. **Search Implementation**: ✅ Completed with debouncing and URL persistence
2. **Filter Modal**: ✅ Completed with full API integration
3. **Pagination**: Add pagination for large script lists
4. **Real-time Updates**: Consider WebSocket integration for live updates

### **📝 Files Created/Updated for Filter System**

- ✅ `web-app/app/(dashboard)/my-scripts/actions.ts` - Added ScriptFilters interface and filter support
- ✅ `web-app/app/(dashboard)/my-scripts/_utils/filterUtils.ts` - New filter utility functions
- ✅ `web-app/app/(dashboard)/my-scripts/_components/FilterScriptModal.tsx` - Updated with API integration
- ✅ `web-app/app/(dashboard)/my-scripts/_components/MyScriptsTabWrapper.tsx` - Added filter handling
- ✅ `web-app/app/(dashboard)/my-scripts/_components/ScriptsTab.tsx` - Added filter props
- ✅ `web-app/app/(dashboard)/my-scripts/_components/MyScriptsContent.tsx` - Updated to handle filter params
- ✅ `web-app/app/(dashboard)/my-scripts/_types/index.ts` - Updated type definitions

This implementation provides a robust, scalable, and maintainable solution that follows modern Next.js patterns and ensures optimal user experience.
