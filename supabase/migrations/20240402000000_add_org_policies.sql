-- Ensure the policy for inserting new organizations exists
DROP POLICY IF EXISTS "p_orgs_insert" ON public.orgs;
CREATE POLICY "p_orgs_insert" ON public.orgs
  FOR INSERT
  TO authenticated
  WITH CHECK (
    (id = auth.uid())
    OR (owner_id = auth.uid())
  );

-- Ensure members can only insert themselves into organizations
DROP POLICY IF EXISTS "Insert org_members self" ON public.org_members;
CREATE POLICY "Insert org_members self" ON public.org_members
  FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());
