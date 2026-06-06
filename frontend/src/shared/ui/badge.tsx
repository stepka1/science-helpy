import type { HTMLAttributes } from 'react'
import { cn } from '../lib/cn'

export function Badge({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border border-line bg-fog px-3 py-1 text-[11px] uppercase tracking-[0.24em] text-muted',
        className,
      )}
      {...props}
    />
  )
}
