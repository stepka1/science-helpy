type MeterProps = {
  value: number
}

export function Meter({ value }: MeterProps) {
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-fog">
      <div className="h-full rounded-full bg-ink transition-[width] duration-500" style={{ width: `${value}%` }} />
    </div>
  )
}
