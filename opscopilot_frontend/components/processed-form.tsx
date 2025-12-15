// components/processed-form.tsx
"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
  CreateProcessedSchema,
  type Processed,
} from "@/types/processed";
import { apiPost } from "@/lib/api";

// 🔑 Tipos derivados del schema de Zod
// - FormInput: lo que ENTRA al resolver (puede incluir string en amount si tu schema lo permite)
// - FormOutput: lo que SALE del resolver (amount ya normalizado a number|null)
type FormInput = z.input<typeof CreateProcessedSchema>;
type FormOutput = z.output<typeof CreateProcessedSchema>;

type Props = { onCreated?: (row: Processed) => void };

export default function ProcessedForm({ onCreated }: Props) {
  const [submitting, setSubmitting] = useState(false);
  const router = useRouter(); 

  // 👇 Esta es la línea clave que corrige el error del "Resolver"
  const form = useForm<FormInput, any, FormOutput>({
    resolver: zodResolver(CreateProcessedSchema),
    defaultValues: {
      item: "",
      amount: null,
      date_str: "",
      source_file: "",
    } as FormInput,
  });

  const { register, handleSubmit, reset } = form;

  const onSubmit = async (values: FormOutput) => {
    try {
      setSubmitting(true);
      // values.amount YA está en number|null si tu schema hace transform
      const created = await apiPost<Processed, FormOutput>("/processed/", values);
      toast.success("Guardado");
      reset();
      router.refresh();
      onCreated?.(created);
    } catch (err: any) {
  // si usas la ApiError que definimos en lib/api.ts, tiene .status y .payload
  const status = err?.status ?? err?.response?.status;
  const detail = err?.payload || err?.response?.data?.detail || err?.message;

  if (status === 409) {
    // Duplicado: muestra aviso y refresca la tabla porque la fila ya está
    toast.warning("Ese registro ya existe (duplicado).");
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("processed:created"));
    }
    // si usas React Query:
    // qc.invalidateQueries({ queryKey: ["processed-page"] });

    return; // <- no lo trates como error
  }

  toast.error(typeof detail === "string" ? detail : "Error al guardar");

    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <div className="grid gap-2">
        <Label htmlFor="item">Concepto</Label>
        <Input id="item" placeholder="Texto libre" {...register("item")} />
      </div>
      
      <div className="grid gap-2">
        <Label htmlFor="amount">Importe</Label>
        {/* Si tu schema acepta string|number con transform, NO necesitas setValueAs */}
        <Input id="amount" placeholder="123.45" {...register("amount")} />
        {/*
          Alternativa si tu schema es SOLO number:
          <Input
            id="amount"
            type="number"
            step="any"
            {...register("amount", {
              setValueAs: (v) =>
                v === "" || v === null || v === undefined ? null : Number(v),
            })}
          />
        */}
      </div>

      <div className="grid gap-2">
        <Label htmlFor="date_str">Fecha</Label>
        <Input id="date_str" placeholder="2025-10-12" {...register("date_str")} />
      </div>

      <div className="grid gap-2">
        <Label htmlFor="source_file">Origen</Label>
        <Input id="source_file" placeholder="sample.csv" {...register("source_file")} />
      </div>

      <Button type="submit" disabled={submitting}>
        {submitting ? "Guardando…" : "Guardar"}
      </Button>
    </form>
  );
}
