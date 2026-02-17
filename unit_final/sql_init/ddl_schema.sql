CREATE TABLE IF NOT EXISTS client_queries(
  id bigserial PRIMARY KEY,
  ts timestamptz DEFAULT now(),
  user_id text,
  query text
);

CREATE TABLE IF NOT EXISTS products(
  id bigserial PRIMARY KEY,
  ts timestamptz DEFAULT now(),
  value text
);