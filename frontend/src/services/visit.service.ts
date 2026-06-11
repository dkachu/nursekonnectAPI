import { visitApi } from "@/api/visit.api";
import type { VisitNote, VisitNotePayload } from "@/types";

export class VisitService {
  getVisitNotes(): Promise<VisitNote[]> {
    return visitApi.listVisitNotes();
  }

  createVisitNote(payload: VisitNotePayload): Promise<VisitNote> {
    return visitApi.createVisitNote(payload);
  }

  getVisitNote(noteId: number): Promise<VisitNote> {
    return visitApi.getVisitNote(noteId);
  }

  updateVisitNote(noteId: number, payload: Partial<VisitNotePayload>): Promise<VisitNote> {
    return visitApi.updateVisitNote(noteId, payload);
  }
}

export const visitService = new VisitService();
