create table if not exists intake_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  status text check (status in ('new','collecting','complete','error')) default 'collecting',
  idea_schema jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists intake_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references intake_sessions (id) on delete cascade,
  role text check (role in ('user','agent','system')),
  content text,
  payload jsonb,
  created_at timestamptz default now()
);

create table if not exists intake_artifacts (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references intake_sessions (id) on delete cascade,
  type text check (type in ('audio','pdf','docx','image','other')),
  storage_path text,
  text_extracted text,
  meta jsonb,
  created_at timestamptz default now()
);
