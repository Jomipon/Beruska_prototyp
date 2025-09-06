create extension if not exists "uuid-ossp";
create table clients (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null,
  name text not null,
  phone text,
  notes text,
  created_at timestamptz not null default now()
);

CREATE TABLE accounts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  owner_id text NOT NULL DEFAULT gen_random_uuid()::text,
  created_at timestamptz NOT NULL DEFAULT now()
);

alter table clients enable row level security;
create policy "owner can read" on clients
  for select using (owner_id = auth.uid());

create policy "owner can write" on clients
  for insert with check (owner_id = auth.uid())
/*  using (owner_id = auth.uid());*/

CREATE OR REPLACE FUNCTION get_account_by_email(p_email text)
RETURNS SETOF accounts
LANGUAGE plpgsql
VOLATILE
AS $$
BEGIN
  RETURN QUERY
  WITH upsert AS (
    INSERT INTO accounts (email)
    VALUES (p_email)
    ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email
    RETURNING *
  )
  SELECT * FROM upsert
  UNION ALL
  SELECT *
  FROM accounts
  WHERE email = p_email
    AND NOT EXISTS (SELECT 1 FROM upsert);
END;
$$;

