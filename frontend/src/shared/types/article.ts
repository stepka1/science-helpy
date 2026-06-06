export type ArticleSummary = {
  id: string
  arxivId: string
  title: string
  authors: string[]
  published: string
  abstract: string
  tags: string[]
}

export type Evaluation = {
  id: string
  articleId: string
  category: string
  relevance: string
  novelty: number
  rigor: number
  impact: number
  overall: number
  pros: string[]
  cons: string[]
  reasoning: string
}

export type ReviewSection = {
  title: string
  body: string
}

export type Review = {
  id: string
  articleId: string
  summary: string
  methods: string
  results: string
  criticism: string
  application: string
  verdict: string
  fullText: string
  sections: ReviewSection[]
}

export type ArticleDetail = ArticleSummary & {
  publishedDate?: string
  pdfUrl?: string
  texUrl?: string
  localPdfPath?: string
  localTexPath?: string
  parsedContent?: string
}
