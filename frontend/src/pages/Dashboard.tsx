import React, { useEffect, useState } from 'react'
import axios from 'axios'

const DASHBOARD_CACHE_KEY = 'accesslearn.dashboard.cache'
const AUTH_TOKEN_KEY = 'accesslearn.auth.token'

function AuthCard({
  mode,
  onModeChange,
  onAuthenticated,
}: {
  mode: 'login' | 'register'
  onModeChange: (nextMode: 'login' | 'register') => void
  onAuthenticated: (token: string) => void
}) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const submit = async () => {
    setBusy(true)
    setError('')
    try {
      const res = await axios.post(`http://localhost:8000/auth/${mode}`, { email, password })
      const token = res.data.token
      onAuthenticated(token)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Authentication failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-lg">
      <div className="mb-6 text-center">
        <p className="text-xs uppercase tracking-[0.3em] text-indigo-500">AccessLearn</p>
        <h2 className="mt-2 text-2xl font-bold text-slate-900">Welcome back</h2>
        <p className="mt-2 text-sm text-slate-500">Sign in to view your study dashboard.</p>
      </div>

      <div className="mb-4 flex rounded-full bg-slate-100 p-1">
        <button type="button" onClick={() => onModeChange('login')} className={`flex-1 rounded-full px-3 py-2 text-sm font-semibold ${mode === 'login' ? 'bg-slate-900 text-white' : 'text-slate-600'}`}>Login</button>
        <button type="button" onClick={() => onModeChange('register')} className={`flex-1 rounded-full px-3 py-2 text-sm font-semibold ${mode === 'register' ? 'bg-slate-900 text-white' : 'text-slate-600'}`}>Register</button>
      </div>

      <label className="block text-sm font-medium text-slate-700">Email</label>
      <input value={email} onChange={(e) => setEmail(e.target.value)} className="mt-2 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" placeholder="you@example.com" />

      <label className="mt-4 block text-sm font-medium text-slate-700">Password</label>
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="mt-2 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" placeholder="••••••••" />

      {error && <p className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}

      <button disabled={busy || !email || !password} onClick={submit} className="mt-5 w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300">
        {busy ? 'Please wait…' : mode === 'login' ? 'Login' : 'Create account'}
      </button>
    </div>
  )
}

function FileUpload({onUploaded}:{onUploaded:(id:number)=>void}){
  const [file, setFile] = useState<File|null>(null)
  const upload=async()=>{
    if(!file) return
    const fd = new FormData()
    fd.append('file', file)
    const res = await axios.post('http://localhost:8000/upload/', fd, {headers: {'Content-Type':'multipart/form-data'}})
    onUploaded(res.data.id)
  }
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-800">Upload a PDF</h2>
          <p className="text-sm text-slate-500">Get a summary, voice narration, and YouTube recommendations for the document topics.</p>
        </div>
        <label className="cursor-pointer rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-100">
          <input type="file" accept="application/pdf" className="hidden" onChange={(e: React.ChangeEvent<HTMLInputElement>)=>setFile(e.target.files?.[0]||null)} />
          {file ? file.name : 'Choose PDF file'}
        </label>
      </div>
      <button onClick={upload} className="mt-4 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700">Upload & Process</button>
    </div>
  )
}

function AudioPlayer({src}:{src?:string}){
  if(!src) return null
  const audioSrc = src.startsWith('http') ? src : `http://localhost:8000${src}`
  return (<audio controls src={audioSrc} className="w-full rounded-lg" />)
}

function MediaLink({label, href}:{label:string; href?:string}){
  if (!href) return <p className="text-sm text-slate-500">Not ready</p>
  return <a className="inline-flex items-center rounded-full bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 transition hover:bg-blue-100" href={`http://localhost:8000${href}`} target="_blank" rel="noreferrer">{label}</a>
}

function generateFlashcards(summaryText: string) {
  const sentences = summaryText
    .split(/[.!?]+/)
    .map((item) => item.trim())
    .filter((item) => item.length > 30)

  return sentences.slice(0, 4).map((sentence, index) => ({
    id: `${index}-${sentence.slice(0, 12)}`,
    front: sentence.length > 80 ? `${sentence.slice(0, 80)}…` : sentence,
    back: sentence,
  }))
}

function generateCourseRecommendations(summaryText: string) {
  const normalized = summaryText.toLowerCase()
  const courses: Array<{ title: string; reason: string; url: string }> = []

  if (normalized.includes('python') || normalized.includes('programming')) {
    courses.push({
      title: 'Python for Everybody',
      reason: 'Great for building a strong foundation in programming concepts that appear in the document.',
      url: 'https://www.coursera.org/specializations/python',
    })
  }

  if (normalized.includes('machine learning') || normalized.includes('artificial intelligence') || normalized.includes('ai')) {
    courses.push({
      title: 'Machine Learning Specialization',
      reason: 'A highly popular pathway for AI and ML concepts connected to the uploaded study topics.',
      url: 'https://www.coursera.org/specializations/machine-learning-introduction',
    })
  }

  if (normalized.includes('data') || normalized.includes('analytics')) {
    courses.push({
      title: 'Google Data Analytics Professional Certificate',
      reason: 'Useful when the summary emphasizes data analysis, dashboards, and analytical thinking.',
      url: 'https://www.coursera.org/professional-certificates/google-data-analytics',
    })
  }

  if (normalized.includes('cloud') || normalized.includes('network')) {
    courses.push({
      title: 'AWS Cloud Practitioner Essentials',
      reason: 'Recommended when the material focuses on cloud systems, networks, and modern infrastructure fundamentals.',
      url: 'https://aws.amazon.com/training/learn-about/cloud-practitioner/',
    })
  }

  if (normalized.includes('database') || normalized.includes('sql')) {
    courses.push({
      title: 'SQL for Data Science',
      reason: 'Helpful for study areas involving databases, querying, and data organization.',
      url: 'https://www.coursera.org/learn/sql-for-data-science',
    })
  }

  if (courses.length === 0) {
    courses.push({
      title: 'Study Skills & Academic Growth Bootcamp',
      reason: 'A broad course path to improve the learning strategy behind the uploaded material.',
      url: 'https://www.coursera.org/',
    })
  }

  return courses.slice(0, 3)
}

export default function Dashboard(){
  const [token, setToken] = useState<string | null>(null)
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')
  const [docId, setDocId] = useState<number|undefined>()
  const [dashboard, setDashboard] = useState<any>(null)
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [summary, setSummary] = useState<string>('')
  const [quiz, setQuiz] = useState<any[]>([])
  const [quizAnswers, setQuizAnswers] = useState<Record<string, any>>({})
  const [quizSubmitted, setQuizSubmitted] = useState(false)
  const [quizScore, setQuizScore] = useState<number | null>(null)
  const [activeTab, setActiveTab] = useState<'summary' | 'youtube' | 'quiz' | 'insights'>('summary')
  const [busy, setBusy] = useState(false)

  const handleAuthenticated = (nextToken: string) => {
    setToken(nextToken)
    window.localStorage.setItem(AUTH_TOKEN_KEY, nextToken)
    axios.defaults.headers.common.Authorization = `Bearer ${nextToken}`
  }

  useEffect(() => {
    const savedToken = window.localStorage.getItem(AUTH_TOKEN_KEY)
    if (savedToken) {
      setToken(savedToken)
      axios.defaults.headers.common.Authorization = `Bearer ${savedToken}`
    }
  }, [])

  const flashcards = generateFlashcards(summary)
  const courseRecommendations = generateCourseRecommendations(summary)
  const quizCount = quiz.length
  const readinessScore = quizSubmitted && quizCount > 0 ? Math.round(((quizScore ?? 0) / quizCount) * 100) : null
  const performanceLabel = readinessScore === null
    ? 'Not graded yet'
    : readinessScore >= 80
      ? 'Excellent understanding'
      : readinessScore >= 60
        ? 'Good progress'
        : 'Needs more revision'

  useEffect(() => {
    const cached = window.localStorage.getItem(DASHBOARD_CACHE_KEY)
    if (!cached) return

    try {
      const parsed = JSON.parse(cached)
      if (parsed.docId) setDocId(parsed.docId)
      if (parsed.dashboard) setDashboard(parsed.dashboard)
      if (parsed.recommendations) setRecommendations(parsed.recommendations)
      if (parsed.summary) setSummary(parsed.summary)
      if (parsed.quiz) setQuiz(parsed.quiz)
      if (parsed.quizAnswers) setQuizAnswers(parsed.quizAnswers)
      if (parsed.quizSubmitted) setQuizSubmitted(parsed.quizSubmitted)
      if (typeof parsed.quizScore === 'number') setQuizScore(parsed.quizScore)
      if (parsed.activeTab) setActiveTab(parsed.activeTab)

      if (parsed.docId) {
        axios.get(`http://localhost:8000/dashboard/${parsed.docId}`)
          .then((response) => {
            const nextDashboard = response.data
            const nextSummary = response.data.summary_text || ''
            setDashboard(nextDashboard)
            setSummary(nextSummary)
            persistState({
              docId: parsed.docId,
              dashboard: nextDashboard,
              recommendations: parsed.recommendations || [],
              summary: nextSummary,
              quiz: parsed.quiz || [],
              quizAnswers: parsed.quizAnswers || {},
              quizSubmitted: parsed.quizSubmitted || false,
              quizScore: typeof parsed.quizScore === 'number' ? parsed.quizScore : null,
              activeTab: parsed.activeTab || 'summary',
            })
          })
          .catch(() => {
            // Fall back to the cached summary if the backend is unavailable.
          })
      }

      if (parsed.docId && (!Array.isArray(parsed.quiz) || parsed.quiz.length === 0)) {
        axios.post('http://localhost:8000/generate-quiz/', {document_id: parsed.docId})
          .then((response) => {
            const nextQuiz = response.data.quiz || []
            setQuiz(nextQuiz)
            window.localStorage.setItem(DASHBOARD_CACHE_KEY, JSON.stringify({
              docId: parsed.docId,
              dashboard: parsed.dashboard,
              recommendations: parsed.recommendations || [],
              summary: parsed.summary || '',
              quiz: nextQuiz,
              quizAnswers: parsed.quizAnswers || {},
              quizSubmitted: parsed.quizSubmitted || false,
              quizScore: typeof parsed.quizScore === 'number' ? parsed.quizScore : null,
              activeTab: parsed.activeTab || 'summary',
            }))
          })
          .catch(() => {
            // Leave the existing dashboard state intact if quiz generation fails.
          })
      }
    } catch {
      window.localStorage.removeItem(DASHBOARD_CACHE_KEY)
    }
  }, [])

  const persistState = (nextState: { docId?: number; dashboard?: any; recommendations?: any[]; summary?: string; quiz?: any[]; quizAnswers?: Record<string, any>; quizSubmitted?: boolean; quizScore?: number | null; activeTab?: 'summary' | 'youtube' | 'quiz' | 'insights' }) => {
    window.localStorage.setItem(DASHBOARD_CACHE_KEY, JSON.stringify(nextState))
  }

  const updateQuizAnswer = (questionId: string, value: any) => {
    const nextAnswers = { ...quizAnswers, [questionId]: value }
    setQuizAnswers(nextAnswers)
    persistState({ docId, dashboard, recommendations, summary, quiz, quizAnswers: nextAnswers, quizSubmitted, quizScore, activeTab })
  }

  const logout = () => {
    setToken(null)
    setDocId(undefined)
    setDashboard(null)
    setRecommendations([])
    setSummary('')
    setQuiz([])
    setQuizAnswers({})
    setQuizSubmitted(false)
    setQuizScore(null)
    setActiveTab('summary')
    window.localStorage.removeItem(AUTH_TOKEN_KEY)
    window.localStorage.removeItem(DASHBOARD_CACHE_KEY)
    delete axios.defaults.headers.common.Authorization
  }

  const submitQuiz = () => {
    let score = 0
    quiz.forEach((question) => {
      const answer = quizAnswers[question.id]
      if (question.type === 'mcq') {
        if ((answer || '').trim() === question.answer) score += 1
      } else if (question.type === 'true_false') {
        if (String(answer) === String(question.answer)) score += 1
      } else if (question.type === 'fill_blank') {
        const normalized = String(answer || '').trim().toLowerCase()
        const accepted = (question.acceptable_answers || []).map((item: string) => item.toLowerCase())
        if (accepted.includes(normalized) || accepted.some((item: string) => normalized.includes(item))) score += 1
      } else if (question.type === 'short_answer') {
        const normalized = String(answer || '').toLowerCase()
        const matches = (question.keywords || []).filter((item: string) => normalized.includes(item.toLowerCase())).length
        if (matches >= 2 || normalized.length > 25) score += 1
      }
    })
    setQuizScore(score)
    setQuizSubmitted(true)
    persistState({ docId, dashboard, recommendations, summary, quiz, quizAnswers, quizSubmitted: true, quizScore: score, activeTab })
  }

  const handleUploaded = async (id:number)=>{
    setDocId(id)
    setBusy(true)
    try {
      await axios.post('http://localhost:8000/extract/', {document_id: id})
      await axios.post('http://localhost:8000/simplify/', {document_id: id, level: 'beginner'})
      await axios.post('http://localhost:8000/generate-audio/', {document_id: id})
      await axios.post('http://localhost:8000/generate-captions/', {document_id: id})
      const recommendationsRes = await axios.post('http://localhost:8000/generate-video/', {document_id: id})
      const quizRes = await axios.post('http://localhost:8000/generate-quiz/', {document_id: id})
      const nextRecommendations = recommendationsRes.data.youtube_recommendations || []
      const nextQuiz = quizRes.data.quiz || []
      setRecommendations(nextRecommendations)
      setQuiz(nextQuiz)
      setQuizAnswers({})
      setQuizSubmitted(false)
      setQuizScore(null)
      const res = await axios.get(`http://localhost:8000/dashboard/${id}`)
      const nextDashboard = res.data
      const nextSummary = res.data.summary_text || ''
      setDashboard(nextDashboard)
      setSummary(nextSummary)
      persistState({ docId: id, dashboard: nextDashboard, recommendations: nextRecommendations, summary: nextSummary, quiz: nextQuiz, quizAnswers: {}, quizSubmitted: false, quizScore: null, activeTab: 'summary' })
    } finally {
      setBusy(false)
    }
  }

  const generateVideo = async () => {
    if (!docId) return
    setBusy(true)
    try {
      const res = await axios.post('http://localhost:8000/generate-video/', {document_id: docId})
      const quizRes = await axios.post('http://localhost:8000/generate-quiz/', {document_id: docId})
      const nextRecommendations = res.data.youtube_recommendations || []
      const nextQuiz = quizRes.data.quiz || []
      setRecommendations(nextRecommendations)
      setQuiz(nextQuiz)
      const dashboardRes = await axios.get(`http://localhost:8000/dashboard/${docId}`)
      const nextDashboard = dashboardRes.data
      const nextSummary = dashboardRes.data.summary_text || ''
      setDashboard(nextDashboard)
      setSummary(nextSummary)
      persistState({ docId, dashboard: nextDashboard, recommendations: nextRecommendations, summary: nextSummary, quiz: nextQuiz, quizAnswers, quizSubmitted, quizScore, activeTab })
    } finally {
      setBusy(false)
    }
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-slate-100 p-6 md:p-10">
        <div className="mx-auto max-w-6xl">
          <div className="mb-8 overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 p-8 text-white shadow-2xl ring-1 ring-white/10 md:p-10">
            <p className="text-xs uppercase tracking-[0.3em] text-indigo-200">AccessLearn</p>
            <h1 className="mt-3 font-serif text-4xl font-bold leading-tight md:text-5xl">Secure PDF study dashboard</h1>
            <p className="mt-4 text-sm leading-6 text-slate-300 md:text-base">Create an account or sign in to unlock the dashboard, summary, quiz, and learning recommendations.</p>
          </div>
          <AuthCard mode={authMode} onModeChange={setAuthMode} onAuthenticated={handleAuthenticated} />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-100 p-6 md:p-10">
      <div className="mx-auto max-w-6xl space-y-6">
        <div className="overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 p-8 text-white shadow-2xl ring-1 ring-white/10 md:p-10">
          <div className="max-w-3xl">
            <p className="text-xs uppercase tracking-[0.3em] text-indigo-200">AccessLearn</p>
            <h1 className="mt-3 font-serif text-4xl font-bold leading-tight md:text-5xl">Turn a PDF into a summary, voice narration, and study videos.</h1>
            <p className="mt-4 text-sm leading-6 text-slate-300 md:text-base">Upload a document and get a cleaner summary, audio playback, captions, and properly linked YouTube recommendations for the topics inside the PDF.</p>
          </div>
        </div>

        <FileUpload onUploaded={handleUploaded} />

        {docId && (
          <button disabled={busy} onClick={generateVideo} className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50">
            {busy ? 'Processing…' : 'Refresh YouTube Suggestions'}
          </button>
        )}

        {dashboard && (
          <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-soft shadow-sm">
            <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-4">
              {([
                ['summary', 'Summary'],
                ['youtube', 'YouTube'],
                ['quiz', 'Quiz'],
                ['insights', 'Insights'],
              ] as const).map(([key, label]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => {
                    setActiveTab(key)
                    persistState({ docId, dashboard, recommendations, summary, quiz, quizAnswers, quizSubmitted, quizScore, activeTab: key })
                  }}
                  className={`rounded-full px-4 py-2 text-sm font-semibold transition ${activeTab === key ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="mt-6">
              {activeTab === 'summary' && (
                <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
                    <h2 className="text-lg font-semibold text-slate-800">Document</h2>
                    <p className="mt-2 text-sm text-slate-600">{dashboard.document.filename}</p>
                  </div>

                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
                    <h2 className="text-lg font-semibold text-slate-800">Summary</h2>
                    <div className="mt-3 max-h-72 overflow-y-auto rounded-2xl border border-slate-200 bg-white p-4">
                      <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">{summary || 'Not ready'}</p>
                    </div>
                    {summary && <p className="mt-4 text-xs uppercase tracking-[0.2em] text-slate-400">Full auto-generated summary</p>}
                  </div>

                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6 lg:col-span-2">
                    <h2 className="text-lg font-semibold text-slate-800">Voice Summary</h2>
                    <div className="mt-4">
                      {dashboard.outputs?.audio ? <AudioPlayer src={`http://localhost:8000${dashboard.outputs.audio}`} /> : <p className="text-sm text-slate-500">Not ready</p>}
                    </div>
                    <div className="mt-3"><MediaLink label="Open audio file" href={dashboard.outputs?.audio} /></div>
                  </div>

                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
                    <h2 className="text-lg font-semibold text-slate-800">Captions</h2>
                    <div className="mt-3"><MediaLink label="Download SRT" href={dashboard.outputs?.captions} /></div>
                  </div>
                </div>
              )}

              {activeTab === 'youtube' && (
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
                  <h2 className="text-lg font-semibold text-slate-800">Recommended YouTube Videos</h2>
                  {recommendations.length > 0 ? (
                    <div className="mt-4 space-y-3">
                      {recommendations.map((item, index) => (
                        <div key={`${item.title}-${index}`} className="rounded-2xl border border-slate-200 bg-gradient-to-br from-white to-slate-50 p-4 shadow-sm">
                          <p className="font-medium text-slate-800">{item.title}</p>
                          <p className="mt-1 text-sm text-slate-600">{item.reason}</p>
                          <button
                            type="button"
                            className="mt-3 inline-flex items-center rounded-full bg-red-50 px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-100"
                            onClick={() => window.location.assign(item.url)}
                          >
                            Open on YouTube
                          </button>
                          <p className="mt-2 break-all text-xs text-slate-400">{item.url}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="mt-3 text-sm text-slate-500">Recommendations will appear here after the PDF is processed.</p>
                  )}
                </div>
              )}

              {activeTab === 'quiz' && (
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h2 className="text-lg font-semibold text-slate-800">Quiz Generator</h2>
                      <p className="text-sm text-slate-500">Answer the questions and then submit to see your score, the correct answers, and explanations.</p>
                    </div>
                    <button
                      type="button"
                      onClick={submitQuiz}
                      disabled={!quiz.length}
                      className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:bg-emerald-200"
                    >
                      Submit Quiz
                    </button>
                  </div>

                  {quizScore !== null && (
                    <div className="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-emerald-900">
                      <p className="text-sm font-semibold">Score: {quizScore}/{quiz.length}</p>
                    </div>
                  )}

                  {quiz.length > 0 ? (
                    <div className="mt-5 space-y-4">
                      {quiz.map((question, index) => {
                        const userAnswer = quizAnswers[question.id]
                        const isAnswered = quizSubmitted
                        let isCorrect = false
                        if (quizSubmitted) {
                          if (question.type === 'mcq') {
                            isCorrect = userAnswer === question.answer
                          } else if (question.type === 'true_false') {
                            isCorrect = String(userAnswer) === String(question.answer)
                          } else if (question.type === 'fill_blank') {
                            const normalized = String(userAnswer || '').trim().toLowerCase()
                            const accepted = (question.acceptable_answers || []).map((item: string) => item.toLowerCase())
                            isCorrect = accepted.includes(normalized) || accepted.some((item: string) => normalized.includes(item))
                          } else if (question.type === 'short_answer') {
                            const normalized = String(userAnswer || '').toLowerCase()
                            isCorrect = (question.keywords || []).filter((item: string) => normalized.includes(item.toLowerCase())).length >= 2 || normalized.length > 25
                          }
                        }

                        return (
                          <div key={question.id} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                            <p className="text-sm font-semibold text-slate-500">Question {index + 1} · {question.type.replace('_', ' ')}</p>
                            <p className="mt-1 text-base font-medium text-slate-800">{question.question}</p>

                            {question.type === 'mcq' && (
                              <div className="mt-3 grid gap-2">
                                {question.options.map((option: string) => (
                                  <label key={option} className="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700 hover:bg-slate-100">
                                    <input
                                      type="radio"
                                      name={question.id}
                                      checked={userAnswer === option}
                                      onChange={() => updateQuizAnswer(question.id, option)}
                                    />
                                    {option}
                                  </label>
                                ))}
                              </div>
                            )}

                            {question.type === 'true_false' && (
                              <div className="mt-3 flex gap-3">
                                {['True', 'False'].map((option) => (
                                  <button
                                    key={option}
                                    type="button"
                                    onClick={() => updateQuizAnswer(question.id, option === 'True')}
                                    className={`rounded-full px-4 py-2 text-sm font-semibold ${userAnswer === (option === 'True') ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
                                  >
                                    {option}
                                  </button>
                                ))}
                              </div>
                            )}

                            {question.type === 'fill_blank' && (
                              <input
                                className="mt-3 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 outline-none focus:border-slate-400"
                                value={userAnswer || ''}
                                onChange={(event) => updateQuizAnswer(question.id, event.target.value)}
                                placeholder="Type your answer here"
                              />
                            )}

                            {question.type === 'short_answer' && (
                              <textarea
                                className="mt-3 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 outline-none focus:border-slate-400"
                                rows={4}
                                value={userAnswer || ''}
                                onChange={(event) => updateQuizAnswer(question.id, event.target.value)}
                                placeholder="Write a short answer here"
                              />
                            )}

                            {isAnswered && (
                              <div className={`mt-4 rounded-xl border p-4 text-sm ${isCorrect ? 'border-emerald-200 bg-emerald-50 text-emerald-900' : 'border-rose-200 bg-rose-50 text-rose-900'}`}>
                                <p className="font-semibold">{isCorrect ? 'Correct' : 'Incorrect'}</p>
                                <p className="mt-1">Correct answer: {Array.isArray(question.answer) ? question.answer.join(', ') : String(question.answer)}</p>
                                <p className="mt-1">Explanation: {question.explanation}</p>
                              </div>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  ) : (
                    <p className="mt-4 text-sm text-slate-500">Quiz will appear here after the PDF is processed.</p>
                  )}
                </div>
              )}

              {activeTab === 'insights' && (
                <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
                    <h2 className="text-lg font-semibold text-slate-800">Performance Analysis</h2>
                    <div className="mt-4 space-y-3 text-sm text-slate-700">
                      <div className="rounded-2xl border border-slate-200 bg-white p-4">
                        <p className="font-semibold text-slate-800">Study readiness</p>
                        <p className="mt-1">{performanceLabel}</p>
                      </div>
                      <div className="rounded-2xl border border-slate-200 bg-white p-4">
                        <p className="font-semibold text-slate-800">Quiz result</p>
                        <p className="mt-1">{quizScore !== null ? `${quizScore}/${quizCount}` : 'No quiz attempt yet'}</p>
                      </div>
                      <div className="rounded-2xl border border-slate-200 bg-white p-4">
                        <p className="font-semibold text-slate-800">Summary strength</p>
                        <p className="mt-1">{summary.length > 120 ? 'Strong topic coverage available' : 'Summary is still being formed'}</p>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
                    <h2 className="text-lg font-semibold text-slate-800">Flash Cards</h2>
                    <div className="mt-4 space-y-3">
                      {flashcards.length > 0 ? flashcards.map((card) => (
                        <div key={card.id} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Flash card</p>
                          <p className="mt-2 text-sm font-semibold text-slate-800">{card.front}</p>
                          <p className="mt-2 text-sm text-slate-600">{card.back}</p>
                        </div>
                      )) : <p className="text-sm text-slate-500">Flash cards will appear once the summary is ready.</p>}
                    </div>
                  </div>

                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6 lg:col-span-2">
                    <h2 className="text-lg font-semibold text-slate-800">Viral Course Recommendations</h2>
                    <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
                      {courseRecommendations.map((course) => (
                        <div key={course.title} className="rounded-2xl border border-slate-200 bg-gradient-to-br from-white to-indigo-50 p-4 shadow-sm">
                          <p className="text-sm font-semibold text-slate-800">{course.title}</p>
                          <p className="mt-2 text-sm text-slate-600">{course.reason}</p>
                          <a className="mt-3 inline-flex items-center rounded-full bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-700 transition hover:bg-indigo-100" href={course.url} target="_blank" rel="noreferrer">Explore course</a>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
