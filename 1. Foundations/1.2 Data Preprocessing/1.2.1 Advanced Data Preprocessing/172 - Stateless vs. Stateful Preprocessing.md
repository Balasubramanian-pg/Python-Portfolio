# Stateless vs. Stateful Preprocessing

Stateless steps (e.g., log transformation, dropping a column) require no memory of the data. Stateful steps (e.g., standard scaling, target encoding) "learn" parameters and must be carefully managed to avoid leakage.
