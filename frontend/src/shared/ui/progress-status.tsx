import { useEffect, useState } from 'react'
import { Meter } from './meter'

type ProgressStatusProps = {
  active: boolean
  done?: boolean
  estimateLabel?: string
}

const ESTIMATED_DURATION_MS = 2 * 60 * 1000

export function ProgressStatus({
  active,
  done = false,
  estimateLabel = 'Обычно занимает около 2 минут.',
}: ProgressStatusProps) {
  const [value, setValue] = useState(done ? 100 : 0)

  useEffect(() => {
    if (done) {
      setValue(100)
      return
    }

    if (!active) {
      setValue(0)
      return
    }

    const startedAt = Date.now()
    const timer = window.setInterval(() => {
      const elapsed = Date.now() - startedAt
      const progress = Math.min(92, 12 + (elapsed / ESTIMATED_DURATION_MS) * 80)
      setValue(progress)
    }, 500)

    return () => {
      window.clearInterval(timer)
    }
  }, [active, done])

  return (
    <div className="mt-3 space-y-2">
      <Meter value={done ? 100 : value} />
      <p className="text-xs text-muted">{done ? 'Завершено.' : estimateLabel}</p>
    </div>
  )
}
