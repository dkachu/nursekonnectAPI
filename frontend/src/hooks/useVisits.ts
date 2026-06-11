import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { visitService } from "@/services/visit.service";
import type { VisitNote, VisitNotePayload } from "@/types";

export function useVisitNotes() {
  return useQuery({ queryKey: ["visit-notes"], queryFn: () => visitService.getVisitNotes() });
}

export function useVisitNote(noteId: number | null) {
  return useQuery({
    queryKey: ["visit-notes", noteId],
    queryFn: () => visitService.getVisitNote(Number(noteId)),
    enabled: noteId !== null,
  });
}

export function useCreateVisitNote() {
  const queryClient = useQueryClient();
  return useMutation<VisitNote, Error, VisitNotePayload>({
    mutationFn: (payload) => visitService.createVisitNote(payload),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["visit-notes"] }),
  });
}

export function useUpdateVisitNote() {
  const queryClient = useQueryClient();
  return useMutation<VisitNote, Error, { noteId: number; payload: Partial<VisitNotePayload> }>({
    mutationFn: ({ noteId, payload }) => visitService.updateVisitNote(noteId, payload),
    onSuccess: (note) => {
      void queryClient.invalidateQueries({ queryKey: ["visit-notes"] });
      void queryClient.invalidateQueries({ queryKey: ["visit-notes", note.id] });
    },
  });
}
