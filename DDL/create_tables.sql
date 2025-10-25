delete table public.company;
drop table if exists public.company;

DROP POLICY IF EXISTS "read own rows" ON company;
DROP POLICY IF EXISTS "insert as self" ON company;
DROP POLICY IF EXISTS "update own rows" ON company;
DROP POLICY IF EXISTS "delete own rows" ON company;

create table public.company
 (
  company_id text not null default gen_random_uuid (),
  owner_id SET DEFAULT get_owner_id((auth.uid())::text),
  name text not null,
  name_first text not null,
  name_last text not null,
  active boolean not null default true,
  note text not null,
  type_person int null default 0,
  created_at timestamp with time zone not null default now(),
  type_person int null default 0;
  address text null;
  type_relationship int not null default 0;
  email text null;
  phone_number text null;
  alias text null;
  foundation_id text null;
  ico text null;
  constraint company_pkey primary key (company_id)
) TABLESPACE pg_default;

-- zapnutí RLS - každý vidí svoje řádky
ALTER TABLE company ENABLE ROW LEVEL SECURITY;

create policy "read own rows"
on company for select
to authenticated
using (owner_id = get_owner_id ());

-- INSERT: smí vložit jen jako sám sebe
create policy "insert as self"
on company for insert
to authenticated
with check (owner_id = get_owner_id ());

-- UPDATE: může měnit jen své řádky
create policy "update own rows"
on company for update
to authenticated
using (owner_id = get_owner_id ())
with check (owner_id = get_owner_id ());

-- DELETE: může mazat jen své řádky (pokud chceš)
create policy "delete own rows"
on company for delete
to authenticated
using (owner_id = get_owner_id ());


CREATE TABLE accounts (
  account_id text PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_id text UNIQUE NOT NULL,
  owner_id text NOT NULL,
  email text NOT NULL,
  is_active boolean DEFAULT true, 
  created_at timestamp NOT NULL DEFAULT now()
);

create table public.quote
(
  quote_id text not null default gen_random_uuid (),
  quote_text text not null,
  quote_author text not null,
  created_at timestamp with time zone not null default now(),
  constraint quote_pkey primary key (quote_id)
) TABLESPACE pg_default;

create table public.settings
 (
  settings_id text not null default gen_random_uuid (),
  owner_id text DEFAULT get_owner_id(),
  weather_enable boolean not null default false,
  weather_place text null,
  quote_enable boolean not null default false,
  constraint settings_pkey primary key (settings_id)
) TABLESPACE pg_default;

ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

create policy "read own rows"
on settings for select
to authenticated
using (owner_id = get_owner_id ());

-- INSERT: smí vložit jen jako sám sebe
create policy "insert as self"
on settings for insert
to authenticated
with check (owner_id = get_owner_id ());

-- UPDATE: může měnit jen své řádky
create policy "update own rows"
on settings for update
to authenticated
using (owner_id = get_owner_id ())
with check (owner_id = get_owner_id ());

-- DELETE: může mazat jen své řádky (pokud chceš)
create policy "delete own rows"
on settings for delete
to authenticated
using (owner_id = get_owner_id ());