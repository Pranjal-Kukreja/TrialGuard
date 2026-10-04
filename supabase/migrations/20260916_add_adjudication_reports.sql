ALTER TABLE public.patients
ADD COLUMN IF NOT EXISTS adjudication_reports jsonb NOT NULL DEFAULT '[]'::jsonb;

COMMENT ON COLUMN public.patients.adjudication_reports IS
  'Append-only JSON array of finalized human adjudication reports.';
