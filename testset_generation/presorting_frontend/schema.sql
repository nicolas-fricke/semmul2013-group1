drop table if exists semmul_images;
create table semmul_images (
  id integer primary key autoincrement,
  image_id integer not null,
  contains_food integer not null,
  nicname text,
  email text
);