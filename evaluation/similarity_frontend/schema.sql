drop table if exists semmul_image_similarity;
create table semmul_image_similarity (
  id integer primary key autoincrement,
  image_1_id integer not null,
  image_2_id integer not null,
  semantic_similarity text not null,
  visual_similarity text not null,
  nicname text,
  email text,
  created_at timestamp default current_timestamp
);