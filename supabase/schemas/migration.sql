create table public.user (
  inserted_at timestamp with time zone not null default now(),
  name text not null,
  email text not null,
  password text not null,
  id uuid not null,
  constraint user_pkey primary key (id),
  constraint user_email_key unique (email)
) TABLESPACE pg_default;

create table public.team (
  id uuid not null default gen_random_uuid (),
  inserted_at timestamp with time zone null default now(),
  name text not null,
  owner_user_id uuid not null,
  constraint team_pkey primary key (id),
  constraint fk_user_id foreign KEY (owner_user_id) references "user" (id) on delete CASCADE
) TABLESPACE pg_default;

create table public.schema (
  id uuid not null default gen_random_uuid (),
  inserted_at timestamp with time zone null default now(),
  title text not null,
  database_model character varying null,
  display_picture text null,
  updated_at timestamp with time zone null,
  constraint schema_pkey primary key (id)
) TABLESPACE pg_default;

create table public.user_schema (
  id uuid not null default gen_random_uuid (),
  user_id uuid not null,
  schema_id uuid not null,
  constraint user_schema_pkey primary key (id),
  constraint fk_user_schema_schema foreign KEY (schema_id) references schema (id) on delete CASCADE,
  constraint fk_user_schema_user foreign KEY (user_id) references "user" (id) on delete CASCADE
) TABLESPACE pg_default;

create index IF not exists idx_user_schema_user_id on public.user_schema using btree (user_id) TABLESPACE pg_default;

create index IF not exists idx_user_schema_schema_id on public.user_schema using btree (schema_id) TABLESPACE pg_default;

create table public.user_team (
  id uuid not null default gen_random_uuid (),
  user_id uuid not null,
  team_id uuid not null,
  constraint user_team_pkey primary key (id),
  constraint fk_team foreign KEY (team_id) references team (id) on delete CASCADE,
  constraint fk_user foreign KEY (user_id) references "user" (id) on delete CASCADE
) TABLESPACE pg_default;