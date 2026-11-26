begin;

create table public.gtl_dashboard_snapshot (
  id integer primary key check (id = 1),
  rows jsonb not null default '[]'::jsonb check (jsonb_typeof(rows) = 'array'),
  updated_at timestamptz
);

insert into public.gtl_dashboard_snapshot (id) values (1);

alter table public.gtl_dashboard_snapshot enable row level security;
revoke all on public.gtl_dashboard_snapshot from public, anon, authenticated;
grant select on public.gtl_dashboard_snapshot to anon, authenticated;
grant update (rows) on public.gtl_dashboard_snapshot to authenticated;

create policy "Dashboard viewers can read the snapshot"
  on public.gtl_dashboard_snapshot for select to anon, authenticated
  using (true);

create policy "Dashboard admin can replace the snapshot"
  on public.gtl_dashboard_snapshot for update to authenticated
  using ((select auth.jwt()->>'email') = 'sandunpersonal@gmail.com')
  with check ((select auth.jwt()->>'email') = 'sandunpersonal@gmail.com');

create function public.gtl_stamp_dashboard_snapshot()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if jsonb_typeof(new.rows) is distinct from 'array' then
    raise exception 'The snapshot must contain an array of zone records';
  end if;
  if jsonb_array_length(new.rows) = 0 then
    raise exception 'The snapshot must contain zone records';
  end if;
  new.updated_at := clock_timestamp();
  return new;
end;
$$;

revoke all on function public.gtl_stamp_dashboard_snapshot() from public, anon, authenticated;
create trigger gtl_stamp_dashboard_snapshot
  before update of rows on public.gtl_dashboard_snapshot
  for each row execute function public.gtl_stamp_dashboard_snapshot();

commit;
