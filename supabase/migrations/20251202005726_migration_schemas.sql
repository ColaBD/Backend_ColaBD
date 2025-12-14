
  create table "public"."schema" (
    "id" uuid not null default gen_random_uuid(),
    "inserted_at" timestamp with time zone default now(),
    "title" text not null,
    "database_model" character varying,
    "display_picture" text,
    "updated_at" timestamp with time zone
      );



  create table "public"."team" (
    "id" uuid not null default gen_random_uuid(),
    "inserted_at" timestamp with time zone default now(),
    "name" text not null,
    "owner_user_id" uuid not null
      );



  create table "public"."user" (
    "inserted_at" timestamp with time zone not null default now(),
    "name" text not null,
    "email" text not null,
    "password" text not null,
    "id" uuid not null
      );



  create table "public"."user_schema" (
    "id" uuid not null default gen_random_uuid(),
    "user_id" uuid not null,
    "schema_id" uuid not null
      );



  create table "public"."user_team" (
    "id" uuid not null default gen_random_uuid(),
    "user_id" uuid not null,
    "team_id" uuid not null
      );


CREATE INDEX idx_user_schema_schema_id ON public.user_schema USING btree (schema_id);

CREATE INDEX idx_user_schema_user_id ON public.user_schema USING btree (user_id);

CREATE UNIQUE INDEX schema_pkey ON public.schema USING btree (id);

CREATE UNIQUE INDEX team_pkey ON public.team USING btree (id);

CREATE UNIQUE INDEX user_email_key ON public."user" USING btree (email);

CREATE UNIQUE INDEX user_pkey ON public."user" USING btree (id);

CREATE UNIQUE INDEX user_schema_pkey ON public.user_schema USING btree (id);

CREATE UNIQUE INDEX user_team_pkey ON public.user_team USING btree (id);

alter table "public"."schema" add constraint "schema_pkey" PRIMARY KEY using index "schema_pkey";

alter table "public"."team" add constraint "team_pkey" PRIMARY KEY using index "team_pkey";

alter table "public"."user" add constraint "user_pkey" PRIMARY KEY using index "user_pkey";

alter table "public"."user_schema" add constraint "user_schema_pkey" PRIMARY KEY using index "user_schema_pkey";

alter table "public"."user_team" add constraint "user_team_pkey" PRIMARY KEY using index "user_team_pkey";

alter table "public"."team" add constraint "fk_user_id" FOREIGN KEY (owner_user_id) REFERENCES public."user"(id) ON DELETE CASCADE not valid;

alter table "public"."team" validate constraint "fk_user_id";

alter table "public"."user" add constraint "user_email_key" UNIQUE using index "user_email_key";

alter table "public"."user_schema" add constraint "fk_user_schema_schema" FOREIGN KEY (schema_id) REFERENCES public.schema(id) ON DELETE CASCADE not valid;

alter table "public"."user_schema" validate constraint "fk_user_schema_schema";

alter table "public"."user_schema" add constraint "fk_user_schema_user" FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE not valid;

alter table "public"."user_schema" validate constraint "fk_user_schema_user";

alter table "public"."user_team" add constraint "fk_team" FOREIGN KEY (team_id) REFERENCES public.team(id) ON DELETE CASCADE not valid;

alter table "public"."user_team" validate constraint "fk_team";

alter table "public"."user_team" add constraint "fk_user" FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE not valid;

alter table "public"."user_team" validate constraint "fk_user";

grant delete on table "public"."schema" to "anon";

grant insert on table "public"."schema" to "anon";

grant references on table "public"."schema" to "anon";

grant select on table "public"."schema" to "anon";

grant trigger on table "public"."schema" to "anon";

grant truncate on table "public"."schema" to "anon";

grant update on table "public"."schema" to "anon";

grant delete on table "public"."schema" to "authenticated";

grant insert on table "public"."schema" to "authenticated";

grant references on table "public"."schema" to "authenticated";

grant select on table "public"."schema" to "authenticated";

grant trigger on table "public"."schema" to "authenticated";

grant truncate on table "public"."schema" to "authenticated";

grant update on table "public"."schema" to "authenticated";

grant delete on table "public"."schema" to "service_role";

grant insert on table "public"."schema" to "service_role";

grant references on table "public"."schema" to "service_role";

grant select on table "public"."schema" to "service_role";

grant trigger on table "public"."schema" to "service_role";

grant truncate on table "public"."schema" to "service_role";

grant update on table "public"."schema" to "service_role";

grant delete on table "public"."team" to "anon";

grant insert on table "public"."team" to "anon";

grant references on table "public"."team" to "anon";

grant select on table "public"."team" to "anon";

grant trigger on table "public"."team" to "anon";

grant truncate on table "public"."team" to "anon";

grant update on table "public"."team" to "anon";

grant delete on table "public"."team" to "authenticated";

grant insert on table "public"."team" to "authenticated";

grant references on table "public"."team" to "authenticated";

grant select on table "public"."team" to "authenticated";

grant trigger on table "public"."team" to "authenticated";

grant truncate on table "public"."team" to "authenticated";

grant update on table "public"."team" to "authenticated";

grant delete on table "public"."team" to "service_role";

grant insert on table "public"."team" to "service_role";

grant references on table "public"."team" to "service_role";

grant select on table "public"."team" to "service_role";

grant trigger on table "public"."team" to "service_role";

grant truncate on table "public"."team" to "service_role";

grant update on table "public"."team" to "service_role";

grant delete on table "public"."user" to "anon";

grant insert on table "public"."user" to "anon";

grant references on table "public"."user" to "anon";

grant select on table "public"."user" to "anon";

grant trigger on table "public"."user" to "anon";

grant truncate on table "public"."user" to "anon";

grant update on table "public"."user" to "anon";

grant delete on table "public"."user" to "authenticated";

grant insert on table "public"."user" to "authenticated";

grant references on table "public"."user" to "authenticated";

grant select on table "public"."user" to "authenticated";

grant trigger on table "public"."user" to "authenticated";

grant truncate on table "public"."user" to "authenticated";

grant update on table "public"."user" to "authenticated";

grant delete on table "public"."user" to "service_role";

grant insert on table "public"."user" to "service_role";

grant references on table "public"."user" to "service_role";

grant select on table "public"."user" to "service_role";

grant trigger on table "public"."user" to "service_role";

grant truncate on table "public"."user" to "service_role";

grant update on table "public"."user" to "service_role";

grant delete on table "public"."user_schema" to "anon";

grant insert on table "public"."user_schema" to "anon";

grant references on table "public"."user_schema" to "anon";

grant select on table "public"."user_schema" to "anon";

grant trigger on table "public"."user_schema" to "anon";

grant truncate on table "public"."user_schema" to "anon";

grant update on table "public"."user_schema" to "anon";

grant delete on table "public"."user_schema" to "authenticated";

grant insert on table "public"."user_schema" to "authenticated";

grant references on table "public"."user_schema" to "authenticated";

grant select on table "public"."user_schema" to "authenticated";

grant trigger on table "public"."user_schema" to "authenticated";

grant truncate on table "public"."user_schema" to "authenticated";

grant update on table "public"."user_schema" to "authenticated";

grant delete on table "public"."user_schema" to "service_role";

grant insert on table "public"."user_schema" to "service_role";

grant references on table "public"."user_schema" to "service_role";

grant select on table "public"."user_schema" to "service_role";

grant trigger on table "public"."user_schema" to "service_role";

grant truncate on table "public"."user_schema" to "service_role";

grant update on table "public"."user_schema" to "service_role";

grant delete on table "public"."user_team" to "anon";

grant insert on table "public"."user_team" to "anon";

grant references on table "public"."user_team" to "anon";

grant select on table "public"."user_team" to "anon";

grant trigger on table "public"."user_team" to "anon";

grant truncate on table "public"."user_team" to "anon";

grant update on table "public"."user_team" to "anon";

grant delete on table "public"."user_team" to "authenticated";

grant insert on table "public"."user_team" to "authenticated";

grant references on table "public"."user_team" to "authenticated";

grant select on table "public"."user_team" to "authenticated";

grant trigger on table "public"."user_team" to "authenticated";

grant truncate on table "public"."user_team" to "authenticated";

grant update on table "public"."user_team" to "authenticated";

grant delete on table "public"."user_team" to "service_role";

grant insert on table "public"."user_team" to "service_role";

grant references on table "public"."user_team" to "service_role";

grant select on table "public"."user_team" to "service_role";

grant trigger on table "public"."user_team" to "service_role";

grant truncate on table "public"."user_team" to "service_role";

grant update on table "public"."user_team" to "service_role";


