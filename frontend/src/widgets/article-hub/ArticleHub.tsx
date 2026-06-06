import type { ReactNode } from 'react'
import { isAxiosError } from 'axios'
import {
  BookOpen,
  BrainCircuit,
  CalendarDays,
  ChevronRight,
  Download,
  ExternalLink,
  FileCode2,
  FileText,
  FolderSearch,
  LoaderCircle,
  ScrollText,
  Sparkles,
  Telescope,
} from 'lucide-react'
import {
  useArticleDetail,
  useArticleEvaluation,
  useArticleParse,
  useArticleReview,
  useGenerateArticleEvaluation,
  useGenerateArticleReview,
} from '../../entities/article/api/article-api'
import { useSelectedArticle } from '../../features/article-picker/model/use-selected-article'
import type { Evaluation, Review } from '../../shared/types/article'
import { Badge } from '../../shared/ui/badge'
import { Button } from '../../shared/ui/button'
import { Card } from '../../shared/ui/card'
import { Meter } from '../../shared/ui/meter'
import { ProgressStatus } from '../../shared/ui/progress-status'

export function ArticleHub() {
  const { selectedArticleId, setSelectedArticleId } = useSelectedArticle()
  const articleQuery = useArticleDetail(selectedArticleId)
  const article = articleQuery.data
  const articleBackendId = article?.id ?? ''

  const parseMutation = useArticleParse(articleBackendId)
  const evaluationQuery = useArticleEvaluation(articleBackendId)
  const reviewQuery = useArticleReview(articleBackendId)
  const evaluationMutation = useGenerateArticleEvaluation(articleBackendId)
  const reviewMutation = useGenerateArticleReview(articleBackendId)

  const evaluation = evaluationQuery.data ?? null
  const review = reviewQuery.data ?? null

  const isDownloading = articleQuery.isLoading || articleQuery.isFetching
  const isParsing = parseMutation.isPending
  const isEvaluating = evaluationMutation.isPending
  const isWritingReview = reviewMutation.isPending
  const inferredParsing = !article?.parsedContent && (isEvaluating || isWritingReview)

  if (!selectedArticleId) {
    return (
      <Card className="min-h-[640px]">
        <div className="space-y-8">
          <div className="max-w-2xl space-y-4">
            <p className="font-mono text-xs uppercase tracking-[0.28em] text-muted">Рабочая область</p>
            <h2 className="text-3xl text-ink md:text-4xl">Выберите статью из результатов поиска.</h2>
            <p className="text-base leading-8 text-muted">
              После выбора здесь откроется вся рабочая зона: исходные материалы, текст статьи, оценка, краткая выжимка и полный обзор.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <WorkspaceTile
              icon={<Telescope className="h-5 w-5" />}
              title="1. Найдите публикацию"
              description="Введите тему, название или ключевые слова, а затем выберите наиболее подходящую статью."
            />
            <WorkspaceTile
              icon={<FileText className="h-5 w-5" />}
              title="2. Откройте материалы"
              description="Здесь появятся файлы статьи и текстовая версия, которую можно читать прямо в интерфейсе."
            />
            <WorkspaceTile
              icon={<Sparkles className="h-5 w-5" />}
              title="3. Запустите разбор"
              description="Получите оценку, краткое резюме и полный обзор без перехода между разными экранами."
            />
          </div>

          <div className="rounded-[28px] border border-line bg-fog/70 p-5">
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-muted">Что будет доступно</p>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <PreviewChip label="Файлы статьи" value="PDF, TeX и основные сведения о публикации" />
              <PreviewChip label="Текст для чтения" value="Подготовленная версия статьи прямо на странице" />
              <PreviewChip label="Оценка" value="Новизна, строгость, влияние и краткий комментарий" />
              <PreviewChip label="Обзор" value="Резюме, методы, результаты, критика и применение" />
            </div>
          </div>
        </div>
      </Card>
    )
  }

  if (articleQuery.isLoading || (articleQuery.isFetching && !article)) {
    return (
      <Card className="min-h-[640px] space-y-4">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-muted">Подготовка</p>
        <h2 className="text-2xl text-ink">Подготавливаю материалы статьи.</h2>
        <LoadingBlock title="Идёт загрузка" description="Собираю описание статьи и доступные файлы, чтобы можно было перейти к разбору." />
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <Step title="1. Загрузка" description="собираю материалы статьи" state="active" />
          <Step title="2. Текст" description="ожидает подготовки материалов" state="idle" />
          <Step title="3. Оценка" description="станет доступна после загрузки" state="idle" />
          <Step title="4. Обзор" description="станет доступен после загрузки" state="idle" />
        </div>
      </Card>
    )
  }

  if (articleQuery.isError || !article) {
    return (
      <Card className="min-h-[640px] space-y-4">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-muted">Ошибка</p>
        <h2 className="text-2xl text-ink">Не удалось загрузить карточку статьи.</h2>
        <p className="max-w-xl text-sm leading-7 text-muted">
          Попробуйте открыть статью ещё раз чуть позже.
        </p>
        <div className="rounded-[20px] border border-line bg-fog/80 p-4 font-mono text-xs text-muted">
          {getErrorMessage(articleQuery.error)}
        </div>
      </Card>
    )
  }

  const pipelineSteps = [
    {
      title: '1. Загрузка',
      description: isDownloading ? 'подготавливаю файлы статьи' : article.localPdfPath || article.localTexPath ? 'материалы готовы' : 'ожидает запуска',
      state: isDownloading ? 'active' : article.localPdfPath || article.localTexPath ? 'done' : 'idle',
    },
    {
      title: '2. Текст',
      description: isParsing || inferredParsing ? 'извлекаю текст статьи' : article.parsedContent ? 'текст готов' : 'ещё не запускался',
      state: isParsing || inferredParsing ? 'active' : article.parsedContent ? 'done' : 'idle',
    },
    {
      title: '3. Оценка',
      description: isEvaluating ? 'готовлю оценку статьи' : evaluation ? 'оценка готова' : 'ещё не запускалась',
      state: isEvaluating ? 'active' : evaluation ? 'done' : 'idle',
    },
    {
      title: '4. Обзор',
      description: isWritingReview ? 'пишу обзор статьи' : review ? 'обзор готов' : 'ещё не запускался',
      state: isWritingReview ? 'active' : review ? 'done' : 'idle',
    },
  ] as const

  return (
    <Card className="space-y-6">
      <div className="space-y-5 border-b border-line pb-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-3xl">
            <p className="font-mono text-xs uppercase tracking-[0.28em] text-muted">Статья</p>
            <h1 className="mt-3 text-4xl leading-tight text-ink md:text-5xl">{article.title}</h1>
            <p className="mt-4 max-w-3xl text-base leading-7 text-muted">{article.abstract}</p>
          </div>
          <div className="min-w-[320px] space-y-3 rounded-[24px] border border-line bg-fog/80 p-5">
            <Badge>{article.arxivId}</Badge>
            <InfoRow label="Дата публикации" value={article.published} />
            <InfoRow label="Авторы" value={article.authors.join(', ')} />
            <div className="flex flex-wrap gap-2">
              {article.tags.length > 0 ? article.tags.map((tag) => <Badge key={tag}>{tag}</Badge>) : <Badge>Без категорий</Badge>}
            </div>
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {pipelineSteps.map((step) => (
            <Step key={step.title} title={step.title} description={step.description} state={step.state} />
          ))}
        </div>

        <div className="rounded-[26px] border border-line bg-fog/70 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.22em] text-muted">Действия</p>
              <p className="mt-2 max-w-2xl text-sm leading-7 text-muted">
                Начните с подготовки текста, затем выберите: нужна быстрая оценка статьи или развёрнутый обзор.
              </p>
            </div>
            <Badge className="bg-white/82 text-ink">Текущая статья: {article.arxivId}</Badge>
          </div>

          <div className="mt-4 grid gap-3 lg:grid-cols-2 2xl:grid-cols-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => articleQuery.refetch()}
              disabled={isDownloading}
              className="w-full justify-center"
            >
              {isDownloading ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}
              Обновить материалы
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => parseMutation.mutate()}
              disabled={isParsing || !articleBackendId}
              className="w-full justify-center"
            >
              {isParsing ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <FileText className="mr-2 h-4 w-4" />}
              Извлечь текст
            </Button>
            <Button
              type="button"
              onClick={() => evaluationMutation.mutate()}
              disabled={isEvaluating || !articleBackendId}
              className="w-full justify-center bg-[#1e2a24] text-paper hover:bg-[#253229]"
            >
              {isEvaluating ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <BrainCircuit className="mr-2 h-4 w-4" />}
              Получить оценку
            </Button>
            <Button
              type="button"
              onClick={() => reviewMutation.mutate()}
              disabled={isWritingReview || !articleBackendId}
              className="w-full justify-center bg-[#7a4a22] text-paper hover:bg-[#8b5528]"
            >
              {isWritingReview ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
              Собрать обзор
            </Button>
          </div>
        </div>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.2fr,0.8fr]">
        <div className="space-y-5">
          <Card className="rounded-[24px] bg-white/65 p-5 shadow-none">
            <div className="flex items-center gap-2">
              <CalendarDays className="h-4 w-4 text-muted" />
              <h2 className="text-xl text-ink">Информация о статье</h2>
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <ArtifactRow label="arXiv ID" value={article.arxivId} icon={<FolderSearch className="h-4 w-4" />} />
              <ArtifactRow label="Дата публикации" value={article.published} icon={<CalendarDays className="h-4 w-4" />} />
              <ArtifactRow label="Авторы" value={article.authors.join(', ')} icon={<FileCode2 className="h-4 w-4" />} />
              <ArtifactRow label="Категории" value={article.tags.length > 0 ? article.tags.join(', ') : 'Не указаны'} icon={<FolderSearch className="h-4 w-4" />} />
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {article.pdfUrl && (
                <a href={article.pdfUrl} target="_blank" rel="noreferrer" download>
                  <Button type="button" variant="outline">
                    <Download className="mr-2 h-4 w-4" />
                    Скачать PDF
                  </Button>
                </a>
              )}
              {article.texUrl && (
                <a href={article.texUrl} target="_blank" rel="noreferrer" download>
                  <Button type="button" variant="outline">
                    <Download className="mr-2 h-4 w-4" />
                    Скачать TeX
                  </Button>
                </a>
              )}
              {article.pdfUrl && (
                <a href={article.pdfUrl} target="_blank" rel="noreferrer">
                  <Button type="button" variant="ghost">
                    <ExternalLink className="mr-2 h-4 w-4" />
                    Открыть PDF
                  </Button>
                </a>
              )}
            </div>
          </Card>

          <Card className="rounded-[24px] bg-white/65 p-5 shadow-none">
            <div className="flex items-center gap-2">
              <ScrollText className="h-4 w-4 text-muted" />
              <h2 className="text-xl text-ink">Распарсенный текст</h2>
            </div>
            {parseMutation.isError && (
              <ErrorBlock message={getErrorMessage(parseMutation.error)} />
            )}
            {article.parsedContent ? (
              <TextBlock value={article.parsedContent} />
            ) : isParsing || inferredParsing ? (
              <LoadingBlock title="Извлекаю текст статьи" description="Подготавливаю текстовую версию статьи для чтения и дальнейшего анализа." />
            ) : (
              <p className="mt-4 text-sm leading-7 text-muted">Текст статьи пока не подготовлен. Нажмите «Извлечь текст», чтобы открыть его здесь.</p>
            )}
          </Card>

          <SummaryPanel
            review={review}
            isGenerating={isWritingReview}
            errorMessage={reviewMutation.isError ? getErrorMessage(reviewMutation.error) : null}
          />

          <EvaluationPanel
            evaluation={evaluation}
            isLoading={evaluationQuery.isLoading}
            isGenerating={isEvaluating}
            errorMessage={evaluationQuery.isError ? getErrorMessage(evaluationQuery.error) : evaluationMutation.isError ? getErrorMessage(evaluationMutation.error) : null}
          />

          <ReviewPanel
            review={review}
            isLoading={reviewQuery.isLoading}
            isGenerating={isWritingReview}
            errorMessage={reviewQuery.isError ? getErrorMessage(reviewQuery.error) : reviewMutation.isError ? getErrorMessage(reviewMutation.error) : null}
          />
        </div>

        <div className="space-y-5">
          <Card className="rounded-[24px] bg-ink p-5 text-paper shadow-none">
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-paper/60">Что можно сделать</p>
            <h2 className="mt-3 text-2xl text-paper">Работайте со статьёй шаг за шагом.</h2>
            <div className="mt-4 space-y-3 text-sm text-paper/75">
              <p>Обновите материалы, если хотите заново подтянуть сведения и файлы по статье.</p>
              <p>Извлеките текст, когда нужно читать статью прямо на странице, а не в отдельном PDF.</p>
              <p>Получите оценку, если нужен быстрый ориентир по качеству и значимости работы.</p>
              <p>Соберите обзор, если нужен полный связный разбор методов, результатов и ограничений.</p>
            </div>
          </Card>

          <Card className="rounded-[24px] bg-white/65 p-5 shadow-none">
            <div className="flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-muted" />
              <h2 className="text-xl text-ink">Действия с текущей статьёй</h2>
            </div>
            <div className="mt-4 space-y-3 text-sm text-muted">
              <p>Если вы уже открывали эту статью раньше, готовые материалы появятся здесь автоматически.</p>
              <p>Если данных пока нет, можно отдельно извлечь текст, получить оценку или собрать обзор.</p>
              <Button type="button" variant="ghost" className="px-0 text-left text-ink" onClick={() => setSelectedArticleId(article.arxivId)}>
                Открыть эту статью заново
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </Card>
  )
}

function EvaluationPanel({
  evaluation,
  isLoading,
  isGenerating,
  errorMessage,
}: {
  evaluation: Evaluation | null
  isLoading: boolean
  isGenerating: boolean
  errorMessage: string | null
}) {
  return (
    <Card className="rounded-[24px] bg-white/65 p-5 shadow-none">
      <div className="flex items-center gap-2">
        <BrainCircuit className="h-4 w-4 text-muted" />
        <h2 className="text-xl text-ink">Оценка статьи</h2>
      </div>

      {evaluation && (
        <>
          <div className="mt-4 grid gap-4 md:grid-cols-4">
            {[
              { label: 'Новизна', value: evaluation.novelty },
              { label: 'Строгость', value: evaluation.rigor },
              { label: 'Влияние', value: evaluation.impact },
              { label: 'Итог', value: evaluation.overall },
            ].map((metric) => (
              <Card key={metric.label} className="rounded-[24px] bg-fog/70 p-4 shadow-none">
                <p className="font-mono text-xs uppercase tracking-[0.22em] text-muted">{metric.label}</p>
                <p className="mt-2 text-3xl text-ink">{metric.value}/5</p>
                <div className="mt-3">
                  <Meter value={metric.value * 20} />
                </div>
              </Card>
            ))}
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <ArtifactRow label="Категория" value={evaluation.category} icon={<BrainCircuit className="h-4 w-4" />} />
            <ArtifactRow label="Актуальность" value={evaluation.relevance} icon={<Sparkles className="h-4 w-4" />} />
          </div>

          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <ListBlock title="Плюсы" items={evaluation.pros} prefix="+ " />
            <ListBlock title="Минусы" items={evaluation.cons} prefix="- " />
          </div>

          <div className="mt-4">
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-muted">Комментарий</p>
            <p className="mt-2 text-sm leading-7 text-muted">{evaluation.reasoning}</p>
          </div>
        </>
      )}

      {!evaluation && (isLoading || isGenerating) && (
        <LoadingBlock title="Готовлю оценку статьи" description="Собираю основные выводы, сильные стороны и возможные ограничения работы." />
      )}

      {!evaluation && !isLoading && !isGenerating && !errorMessage && (
        <p className="mt-4 text-sm leading-7 text-muted">Оценка для статьи ещё не сохранена.</p>
      )}

      {errorMessage && <ErrorBlock message={errorMessage} />}
    </Card>
  )
}

function ReviewPanel({
  review,
  isLoading,
  isGenerating,
  errorMessage,
}: {
  review: Review | null
  isLoading: boolean
  isGenerating: boolean
  errorMessage: string | null
}) {
  return (
    <Card className="rounded-[24px] bg-white/65 p-5 shadow-none">
      <div className="flex items-center gap-2">
        <BookOpen className="h-4 w-4 text-muted" />
        <h2 className="text-xl text-ink">Обзор статьи</h2>
      </div>

      {review && (
        <>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <ArtifactRow label="Разделов" value={String(review.sections.length)} icon={<FileCode2 className="h-4 w-4" />} />
            <ArtifactRow label="Краткий итог" value={review.verdict} icon={<BookOpen className="h-4 w-4" />} />
          </div>

          <div className="prose-copy mt-4 space-y-4 text-sm leading-7 text-ink">
            {review.sections.map((section) => (
              <section key={section.title} className="border-t border-line pt-4 first:border-t-0 first:pt-0">
                <h3 className="text-lg">{section.title}</h3>
                <p className="mt-2 whitespace-pre-wrap text-muted">{section.body || 'Пустой раздел'}</p>
              </section>
            ))}
          </div>

          <div className="mt-4">
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-muted">Полный текст обзора</p>
            <TextBlock value={review.fullText} />
          </div>
        </>
      )}

      {!review && (isLoading || isGenerating) && (
        <LoadingBlock title="Готовлю обзор статьи" description="Собираю ключевые идеи, методы, результаты и ограничения в одном тексте." />
      )}

      {!review && !isLoading && !isGenerating && !errorMessage && (
        <p className="mt-4 text-sm leading-7 text-muted">Обзор для статьи ещё не сохранён.</p>
      )}

      {errorMessage && <ErrorBlock message={errorMessage} />}
    </Card>
  )
}

function SummaryPanel({
  review,
  isGenerating,
  errorMessage,
}: {
  review: Review | null
  isGenerating: boolean
  errorMessage: string | null
}) {
  return (
    <Card className="rounded-[24px] bg-fog/80 p-5 shadow-none">
      <div className="flex items-center gap-2">
        <ScrollText className="h-4 w-4 text-muted" />
        <h2 className="text-xl text-ink">Краткая выжимка</h2>
      </div>

      {review ? (
        <div className="mt-4 space-y-4">
          <div className="rounded-[20px] border border-line bg-white/70 p-4">
            <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted">Кратко</p>
            <p className="mt-2 whitespace-pre-wrap text-sm leading-7 text-ink">{review.summary}</p>
          </div>
          <div className="rounded-[20px] border border-line bg-white/70 p-4">
            <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted">Итог</p>
            <p className="mt-2 whitespace-pre-wrap text-sm leading-7 text-ink">{review.verdict}</p>
          </div>
        </div>
      ) : isGenerating ? (
        <LoadingBlock title="Готовлю краткую выжимку" description="Собираю несколько главных выводов и короткий итог по статье." />
      ) : (
        <div className="mt-4 rounded-[20px] border border-line bg-white/70 p-4 text-sm leading-7 text-muted">
          Здесь появится короткое резюме статьи. Нажмите «Собрать обзор», чтобы заполнить этот блок.
        </div>
      )}

      {errorMessage && <ErrorBlock message={errorMessage} />}

      {review && (
        <p className="mt-4 inline-flex items-center gap-2 text-sm text-muted">
          <ChevronRight className="h-4 w-4" />
          Полный обзор ниже раскрывает методы, результаты, критику и применение.
        </p>
      )}
    </Card>
  )
}

function Step({
  title,
  description,
  state,
}: {
  title: string
  description: string
  state: 'done' | 'active' | 'idle'
}) {
  const tone =
    state === 'done'
      ? 'border-ink bg-ink text-paper'
      : state === 'active'
        ? 'border-ink bg-white text-ink'
        : 'border-line bg-fog/70 text-muted'

  return (
    <div className={`rounded-[22px] border p-4 ${tone}`}>
      <p className="font-mono text-xs uppercase tracking-[0.22em]">{title}</p>
      <p className={`mt-2 text-sm leading-6 ${state === 'done' ? 'text-paper/80' : ''}`}>{description}</p>
      {(state === 'active' || state === 'done') && (
        <ProgressStatus
          active={state === 'active'}
          done={state === 'done'}
          estimateLabel="Обычно занимает около 2 минут."
        />
      )}
    </div>
  )
}

function WorkspaceTile({
  icon,
  title,
  description,
}: {
  icon: ReactNode
  title: string
  description: string
}) {
  return (
    <div className="rounded-[24px] border border-line bg-white/72 p-5 shadow-none">
      <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-fog text-ink">
        {icon}
      </div>
      <h3 className="mt-4 text-lg text-ink">{title}</h3>
      <p className="mt-2 text-sm leading-7 text-muted">{description}</p>
    </div>
  )
}

function PreviewChip({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[20px] border border-line bg-white/78 p-4">
      <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted">{label}</p>
      <p className="mt-2 text-sm leading-6 text-ink">{value}</p>
    </div>
  )
}

function ArtifactRow({ label, value, icon }: { label: string; value: string; icon: ReactNode }) {
  return (
    <div className="rounded-[18px] border border-line bg-fog/70 p-3">
      <div className="flex items-center gap-2 text-ink">
        {icon}
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted">{label}</p>
      </div>
      <p className="mt-2 break-all text-sm text-ink">{value}</p>
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted">{label}</p>
      <p className="mt-1 break-all text-sm text-ink">{value}</p>
    </div>
  )
}

function TextBlock({ value }: { value: string }) {
  return (
    <div className="mt-4 max-h-[420px] overflow-auto rounded-[20px] border border-line bg-fog/70 p-4">
      <pre className="whitespace-pre-wrap break-words font-sans text-sm leading-7 text-ink">{value}</pre>
    </div>
  )
}

function ListBlock({ title, items, prefix }: { title: string; items: string[]; prefix: string }) {
  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-[0.22em] text-muted">{title}</p>
      {items.length > 0 ? (
        <ul className="mt-3 space-y-2 text-sm text-ink">
          {items.map((item) => (
            <li key={item}>
              {prefix}
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-muted">Пусто</p>
      )}
    </div>
  )
}

function LoadingBlock({ title, description }: { title: string; description: string }) {
  return (
    <div className="mt-4 rounded-[20px] border border-line bg-fog/70 p-4">
      <div className="flex items-center gap-2 text-ink">
        <LoaderCircle className="h-4 w-4 animate-spin" />
        <p className="text-sm">{title}</p>
      </div>
      <p className="mt-2 text-sm leading-7 text-muted">{description}</p>
      <ProgressStatus active estimateLabel="Обычно занимает около 2 минут." />
    </div>
  )
}

function ErrorBlock({ message }: { message: string }) {
  return (
    <div className="mt-4 rounded-[20px] border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {message}
    </div>
  )
}

function getErrorMessage(error: unknown) {
  if (isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string' && detail.trim()) {
      return detail
    }
    return error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'Неизвестная ошибка.'
}
