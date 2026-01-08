'use client'

import { useState, useEffect } from 'react'

interface Target {
  id: number
  target_text: string
  start_date: string
  end_date: string
  duration_in_days: number
  status: string
}

interface Streak {
  current_streak: number
  last_completed_date: string | null
  today_done: boolean
  completed_days: number
}

export default function Page() {
  const [targets, setTargets] = useState<Target[]>([])
  const [streaks, setStreaks] = useState<Record<number, Streak>>({})
  const [token, setToken] = useState<string | null>(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // New target form
  const [newTargetText, setNewTargetText] = useState('')
  const [newStartDate, setNewStartDate] = useState('')
  const [newDuration, setNewDuration] = useState(30)

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

  useEffect(() => {
    const t = localStorage.getItem('token')
    if (t) setToken(t)
  }, [])

  useEffect(() => {
    if (token) {
      loadActiveTargets()
    }
  }, [token])

  async function loadActiveTargets() {
    try {
      const res = await fetch(`${BACKEND_URL}/target/active`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        const data = await res.json()
        const targetList = Array.isArray(data) ? data : []
        setTargets(targetList)
        
        // Load streaks for each target
        for (const t of targetList) {
          try {
            const streakRes = await fetch(`${BACKEND_URL}/streak/${t.id}`, {
              headers: { Authorization: `Bearer ${token}` },
            })
            if (streakRes.ok) {
              const streakData = await streakRes.json()
              setStreaks(prev => ({ ...prev, [t.id]: streakData }))
            }
          } catch (e) {
            console.error('Failed to load streak', e)
          }
        }
      } else {
        // Token might be invalid
        if (res.status === 401) {
          localStorage.removeItem('token')
          setToken(null)
        }
        setTargets([])
      }
    } catch (e) {
      console.error('Failed to load targets', e)
      setTargets([])
    }
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const formData = new URLSearchParams()
      formData.append('username', email)
      formData.append('password', password)

      const res = await fetch(`${BACKEND_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      })

      if (res.ok) {
        const data = await res.json()
        localStorage.setItem('token', data.access_token)
        setToken(data.access_token)
        setEmail('')
        setPassword('')
      } else {
        setError('Invalid email or password')
      }
    } catch (e) {
      setError('Connection failed. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  async function handleCreateTarget(e: React.FormEvent) {
    e.preventDefault()
    setError('')

    try {
      const res = await fetch(`${BACKEND_URL}/target/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          target_text: newTargetText,
          start_date: newStartDate,
          duration_in_days: newDuration,
        }),
      })

      if (res.ok) {
        setNewTargetText('')
        setNewStartDate('')
        setNewDuration(30)
        loadActiveTargets()
      } else {
        const data = await res.json()
        setError(data.detail || 'Failed to create target')
      }
    } catch (e) {
      setError('Failed to create target')
    }
  }

  async function handleCheckin(targetId: number) {
    try {
      const res = await fetch(`${BACKEND_URL}/checkin/today?target_id=${targetId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })

      const data = await res.json()
      if (data.success) {
        loadActiveTargets()
      } else {
        setError(data.message || 'Check-in failed')
      }
    } catch (e) {
      setError('Check-in failed')
    }
  }

  function handleLogout() {
    localStorage.removeItem('token')
    setToken(null)
    setTargets([])
    setStreaks({})
  }

  // Login form
  if (!token) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <div className="bg-slate-800 p-8 rounded-xl w-full max-w-md">
          <h1 className="text-3xl font-bold text-white mb-6 text-center">🔥 IronStreak</h1>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-slate-300 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full p-3 rounded-lg bg-slate-700 text-white border border-slate-600 focus:border-blue-500 focus:outline-none"
                placeholder="Tarungangwar@gmail.com"
                required
              />
            </div>
            <div>
              <label className="block text-slate-300 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-3 rounded-lg bg-slate-700 text-white border border-slate-600 focus:border-blue-500 focus:outline-none"
                placeholder="password"
                required
              />
            </div>
            {error && <p className="text-red-400 text-sm">{error}</p>}
            <button
              type="submit"
              disabled={loading}
              className="w-full p-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        </div>
      </div>
    )
  }

  // Dashboard
  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">🔥 IronStreak</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600"
          >
            Logout
          </button>
        </div>

        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-300 p-4 rounded-lg mb-6">
            {error}
            <button onClick={() => setError('')} className="float-right">×</button>
          </div>
        )}

        {/* Create Target Form */}
        <div className="bg-slate-800 p-6 rounded-xl mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Create New Target</h2>
          <form onSubmit={handleCreateTarget} className="space-y-4">
            <div>
              <label className="block text-slate-300 mb-2">Target Description</label>
              <input
                type="text"
                value={newTargetText}
                onChange={(e) => setNewTargetText(e.target.value)}
                className="w-full p-3 rounded-lg bg-slate-700 text-white border border-slate-600 focus:border-blue-500 focus:outline-none"
                placeholder="e.g., Do DSA daily for 30 days"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-300 mb-2">Start Date</label>
                <input
                  type="date"
                  value={newStartDate}
                  onChange={(e) => setNewStartDate(e.target.value)}
                  className="w-full p-3 rounded-lg bg-slate-700 text-white border border-slate-600 focus:border-blue-500 focus:outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-300 mb-2">Duration (days)</label>
                <input
                  type="number"
                  value={newDuration}
                  onChange={(e) => setNewDuration(parseInt(e.target.value))}
                  min={1}
                  max={365}
                  className="w-full p-3 rounded-lg bg-slate-700 text-white border border-slate-600 focus:border-blue-500 focus:outline-none"
                  required
                />
              </div>
            </div>
            <button
              type="submit"
              className="w-full p-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700"
            >
              Create Target (Locked Forever!)
            </button>
          </form>
        </div>

        {/* Active Targets */}
        <h2 className="text-2xl font-semibold text-white mb-4">Active Targets</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {targets.length === 0 ? (
            <p className="text-slate-400 col-span-2">No active targets. Create one above!</p>
          ) : (
            targets.map((t) => {
              const streak = streaks[t.id]
              const statusColor = t.status === 'FAILED' ? 'border-red-500' : t.status === 'SUCCESS' ? 'border-green-500' : 'border-slate-600'
              return (
                <div key={t.id} className={`bg-slate-800 p-6 rounded-lg border-2 ${statusColor}`}>
                  <h3 className="text-lg font-semibold text-white mb-2">{t.target_text}</h3>
                  <div className="text-slate-400 text-sm space-y-1 mb-4">
                    <p>📅 {t.start_date} → {t.end_date}</p>
                    <p>📊 {streak?.completed_days || 0} / {t.duration_in_days} days completed</p>
                    <p>🔥 Streak: {streak?.current_streak || 0} days</p>
                    <p className={`font-semibold ${t.status === 'FAILED' ? 'text-red-400' : t.status === 'SUCCESS' ? 'text-green-400' : 'text-blue-400'}`}>
                      Status: {t.status}
                    </p>
                  </div>
                  {t.status === 'ACTIVE' && !streak?.today_done && (
                    <button
                      onClick={() => handleCheckin(t.id)}
                      className="w-full p-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
                    >
                      ✅ Mark Today Done
                    </button>
                  )}
                  {t.status === 'ACTIVE' && streak?.today_done && (
                    <div className="text-center text-green-400 font-semibold p-3 bg-green-900/30 rounded-lg">
                      ✅ Done for today!
                    </div>
                  )}
                  {t.status === 'FAILED' && (
                    <div className="text-center text-red-400 font-semibold">❌ FAILED</div>
                  )}
                  {t.status === 'SUCCESS' && (
                    <div className="text-center text-green-400 font-semibold">🎉 COMPLETED!</div>
                  )}
                </div>
              )
            })
          )}
        </div>
      </div>
    </div>
  )
}
