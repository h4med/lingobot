CREATE TYPE user_status_enum AS ENUM (
    'ena',
    'dis',
    'zer'
);

CREATE TYPE user_role_enum AS ENUM (
    'user',
    'admin'
);

CREATE TYPE sent_by_enum AS ENUM (
    'user',
    'bot'
);


CREATE TABLE lingo_users (
    user_id bigint PRIMARY KEY NOT NULL,
	first_name character varying(255) NOT NULL,
    last_name character varying(255),
    username character varying(255),
    credit integer DEFAULT 50000,
    joined_at timestamp without time zone,
    last_interaction  timestamp without time zone,
    status user_status_enum DEFAULT 'ena'::user_status_enum NOT NULL,
    level smallint DEFAULT 2 NOT NULL,
    role user_role_enum DEFAULT 'user'::user_role_enum NOT NULL,
    model character varying DEFAULT 'GPT-3.5'::character varying,
    is_bot boolean DEFAULT false NOT NULL,
    feature_1_enabled boolean DEFAULT false NOT NULL,
    feature_2_enabled boolean DEFAULT false NOT NULL,
    feature_3_enabled boolean DEFAULT false NOT NULL,
    feature_4_enabled boolean DEFAULT false NOT NULL,
    feature_5_enabled boolean DEFAULT false NOT NULL,
    request_count integer DEFAULT 0
);


CREATE TABLE lingo_conversations (
    id SERIAL PRIMARY KEY NOT NULL,
    user_id bigint REFERENCES lingo_users(user_id),
    message TEXT,
    sent_by sent_by_enum,
    timestamp TIMESTAMP
);

CREATE INDEX idx_timestamp ON lingo_conversations (timestamp);
CREATE INDEX idx_user_id ON lingo_conversations (user_id);

CREATE TABLE lingo_user_logs (
    id bigint PRIMARY KEY NOT NULL,
    user_id bigint  REFERENCES lingo_users(user_id),
    activity_type character varying NOT NULL,
    tokens integer,
    duration integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);