drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  operand1 text not null,
  operator text not null,
  operand2 text not null,
  result text not null
);
