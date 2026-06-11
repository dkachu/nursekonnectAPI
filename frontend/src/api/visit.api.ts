import { apiClient } from "@/api/client";
import type { VisitNote, VisitNotePayload } from "@/types";

export const visitApi = {
  async listVisitNotes(): Promise<VisitNote[]> {
    const response = await apiClient.get<VisitNote[]>("/api/visit-notes/");
    return response.data;
  },
  async createVisitNote(payload: VisitNotePayload): Promise<VisitNote> {
    const response = await apiClient.post<VisitNote>("/api/visit-notes/", payload);
    return response.data;
  },
  async getVisitNote(noteId: number): Promise<VisitNote> {
    const response = await apiClient.get<VisitNote>(`/api/visit-notes/${noteId}/`);
    return response.data;
  },
  async updateVisitNote(noteId: number, payload: Partial<VisitNotePayload>): Promise<VisitNote> {
    const response = await apiClient.patch<VisitNote>(`/api/visit-notes/${noteId}/`, payload);
    return response.data;
  },
};
