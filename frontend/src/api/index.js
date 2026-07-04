const BASE = '/api'

async function request(path, options = {}) {
  const token = localStorage.getItem('cj_token')
  const headers = { ...options.headers }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // 非 FormData 请求才设 Content-Type
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }))
    if (res.status === 401) {
      localStorage.removeItem('cj_token')
      localStorage.removeItem('cj_user')
      // 触发全局重新登录
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }
    throw new Error(err.detail || `请求失败 (${res.status})`)
  }

  return res.json()
}

// ── Auth ────────────────────────────────────────────────────
export function login(username, password) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export function register(username, password) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

// ── Trips ────────────────────────────────────────────────────
export function fetchTrips(params = {}) {
  const q = new URLSearchParams()
  if (params.year) q.set('year', params.year)
  if (params.include_moments) q.set('include_moments', 'true')
  const qs = q.toString()
  return request(`/trips${qs ? `?${qs}` : ''}`)
}

export function createTrip(data) {
  return request('/trips', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function fetchTrip(id) {
  return request(`/trips/${id}`)
}

export function updateTrip(id, data) {
  return request(`/trips/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export function deleteTrip(id, deleteFiles = false) {
  return request(`/trips/${id}?delete_files=${deleteFiles}`, {
    method: 'DELETE',
  })
}

// ── Moments ──────────────────────────────────────────────────
export function fetchMoments(tripId) {
  return request(`/trips/${tripId}/moments`)
}

export function createMoment(data) {
  return request('/moments', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function fetchMoment(id) {
  return request(`/moments/${id}`)
}

export function updateMoment(id, data) {
  return request(`/moments/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export function deleteMoment(id) {
  return request(`/moments/${id}`, {
    method: 'DELETE',
  })
}

// ── Upload ────────────────────────────────────────────────────
export function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request('/upload', {
    method: 'POST',
    body: formData,
  })
}

// ── Cover Upload ─────────────────────────────────────────────
export function uploadCover(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request('/upload/cover', {
    method: 'POST',
    body: formData,
  })
}

// ── Stats ──────────────────────────────────────────────────────
export function fetchStats() {
  return request('/stats/summary')
}
