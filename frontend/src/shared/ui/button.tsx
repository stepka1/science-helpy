import type { ButtonHTMLAttributes } from 'react'
import { cn } from '../lib/cn'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'ghost' | 'outline'
}

export function Button({ className, variant = 'primary', ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded-full border px-4 py-2 text-sm font-medium transition-all duration-200 hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink/20 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0',
        variant === 'primary' && 'border-ink bg-ink text-paper shadow-[0_14px_30px_rgba(17,17,17,0.16)] hover:bg-[#1d1d1d]',
        variant === 'outline' && 'border-line bg-white/82 text-ink hover:border-ink/25 hover:bg-white',
        variant === 'ghost' && 'border-transparent bg-transparent text-muted hover:border-line hover:bg-white/70 hover:text-ink',
        className,
      )}
      {...props}
    />
  )
}
