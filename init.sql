-- Update the insert policy
CREATE
OR REPLACE POLICY insert_users ON users FOR INSERT
WITH
    CHECK (auth.uid () = clerk_user_id);

-- Update the select policy
CREATE
OR REPLACE POLICY select_users ON users FOR
SELECT
    USING (
        auth.uid () = clerk_user_id
        OR auth.role () = 'authenticated'
    );

-- Update the update policy
CREATE
OR REPLACE POLICY update_users ON users FOR
UPDATE USING (auth.uid () = clerk_user_id)
WITH
    CHECK (auth.uid () = clerk_user_id);

-- Update the delete policy
CREATE
OR REPLACE POLICY delete_users ON users FOR DELETE USING (auth.uid () = clerk_user_id);
