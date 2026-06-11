import { useEffect, useRef, useState } from "react";

export function useInfiniteScroll(canLoadMore: boolean): {
  sentinelRef: React.RefObject<HTMLDivElement | null>;
  shouldLoadMore: boolean;
  reset: () => void;
} {
  const sentinelRef = useRef<HTMLDivElement | null>(null);
  const [shouldLoadMore, setShouldLoadMore] = useState(false);

  useEffect(() => {
    const element = sentinelRef.current;
    if (!element || !canLoadMore) {
      return;
    }

    const observer = new IntersectionObserver(([entry]) => {
      if (entry?.isIntersecting) {
        setShouldLoadMore(true);
      }
    });

    observer.observe(element);
    return () => observer.disconnect();
  }, [canLoadMore]);

  return { sentinelRef, shouldLoadMore, reset: () => setShouldLoadMore(false) };
}
