import { useQuery } from '@tanstack/react-query'
import { HeartPulse, Sparkles } from 'lucide-react'
import { useSelectedArticle } from '../../features/article-picker/model/use-selected-article'
import { http } from '../../shared/api/http'
import { Card } from '../../shared/ui/card'

export function ActivityOverview() {
  const { selectedArticleId } = useSelectedArticle()
  const { data: health, isLoading, isError } = useQuery({
    queryKey: ['api-health'],
    queryFn: async () => {
      const { data } = await http.get<{ status: string; message: string }>('/health')
      return data
    },
  })

  if (isLoading) {
    return <Card>Проверяю, всё ли готово к работе...</Card>
  }

  if (isError || !health) {
    return <Card>Сервис временно недоступен. Попробуйте обновить страницу чуть позже.</Card>
  }

  return (
    <div className="space-y-5">
      <Card className="rounded-[24px] bg-ink p-5 text-paper shadow-none">
        <p className="font-mono text-xs uppercase tracking-[0.22em] text-paper/60">Статус сервиса</p>
        <div className="mt-4 flex items-center gap-3">
          <HeartPulse className="h-5 w-5 text-paper" />
          <div>
            <p className="text-lg text-paper">Всё работает</p>
            <p className="text-sm text-paper/70">Можно искать статьи и запускать анализ.</p>
          </div>
        </div>
      </Card>

      <Card className="rounded-[24px] bg-white/65 p-5 shadow-none">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-muted" />
          <h2 className="text-xl text-ink">Выбранная статья</h2>
        </div>
        <p className="mt-3 text-sm leading-7 text-muted">
          {selectedArticleId
            ? `Статья ${selectedArticleId} готова к разбору.`
            : 'Статья ещё не выбрана. Начните с поиска.'}
        </p>
      </Card>
    </div>
  )
}
