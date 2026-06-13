import { create } from "zustand";
import { persist } from "zustand/middleware";

export type BriefFilters = {
  severity: string;
  status: string;
  clientId: string;
};

type AppState = {
  activeClientId: string | null;
  briefFilters: BriefFilters;
  setActiveClientId: (clientId: string | null) => void;
  setBriefFilters: (filters: Partial<BriefFilters>) => void;
  resetBriefFilters: () => void;
};

const DEFAULT_BRIEF_FILTERS: BriefFilters = {
  severity: "",
  status: "",
  clientId: "",
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      activeClientId: null,
      briefFilters: DEFAULT_BRIEF_FILTERS,
      setActiveClientId: (clientId) => set({ activeClientId: clientId }),
      setBriefFilters: (filters) =>
        set((state) => ({ briefFilters: { ...state.briefFilters, ...filters } })),
      resetBriefFilters: () => set({ briefFilters: DEFAULT_BRIEF_FILTERS }),
    }),
    {
      name: "regintel-app",
      partialize: (state) => ({
        activeClientId: state.activeClientId,
        briefFilters: state.briefFilters,
      }),
    },
  ),
);
