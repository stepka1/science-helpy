import type { HTMLAttributes } from 'react'
import { cn } from '../lib/cn'

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'rounded-[28px] border border-line bg-white/75 p-5 shadow-panel backdrop-blur-sm',
        className,
      )}
      {...props}
    />
  )
}
