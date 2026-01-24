import { create } from 'zustand';
import { orchestrationService, OrchestrationStatus } from '../services/orchestration';

interface OrchestrationState {
  status: OrchestrationStatus | null;
  isLoading: boolean;
  error: string | null;
  fetchStatus: () => Promise<void>;
  start: () => Promise<void>;
  stop: () => Promise<void>;
  pause: () => Promise<void>;
  resume: () => Promise<void>;
}

export const useOrchestrationStore = create<OrchestrationState>((set) => ({
  status: null,
  isLoading: false,
  error: null,

  fetchStatus: async () => {
    set({ isLoading: true, error: null });
    try {
      const status = await orchestrationService.getStatus();
      set({ status, isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch status',
        isLoading: false,
      });
    }
  },

  start: async () => {
    set({ isLoading: true, error: null });
    try {
      await orchestrationService.start();
      await orchestrationService.getStatus().then((status) => set({ status }));
      set({ isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to start',
        isLoading: false,
      });
    }
  },

  stop: async () => {
    set({ isLoading: true, error: null });
    try {
      await orchestrationService.stop();
      await orchestrationService.getStatus().then((status) => set({ status }));
      set({ isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to stop',
        isLoading: false,
      });
    }
  },

  pause: async () => {
    set({ isLoading: true, error: null });
    try {
      await orchestrationService.pause();
      await orchestrationService.getStatus().then((status) => set({ status }));
      set({ isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to pause',
        isLoading: false,
      });
    }
  },

  resume: async () => {
    set({ isLoading: true, error: null });
    try {
      await orchestrationService.resume();
      await orchestrationService.getStatus().then((status) => set({ status }));
      set({ isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to resume',
        isLoading: false,
      });
    }
  },
}));
