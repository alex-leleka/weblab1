drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  operand1 integer not null,
  operator text not null
  operand2 integer not null
  result integer not null
);
