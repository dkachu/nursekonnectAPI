import { useMemo, useState } from "react";

interface PaginationState<T> {
  page: number;
  pageSize: number;
  totalPages: number;
  items: T[];
  setPage: (page: number) => void;
}

export function usePagination<T>(items: T[], pageSize = 10): PaginationState<T> {
  const [page, setPage] = useState(1);
  const totalPages = Math.max(1, Math.ceil(items.length / pageSize));
  const paginatedItems = useMemo(() => {
    const start = (page - 1) * pageSize;
    return items.slice(start, start + pageSize);
  }, [items, page, pageSize]);

  return { page, pageSize, totalPages, items: paginatedItems, setPage };
}
