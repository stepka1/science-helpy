import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { http } from '../../../shared/api/http'
import type { ArticleDetail, ArticleSummary, Evaluation, Review, ReviewSection } from '../../../shared/types/article'

type BackendArticle = {
  id: string
  arxiv_id: string
  title: string
  authors: string[]
  abstract: string
  published_date: string | null
  categories: string[]
  pdf_url?: string | null
  tex_url?: string | null
  local_pdf_path?: string | null
  local_tex_path?: string | null
  parsed_content?: string | null
}

type BackendEvaluation = {
  id: string
  article_id: string
  category: string
  novelty_score: number
  methodology_score: number
  impact_score: number
  overall_score: number
  pros: string[]
  cons: string[]
  justification: string
  relevance: string
}

type BackendReview = {
  id: string
  article_id: string
  summary: string
  methods: string
  results: string
  criticism: string
  application: string
  verdict: string
  full_text: string
}

type BackendParseArticle = {
  article_id: string
  parsed_content: string
}

function mapArticle(article: BackendArticle): ArticleDetail {
  return {
    id: article.id,
    arxivId: article.arxiv_id,
    title: article.title,
    authors: article.authors,
    published: article.published_date ? new Date(article.published_date).toLocaleDateString('ru-RU') : 'Дата не указана',
    publishedDate: article.published_date ?? undefined,
    abstract: article.abstract,
    tags: article.categories,
    pdfUrl: article.pdf_url ?? undefined,
    texUrl: article.tex_url ?? undefined,
    localPdfPath: article.local_pdf_path ?? undefined,
    localTexPath: article.local_tex_path ?? undefined,
    parsedContent: article.parsed_content ?? undefined,
  }
}

function mapEvaluation(evaluation: BackendEvaluation): Evaluation {
  return {
    id: evaluation.id,
    articleId: evaluation.article_id,
    category: evaluation.category,
    relevance: evaluation.relevance,
    novelty: evaluation.novelty_score,
    rigor: evaluation.methodology_score,
    impact: evaluation.impact_score,
    overall: evaluation.overall_score,
    pros: evaluation.pros,
    cons: evaluation.cons,
    reasoning: evaluation.justification,
  }
}

function mapReviewSections(review: BackendReview): ReviewSection[] {
  return [
    { title: 'Резюме', body: review.summary },
    { title: 'Методы', body: review.methods },
    { title: 'Результаты', body: review.results },
    { title: 'Критика', body: review.criticism },
    { title: 'Применение', body: review.application },
    { title: 'Вердикт', body: review.verdict },
  ]
}

function mapReview(review: BackendReview): Review {
  return {
    id: review.id,
    articleId: review.article_id,
    summary: review.summary,
    methods: review.methods,
    results: review.results,
    criticism: review.criticism,
    application: review.application,
    verdict: review.verdict,
    fullText: review.full_text,
    sections: mapReviewSections(review),
  }
}

function mapArticleSummary(article: BackendArticle): ArticleSummary {
  return {
    id: article.arxiv_id,
    arxivId: article.arxiv_id,
    title: article.title,
    authors: article.authors,
    published: article.published_date ? new Date(article.published_date).toLocaleDateString('ru-RU') : 'Дата не указана',
    abstract: article.abstract,
    tags: article.categories,
  }
}

export function useArticles(query: string) {
  return useQuery({
    queryKey: ['articles', query],
    queryFn: async ({ signal }) => {
      if (!query.trim()) {
        return []
      }

      const { data } = await http.post<BackendArticle[]>('/articles/search', {
        query,
        max_results: 10,
      }, {
        signal,
      })

      return data.map(mapArticleSummary)
    },
    enabled: Boolean(query.trim()),
  })
}

export function useArticleDetail(articleId: string) {
  return useQuery({
    queryKey: ['article', articleId],
    queryFn: async () => {
      const { data } = await http.post<BackendArticle>('/articles/download', {
        arxiv_id: articleId,
      })
      return mapArticle(data)
    },
    enabled: Boolean(articleId),
    staleTime: 5 * 60 * 1000,
  })
}

export function useArticleParse(articleId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationKey: ['article', articleId, 'parse'],
    mutationFn: async () => {
      const { data } = await http.post<BackendParseArticle>(`/articles/${articleId}/parse`)
      return data
    },
    onSuccess: (data) => {
      queryClient.setQueryData<ArticleDetail | undefined>(['article', articleId], (current) =>
        current ? { ...current, parsedContent: data.parsed_content } : current,
      )
    },
  })
}

export function useArticleEvaluation(articleId: string) {
  return useQuery({
    queryKey: ['article', articleId, 'evaluation'],
    queryFn: async () => {
      try {
        const { data } = await http.get<BackendEvaluation>(`/evaluations/article/${articleId}`)
        return mapEvaluation(data)
      } catch (error) {
        if (typeof error === 'object' && error && 'response' in error) {
          const response = (error as { response?: { status?: number } }).response
          if (response?.status === 404) {
            return null
          }
        }
        throw error
      }
    },
    enabled: Boolean(articleId),
    retry: false,
  })
}

export function useGenerateArticleEvaluation(articleId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationKey: ['article', articleId, 'evaluation'],
    mutationFn: async () => {
      const { data } = await http.post<BackendEvaluation>('/evaluations/evaluate', {
        article_id: articleId,
      })
      return mapEvaluation(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', articleId, 'evaluation'] })
      queryClient.invalidateQueries({ queryKey: ['article', articleId] })
    },
  })
}

export function useArticleReview(articleId: string) {
  return useQuery({
    queryKey: ['article', articleId, 'review'],
    queryFn: async () => {
      try {
        const { data } = await http.get<BackendReview>(`/reviews/article/${articleId}`)
        return mapReview(data)
      } catch (error) {
        if (typeof error === 'object' && error && 'response' in error) {
          const response = (error as { response?: { status?: number } }).response
          if (response?.status === 404) {
            return null
          }
        }
        throw error
      }
    },
    enabled: Boolean(articleId),
    retry: false,
  })
}

export function useGenerateArticleReview(articleId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationKey: ['article', articleId, 'review'],
    mutationFn: async () => {
      const { data } = await http.post<BackendReview>('/reviews/write', {
        article_id: articleId,
      })
      return mapReview(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', articleId, 'review'] })
      queryClient.invalidateQueries({ queryKey: ['article', articleId] })
    },
  })
}
