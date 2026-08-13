import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  BookOpen,
  Eye,
  EyeOff,
  GraduationCap,
  LockKeyhole,
  Mail,
  MessageCircle,
  Sparkles,
  TrendingUp,
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'

export function LoginPage() {
  const navigate = useNavigate()
  const { login, register, error: authError } = useAuth()
  
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [isRegistering, setIsRegistering] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    setError(null)
  }

  const handleLogin = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      await login(formData.email, formData.password)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    if (!formData.name.trim()) {
      setError('Please enter your name')
      setLoading(false)
      return
    }

    try {
      await register(formData.email, formData.name, formData.password)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = isRegistering ? handleRegister : handleLogin

  return (
    <main className="min-h-screen bg-[#F8F9FC] p-4 sm:p-6 lg:p-8">
      <div className="mx-auto flex min-h-[calc(100vh-2rem)] max-w-6xl overflow-hidden rounded-2xl bg-white shadow-[0_20px_60px_rgba(0,0,0,0.08)]">
        
        {/* Left Brand Panel */}
        <section className="relative hidden w-1/2 overflow-hidden bg-gradient-to-br from-indigo-500 via-indigo-600 to-violet-600 p-10 text-white lg:flex lg:flex-col lg:justify-between">
          
          {/* Decorative shapes */}
          <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-white/10" />
          <div className="absolute -bottom-32 -left-20 h-80 w-80 rounded-full bg-white/10" />

          <div className="relative z-10">
            <div className="mb-10 flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/15 backdrop-blur">
                <GraduationCap size={25} />
              </div>

              <span className="text-lg font-semibold">
                Study Assistant
              </span>
            </div>

            <div className="max-w-md">
              <h1 className="text-4xl font-bold leading-tight">
                Learn smarter.
                <br />
                Study better.
              </h1>

              <p className="mt-5 text-base leading-7 text-indigo-100">
                Your AI-powered study companion for understanding
                documents, asking questions, and learning more efficiently.
              </p>
            </div>
          </div>

          {/* Illustration */}
          <div className="relative z-10 flex justify-center py-8">
            <div className="relative flex h-52 w-64 items-end justify-center">
              <div className="absolute bottom-0 h-20 w-56 rounded-full bg-indigo-900/20 blur-xl" />

              <div className="absolute bottom-8 left-8 h-16 w-40 rotate-[-5deg] rounded-lg bg-white shadow-lg" />
              <div className="absolute bottom-12 left-12 h-16 w-40 rotate-[4deg] rounded-lg bg-indigo-100 shadow-lg" />
              <div className="absolute bottom-16 left-16 h-16 w-40 rotate-[-2deg] rounded-lg bg-violet-100 shadow-lg" />

              <div className="absolute bottom-28 flex h-20 w-20 items-center justify-center rounded-full bg-white text-indigo-600 shadow-xl">
                <BookOpen size={36} />
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="relative z-10 grid grid-cols-3 gap-4">
            <Feature
              icon={<MessageCircle size={18} />}
              title="Ask Questions"
              description="Get instant answers"
            />

            <Feature
              icon={<Sparkles size={18} />}
              title="Study Smarter"
              description="Summarize and learn"
            />

            <Feature
              icon={<TrendingUp size={18} />}
              title="Track Progress"
              description="Improve every day"
            />
          </div>
        </section>

        {/* Right Login Panel */}
        <section className="flex w-full items-center justify-center px-6 py-10 sm:px-12 lg:w-1/2 lg:px-16">
          <div className="w-full max-w-md">
            
            {/* Mobile brand */}
            <div className="mb-8 flex items-center gap-3 lg:hidden">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white">
                <GraduationCap size={22} />
              </div>

              <span className="font-semibold text-gray-900">
                Study Assistant
              </span>
            </div>

            {/* Heading */}
            <div className="mb-8">
              <h2 className="text-3xl font-bold tracking-tight text-[#17203A]">
                {isRegistering ? 'Create Account' : 'Welcome Back!'}
              </h2>

              <p className="mt-2 text-sm text-gray-500">
                {isRegistering
                  ? 'Sign up to start your learning journey'
                  : 'Log in to continue your learning journey'}
              </p>
            </div>

            {/* Error Message */}
            {(error || authError) && (
              <div className="mb-6 rounded-lg bg-red-50 p-4 text-sm text-red-700 border border-red-200">
                {error || authError}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              
              {/* Name (Registration only) */}
              {isRegistering && (
                <div>
                  <label
                    htmlFor="name"
                    className="mb-2 block text-sm font-medium text-gray-700"
                  >
                    Full Name
                  </label>

                  <input
                    id="name"
                    name="name"
                    type="text"
                    required={isRegistering}
                    placeholder="Enter your full name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="h-12 w-full rounded-lg border border-gray-200 bg-white px-4 text-sm text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                  />
                </div>
              )}

              {/* Email */}
              <div>
                <label
                  htmlFor="email"
                  className="mb-2 block text-sm font-medium text-gray-700"
                >
                  Email
                </label>

                <div className="relative">
                  <Mail
                    size={18}
                    className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
                  />

                  <input
                    id="email"
                    name="email"
                    type="email"
                    required
                    placeholder="Enter your email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="h-12 w-full rounded-lg border border-gray-200 bg-white pl-11 pr-4 text-sm text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <label
                    htmlFor="password"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Password
                  </label>

                  {!isRegistering && (
                    <button
                      type="button"
                      className="text-xs font-medium text-indigo-600 transition hover:text-indigo-700"
                    >
                      Forgot password?
                    </button>
                  )}
                </div>

                <div className="relative">
                  <LockKeyhole
                    size={18}
                    className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
                  />

                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="h-12 w-full rounded-lg border border-gray-200 bg-white pl-11 pr-11 text-sm text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                  />

                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 transition hover:text-gray-600"
                    aria-label={
                      showPassword
                        ? 'Hide password'
                        : 'Show password'
                    }
                  >
                    {showPassword ? (
                      <EyeOff size={18} />
                    ) : (
                      <Eye size={18} />
                    )}
                  </button>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="h-12 w-full rounded-lg bg-indigo-600 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? (isRegistering ? 'Creating account...' : 'Logging in...') : (isRegistering ? 'Sign Up' : 'Log In')}
              </button>
            </form>

            {/* Toggle Auth Mode */}
            <p className="mt-7 text-center text-sm text-gray-500">
              {isRegistering ? (
                <>
                  Already have an account?{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setIsRegistering(false)
                      setError(null)
                      setFormData({ email: '', password: '', name: '' })
                    }}
                    className="font-semibold text-indigo-600 hover:text-indigo-700"
                  >
                    Log in
                  </button>
                </>
              ) : (
                <>
                  Don't have an account?{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setIsRegistering(true)
                      setError(null)
                      setFormData({ email: '', password: '', name: '' })
                    }}
                    className="font-semibold text-indigo-600 hover:text-indigo-700"
                  >
                    Sign up
                  </button>
                </>
              )}
            </p>
          </div>
        </section>
      </div>
    </main>
  )
}

function Feature({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="text-center">
      <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-white/15">
        {icon}
      </div>

      <p className="text-xs font-semibold">{title}</p>
      <p className="mt-1 text-[11px] text-indigo-100">
        {description}
      </p>
    </div>
  )
}
