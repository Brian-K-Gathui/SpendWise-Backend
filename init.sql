----FOR SUPABASE---------

-- Create a function to check the incoming user ID
CREATE OR REPLACE FUNCTION requesting_user_id()
RETURNS text
LANGUAGE sql
AS $$
SELECT NULLIF(
    current_setting('request.jwt.claims', true)::json->>'sub',
    ''
)::text;
$$;

-- Drop the existing table if needed
DROP TABLE IF EXISTS public.user_data;

-- Create the user_data table with the correct structure
CREATE TABLE IF NOT EXISTS public.user_data (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id TEXT NOT NULL DEFAULT requesting_user_id(),
  data JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on the table
ALTER TABLE public.user_data ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Policy for SELECT operations
CREATE POLICY "Users can view their own data"
ON public.user_data
FOR SELECT
TO authenticated
USING (requesting_user_id() = user_id);

-- Policy for INSERT operations
CREATE POLICY "Users can insert their own data"
ON public.user_data
FOR INSERT
TO authenticated
WITH CHECK (requesting_user_id() = user_id);

-- Policy for UPDATE operations
CREATE POLICY "Users can update their own data"
ON public.user_data
FOR UPDATE
TO authenticated
USING (requesting_user_id() = user_id);

-- Policy for DELETE operations
CREATE POLICY "Users can delete their own data"
ON public.user_data
FOR DELETE
TO authenticated
USING (requesting_user_id() = user_id);
