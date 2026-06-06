import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type SelectedArticleState = {
  selectedArticleId: string
  searchTerm: string
  setSelectedArticleId: (articleId: string) => void
  setSearchTerm: (value: string) => void
}

export const useSelectedArticle = create<SelectedArticleState>()(
  persist(
    (set) => ({
      selectedArticleId: '',
      searchTerm: '',
      setSelectedArticleId: (selectedArticleId) => set({ selectedArticleId }),
      setSearchTerm: (searchTerm) => set({ searchTerm }),
    }),
    {
      name: 'science-helpy-page-state',
      version: 2,
      migrate: (persistedState) => {
        const state = persistedState as Partial<SelectedArticleState> | undefined

        return {
          selectedArticleId: state?.selectedArticleId ?? '',
          searchTerm: '',
        }
      },
      partialize: (state) => ({
        selectedArticleId: state.selectedArticleId,
      }),
    },
  ),
)
