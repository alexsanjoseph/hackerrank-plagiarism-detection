CREATE TABLE submissions_code (
    username TEXT NOT NULL,
    link TEXT NOT NULL,
    challenge TEXT NOT NULL,
    code TEXT,
    score NUMERIC
 );

CREATE UNIQUE INDEX main_idx on submissions(username, challenge);