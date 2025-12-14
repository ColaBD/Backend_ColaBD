-- Create version table
create table "public"."version" (
  "id" uuid not null default gen_random_uuid(),
  "tag" integer not null,
  "created_at" timestamp with time zone not null default now(),
  "created_by" uuid not null,
  "comment" text,
  "data" jsonb not null
);

-- Create schema_version relationship table
create table "public"."schema_version" (
  "id" uuid not null default gen_random_uuid(),
  "schema_id" uuid not null,
  "version_id" uuid not null
);

-- Create indexes
CREATE INDEX idx_schema_version_schema_id ON public.schema_version USING btree (schema_id);
CREATE INDEX idx_schema_version_version_id ON public.schema_version USING btree (version_id);
CREATE INDEX idx_version_created_at ON public.version USING btree (created_at DESC);

-- Create unique indexes for primary keys
CREATE UNIQUE INDEX version_pkey ON public.version USING btree (id);
CREATE UNIQUE INDEX schema_version_pkey ON public.schema_version USING btree (id);

-- Add primary key constraints
alter table "public"."version" add constraint "version_pkey" PRIMARY KEY using index "version_pkey";
alter table "public"."schema_version" add constraint "schema_version_pkey" PRIMARY KEY using index "schema_version_pkey";

-- Add foreign key constraints
alter table "public"."schema_version" add constraint "fk_schema_version_schema" FOREIGN KEY (schema_id) REFERENCES public.schema(id) ON DELETE CASCADE not valid;
alter table "public"."schema_version" validate constraint "fk_schema_version_schema";

alter table "public"."schema_version" add constraint "fk_schema_version_version" FOREIGN KEY (version_id) REFERENCES public.version(id) ON DELETE CASCADE not valid;
alter table "public"."schema_version" validate constraint "fk_schema_version_version";

alter table "public"."version" add constraint "fk_version_user" FOREIGN KEY (created_by) REFERENCES public."user"(id) ON DELETE CASCADE not valid;
alter table "public"."version" validate constraint "fk_version_user";

-- Grant permissions for version table
grant delete on table "public"."version" to "anon";
grant insert on table "public"."version" to "anon";
grant references on table "public"."version" to "anon";
grant select on table "public"."version" to "anon";
grant trigger on table "public"."version" to "anon";
grant truncate on table "public"."version" to "anon";
grant update on table "public"."version" to "anon";

grant delete on table "public"."version" to "authenticated";
grant insert on table "public"."version" to "authenticated";
grant references on table "public"."version" to "authenticated";
grant select on table "public"."version" to "authenticated";
grant trigger on table "public"."version" to "authenticated";
grant truncate on table "public"."version" to "authenticated";
grant update on table "public"."version" to "authenticated";

grant delete on table "public"."version" to "service_role";
grant insert on table "public"."version" to "service_role";
grant references on table "public"."version" to "service_role";
grant select on table "public"."version" to "service_role";
grant trigger on table "public"."version" to "service_role";
grant truncate on table "public"."version" to "service_role";
grant update on table "public"."version" to "service_role";

-- Grant permissions for schema_version table
grant delete on table "public"."schema_version" to "anon";
grant insert on table "public"."schema_version" to "anon";
grant references on table "public"."schema_version" to "anon";
grant select on table "public"."schema_version" to "anon";
grant trigger on table "public"."schema_version" to "anon";
grant truncate on table "public"."schema_version" to "anon";
grant update on table "public"."schema_version" to "anon";

grant delete on table "public"."schema_version" to "authenticated";
grant insert on table "public"."schema_version" to "authenticated";
grant references on table "public"."schema_version" to "authenticated";
grant select on table "public"."schema_version" to "authenticated";
grant trigger on table "public"."schema_version" to "authenticated";
grant truncate on table "public"."schema_version" to "authenticated";
grant update on table "public"."schema_version" to "authenticated";

grant delete on table "public"."schema_version" to "service_role";
grant insert on table "public"."schema_version" to "service_role";
grant references on table "public"."schema_version" to "service_role";
grant select on table "public"."schema_version" to "service_role";
grant trigger on table "public"."schema_version" to "service_role";
grant truncate on table "public"."schema_version" to "service_role";
grant update on table "public"."schema_version" to "service_role";


