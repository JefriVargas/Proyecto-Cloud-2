/*
Consulta: Disponibilidad de funciones por tenant
Une funciones con películas para mostrar la disponibilidad de asientos por tenant.
*/
SELECT 
    p.titulo AS movie_title,
    h.function_date,
    h.available_seats,
    h.tenant_id AS function_tenant
FROM "catalogo_dev"."horarios-dev_data" h
JOIN "catalogo_dev"."peliculas-dev_data" p
    ON h.movie_id = p.movie_id;

/*
Vista asociada
*/
CREATE OR REPLACE VIEW "catalogo_dev"."vista_disponibilidad_funciones" AS
SELECT 
    p.titulo AS movie_title,
    h.function_date,
    h.available_seats,
    h.tenant_id AS function_tenant
FROM "catalogo_dev"."horarios-dev_data" h
JOIN "catalogo_dev"."peliculas-dev_data" p
    ON h.movie_id = p.movie_id;
