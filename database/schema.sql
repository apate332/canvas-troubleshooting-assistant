CREATE TABLE courses (
    course_id BIGINT PRIMARY KEY,
    course_name VARCHAR(255)
);

CREATE TABLE assignments (
    assignment_id BIGINT PRIMARY KEY,
    course_id BIGINT REFERENCES courses(course_id),
    name VARCHAR(255) NOT NULL,
    published BOOLEAN,
    due_at TIMESTAMPTZ,
    unlock_at TIMESTAMPTZ,
    lock_at TIMESTAMPTZ,
    submission_types JSONB
);

-- Stores each troubleshooting session
CREATE TABLE troubleshooting_runs (
    run_id SERIAL PRIMARY KEY,
    assignment_id BIGINT REFERENCES assingments(assignment_id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE troubleshooting_reports (
    report_id SERIAL PRIMARY KEY,
    assignment_id BIGINT REFERENCES assignments(assignment_id),
    issue TEXT NOT NULL,
    severity VARCHAR(50),
    recommendation TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);