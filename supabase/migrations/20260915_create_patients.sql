create table if not exists public.patients (
  patient_id text not null,
  trial_id text null,
  name text null,
  dob date null,
  age integer null,
  sex text null,
  cohort text null,
  diagnosis text null,
  fhir_id text null,
  assigned_demo_trial_id text null,
  demo_category text null,
  clinical_data jsonb null,
  created_at timestamp with time zone null default now(),
  updated_at timestamp with time zone null default now(),
  constraint patients_pkey primary key (patient_id)
);
