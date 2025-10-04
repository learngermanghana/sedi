alter table orgs enable row level security;
alter table org_members enable row level security;

drop policy if exists p_orgs_select on orgs;
drop policy if exists p_orgs_insert on orgs;
create policy p_orgs_select on orgs for select to authenticated
using (exists (select 1 from org_members m where m.org_id = orgs.id and m.user_id = auth.uid()));
create policy p_orgs_insert on orgs for insert to authenticated with check (true);

drop policy if exists p_members_insert on org_members;
drop policy if exists p_members_select on org_members;
create policy p_members_insert on org_members for insert to authenticated
with check (user_id = auth.uid());
create policy p_members_select on org_members for select to authenticated
using (org_id in (select org_id from org_members where user_id = auth.uid()));
