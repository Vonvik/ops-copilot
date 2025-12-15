"use client";

import { useQuery, keepPreviousData } from "@tanstack/react-query";

export type ProcessedRow = {
  id: number;
  item: string | null;
  amount: number | null;
  date_str: string | null;
  source_file: string | null;
  created_at: string;
};

export type ProcessedPage = {
  items: ProcessedRow[];
  total: number;
  page: number;
  page_size: number;
  sort_by?: string | null;
  sort_dir?: "asc" | "desc" | null;
};

async function fetchPage(
  page: number,
  pageSize: number,
  sortBy?: string,
  sortDir?: "asc" | "desc"
): Promise<ProcessedPage> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  if (sortBy) params.set("sort_by", sortBy);
  if (sortDir) params.set("sort_dir", sortDir);

  // NEXT_PUBLIC_API_URL ya apunta a /api/v1
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/processed/page?${params.toString()}`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error(`GET /processed/page ${res.status}`);
  return res.json();
}

export function useProcessedPage(
  page: number,
  pageSize: number,
  sortBy?: string,
  sortDir?: "asc" | "desc"
) {
  return useQuery({
    queryKey: ["processed-page", page, pageSize, sortBy, sortDir],
    queryFn: () => fetchPage(page, pageSize, sortBy, sortDir),
    // v5: reemplaza keepPreviousData por:
    placeholderData: keepPreviousData,
  });
}
