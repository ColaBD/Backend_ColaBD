revoke delete on table "public"."schema_version" from "anon";

revoke insert on table "public"."schema_version" from "anon";

revoke references on table "public"."schema_version" from "anon";

revoke select on table "public"."schema_version" from "anon";

revoke trigger on table "public"."schema_version" from "anon";

revoke truncate on table "public"."schema_version" from "anon";

revoke update on table "public"."schema_version" from "anon";

revoke delete on table "public"."schema_version" from "authenticated";

revoke insert on table "public"."schema_version" from "authenticated";

revoke references on table "public"."schema_version" from "authenticated";

revoke select on table "public"."schema_version" from "authenticated";

revoke trigger on table "public"."schema_version" from "authenticated";

revoke truncate on table "public"."schema_version" from "authenticated";

revoke update on table "public"."schema_version" from "authenticated";

revoke delete on table "public"."schema_version" from "service_role";

revoke insert on table "public"."schema_version" from "service_role";

revoke references on table "public"."schema_version" from "service_role";

revoke select on table "public"."schema_version" from "service_role";

revoke trigger on table "public"."schema_version" from "service_role";

revoke truncate on table "public"."schema_version" from "service_role";

revoke update on table "public"."schema_version" from "service_role";

revoke delete on table "public"."version" from "anon";

revoke insert on table "public"."version" from "anon";

revoke references on table "public"."version" from "anon";

revoke select on table "public"."version" from "anon";

revoke trigger on table "public"."version" from "anon";

revoke truncate on table "public"."version" from "anon";

revoke update on table "public"."version" from "anon";

revoke delete on table "public"."version" from "authenticated";

revoke insert on table "public"."version" from "authenticated";

revoke references on table "public"."version" from "authenticated";

revoke select on table "public"."version" from "authenticated";

revoke trigger on table "public"."version" from "authenticated";

revoke truncate on table "public"."version" from "authenticated";

revoke update on table "public"."version" from "authenticated";

revoke delete on table "public"."version" from "service_role";

revoke insert on table "public"."version" from "service_role";

revoke references on table "public"."version" from "service_role";

revoke select on table "public"."version" from "service_role";

revoke trigger on table "public"."version" from "service_role";

revoke truncate on table "public"."version" from "service_role";

revoke update on table "public"."version" from "service_role";

alter table "public"."schema_version" drop constraint "fk_schema_version_schema";

alter table "public"."schema_version" drop constraint "fk_schema_version_version";

alter table "public"."version" drop constraint "fk_version_user";

alter table "public"."schema_version" drop constraint "schema_version_pkey";

alter table "public"."version" drop constraint "version_pkey";

drop index if exists "public"."idx_schema_version_schema_id";

drop index if exists "public"."idx_schema_version_version_id";

drop index if exists "public"."idx_version_created_at";

drop index if exists "public"."schema_version_pkey";

drop index if exists "public"."version_pkey";

drop table "public"."schema_version";

drop table "public"."version";


