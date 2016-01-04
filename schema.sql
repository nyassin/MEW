drop table if exists entries;
create table entries (
  user_id text primary key not null,
  access_token text not null,
  countries integer not null default 0
);