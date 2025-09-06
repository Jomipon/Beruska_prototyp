-- SELECT: uživatel vidí jen své řádky
create policy if not exists "read own rows"
on items for select
to authenticated
using (owner_id = auth.uid()::text);

-- INSERT: smí vložit jen jako sám sebe
create policy if not exists "insert as self"
on items for insert
to authenticated
with check (owner_id = auth.uid()::text);

-- UPDATE: může měnit jen své řádky
create policy if not exists "update own rows"
on items for update
to authenticated
using (owner_id = auth.uid()::text)
with check (owner_id = auth.uid()::text);

-- DELETE: může mazat jen své řádky (pokud chceš)
create policy if not exists "delete own rows"
on items for delete
to authenticated
using (owner_id = auth.uid()::text);
