-- Tabulka s „vlastníkem“ řádku (každý uvidí jen své)
create table if not exists items (
  id uuid primary key default gen_random_uuid(),
  owner_id text not null default auth.uid()::text,
  content text not null,
  created_at timestamptz not null default now()
);

alter table items enable row level security;
