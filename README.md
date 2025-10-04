# a1a2vocab

## Supabase migrations

The project uses Supabase row level security policies to control who can create
organizations and organization memberships. Before launching the application in
any environment, make sure the policies in `supabase/migrations/` are applied to
the target database.

1. Install the Supabase CLI if you do not already have it: follow the
   instructions at <https://supabase.com/docs/reference/cli/start>.
2. Set the `project_id` in `supabase/config.toml` to the Supabase project ref
   for the environment you want to update.
3. Authenticate with Supabase and link the project:

   ```sh
   supabase login
   supabase link --project-ref "$SUPABASE_PROJECT_REF"
   ```

4. Run the migrations (this will apply the policies defined in
   `supabase/migrations/`):

   ```sh
   supabase db push
   ```

   If you prefer to target a specific database branch or the local development
   database, pass the appropriate flags from the Supabase CLI documentation.

Running `supabase db push` as part of your deployment or environment bootstrap
ensures that the `p_orgs_insert` policy and the `org_members` insert policy are
present before the application starts.
