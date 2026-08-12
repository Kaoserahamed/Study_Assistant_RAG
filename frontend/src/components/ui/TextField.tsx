import { type InputHTMLAttributes, forwardRef } from 'react'

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

export const TextField = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ label, id, className = '', ...props }, ref) => {
    return (
      <label htmlFor={id} className="block">
        {label && <span className="block text-xs font-medium text-ink-soft mb-1.5">{label}</span>}
        <input
          ref={ref}
          id={id}
          className={`w-full rounded-md border border-paper-line bg-white px-3 py-2 text-sm text-ink placeholder:text-ink-faint focus:border-denim outline-none transition-colors ${className}`}
          {...props}
        />
      </label>
    )
  },
)
TextField.displayName = 'TextField'
