-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    clerk_user_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create RLS policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy for selecting users
CREATE POLICY select_users ON users
    FOR SELECT
    USING (
        -- Allow users to see their own data
        clerk_user_id = current_user
        -- Add additional conditions for admin users if needed
    );

-- Policy for inserting users
CREATE POLICY insert_users ON users
    FOR INSERT
    WITH CHECK (
        -- Only allow users to insert their own data
        clerk_user_id = current_user
    );

-- Policy for updating users
CREATE POLICY update_users ON users
    FOR UPDATE
    USING (
        -- Only allow users to update their own data
        clerk_user_id = current_user
    )
    WITH CHECK (
        -- Ensure they can't change the clerk_user_id
        clerk_user_id = current_user
    );

-- Policy for deleting users
CREATE POLICY delete_users ON users
    FOR DELETE
    USING (
        -- Only allow users to delete their own data
        clerk_user_id = current_user
    );

-- Create function to get requesting user ID from JWT
CREATE OR REPLACE FUNCTION requesting_user_id()
RETURNS text
LANGUAGE sql STABLE
AS $$
  SELECT nullif(current_setting('request.jwt.claims', true)::json->>'sub', '')::text;
$$;
