"use client";

import * as React from "react";
import { FormProvider, type UseFormReturn } from "react-hook-form";

export function Form({ children, ...methods }: UseFormReturn & { children: React.ReactNode }) {
  return <FormProvider {...methods}>{children}</FormProvider>;
}
