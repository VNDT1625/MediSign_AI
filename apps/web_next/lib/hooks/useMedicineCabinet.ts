"use client";

/**
 * `lib/hooks/useMedicineCabinet.ts`
 *
 * Custom hook for managing the local medicine cabinet.
 * Persists to `localStorage["medisign:cabinet"]` as an array of
 * `MedicineScanResponse`. Provides optimistic add/remove with
 * deduplication by `normalized_name`.
 *
 * Phase 2: will sync to backend `UserMedicine` CRUD endpoint.
 *
 * @see Requirements 2.3.2
 */

import { useState, useEffect, useCallback } from "react";
import type { MedicineScanResponse } from "@medisign/shared-contracts";

const STORAGE_KEY = "medisign:cabinet";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function readFromStorage(): MedicineScanResponse[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed as MedicineScanResponse[];
  } catch {
    return [];
  }
}

function writeToStorage(items: MedicineScanResponse[]): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch {
    // Storage quota exceeded or private browsing — silently ignore.
  }
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export interface UseMedicineCabinetReturn {
  /** Current cabinet items. */
  items: MedicineScanResponse[];
  /**
   * Optimistically add an item. Deduplicates by `normalized_name`
   * (case-insensitive). If the item already exists it is replaced with
   * the newer scan result.
   */
  add: (item: MedicineScanResponse) => void;
  /**
   * Optimistically remove an item by its `normalized_name`
   * (case-insensitive match).
   */
  remove: (normalizedName: string) => void;
}

export function useMedicineCabinet(): UseMedicineCabinetReturn {
  const [items, setItems] = useState<MedicineScanResponse[]>(() =>
    readFromStorage()
  );

  // Keep state in sync if another tab modifies localStorage.
  useEffect(() => {
    function handleStorage(e: StorageEvent) {
      if (e.key === STORAGE_KEY) {
        setItems(readFromStorage());
      }
    }
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);

  const add = useCallback((item: MedicineScanResponse) => {
    setItems((prev) => {
      const key = item.normalized_name.toLowerCase();
      // Replace existing entry or append new one.
      const filtered = prev.filter(
        (i) => i.normalized_name.toLowerCase() !== key
      );
      const next = [...filtered, item];
      writeToStorage(next);
      return next;
    });
  }, []);

  const remove = useCallback((normalizedName: string) => {
    setItems((prev) => {
      const key = normalizedName.toLowerCase();
      const next = prev.filter(
        (i) => i.normalized_name.toLowerCase() !== key
      );
      writeToStorage(next);
      return next;
    });
  }, []);

  return { items, add, remove };
}
