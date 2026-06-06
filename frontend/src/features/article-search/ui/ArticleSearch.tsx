import { startTransition, useDeferredValue, useState } from 'react'
import { LoaderCircle, Search } from 'lucide-react'
import { isAxiosError } from 'axios'
import { useQueryClient } from '@tanstack/react-query'
import { useArticles } from '../../../entities/article/api/article-api'
import { useSelectedArticle } from '../../article-picker/model/use-selected-article'
import { Badge } from '../../../shared/ui/badge'
import { Card } from '../../../shared/ui/card'
import { Button } from '../../../shared/ui/button'
import { ProgressStatus } from '../../../shared/ui/progress-status'

export function ArticleSearch() {
  const queryClient = useQueryClient()
  const { selectedArticleId, setSelectedArticleId, searchTerm, setSearchTerm } = useSelectedArticle()
  const [draft, setDraft] = useState(searchTerm)
  const deferredSearch = useDeferredValue(searchTerm)
  const { data: articles = [], isLoading, isFetching, isError, error } = useArticles(deferredSearch)
  const isSearchStarted = Boolean(searchTerm.trim())
  const isSearching = isLoading || isFetching
  const stopSearch = () => {
    void queryClient.cancelQueries({ queryKey: ['articles'] })
    startTransition(() => {
      setSearchTerm('')
    })
  }

  return (
    <Card className="space-y-4">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-muted">Поиск статей</p>
          <h2 className="mt-2 text-2xl text-ink">Найдите статью по теме</h2>
        </div>
        <Badge>{isSearching ? 'Идёт поиск' : `Найдено: ${articles.length}`}</Badge>
      </div>

      <label className="flex items-center gap-3 px-4 py-3 border rounded-full border-line bg-paper">
        <Search className="w-4 h-4 text-muted" />
        <input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Например: llm agents, retrieval, qwen..."
          className="w-full text-sm bg-transparent border-0 outline-none placeholder:text-muted"
        />
        <Button
          type="button"
          disabled={isSearching ? false : !draft.trim()}
          onClick={isSearching
            ? stopSearch
            : () => {
                startTransition(() => {
                  setSearchTerm(draft.trim())
                })
              }}
          className="px-3 py-1.5 text-xs"
        >
          {isSearching ? (
            <>
              <LoaderCircle className="w-4 h-4 animate-spin" />
              Стоп
            </>
          ) : 'Найти'}
        </Button>
      </label>

      <div className="space-y-3">
        {!isSearchStarted && (
          <p className="text-sm leading-7 text-muted">
            Введите тему, ключевые слова или название, чтобы подобрать подходящие статьи.
          </p>
        )}
        {isSearching && (
          <div className="rounded-[22px] border border-line bg-fog/70 p-4 text-sm text-muted">
            <p>Подбираю статьи по вашему запросу.</p>
            <ProgressStatus active estimateLabel="Поиск обычно занимает около 2 минут." />
          </div>
        )}
        {isError && (
          <div className="rounded-[22px] border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {isAxiosError(error) ? error.response?.data?.detail ?? error.message : 'Не удалось выполнить поиск статей.'}
          </div>
        )}
        {isSearchStarted && !isSearching && !isError && articles.length === 0 && (
          <div className="rounded-[22px] border border-line bg-fog/70 p-4 text-sm text-muted">
            По запросу `{searchTerm}` ничего не нашлось. Попробуйте изменить формулировку.
          </div>
        )}
        {articles.map((article) => (
          <button
            key={article.id}
            type="button"
            onClick={() => {
              startTransition(() => {
                setSelectedArticleId(article.id)
              })
            }}
            className={`w-full rounded-[22px] border p-4 text-left transition-all ${
              selectedArticleId === article.id
                ? 'border-ink bg-ink text-paper'
                : 'border-line bg-white/50 text-ink hover:-translate-y-0.5 hover:border-ink'
            }`}
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-mono text-xs uppercase tracking-[0.22em]">
                {article.id}
              </span>
              <span className={`text-xs ${selectedArticleId === article.id ? 'text-paper/70' : 'text-muted'}`}>
                {article.published}
              </span>
            </div>

            <h3 className="mt-3 text-lg leading-snug">{article.title}</h3>

            <div className={`mt-3 rounded-[16px] border px-3 py-2 text-xs ${
              selectedArticleId === article.id
                ? 'border-white/10 bg-white/5 text-paper/78'
                : 'border-line bg-fog/70 text-muted'
            }`}>
              <p className="font-mono uppercase tracking-[0.18em]">Авторы</p>
              <p className="mt-2 tracking-normal normal-case line-clamp-2">{article.authors.join(', ')}</p>
            </div>

            <div className="mt-3">
              <p className={`font-mono text-[11px] uppercase tracking-[0.18em] ${selectedArticleId === article.id ? 'text-paper/60' : 'text-muted'}`}>
                Аннотация
              </p>
              <p className={`mt-2 line-clamp-6 text-sm leading-6 ${selectedArticleId === article.id ? 'text-paper/80' : 'text-muted'}`}>
              {article.abstract}
              </p>
            </div>

            <div className="flex flex-wrap gap-2 mt-3">
              {article.tags.map((tag) => (
                <Badge key={tag} className={selectedArticleId === article.id ? 'border-white/20 bg-white/10 text-paper/80' : ''}>
                  {tag}
                </Badge>
              ))}
            </div>
          </button>
        ))}
      </div>
    </Card>
  )
}
