/*
Consulta: Reservas por tenant con películas
Desglosa las reservas por tenant con las película asociada
*/
SELECT 
    r.reservation_id,
    r.tenant_id AS reservation_tenant,
    p.titulo AS movie_title,
    r.function_date,
    r.seats AS reserved_seats
FROM "catalogo_dev"."reservas-dev_data" r
JOIN "catalogo_dev"."horarios-dev_data" h 
    ON r.schedule_id = h.schedule_id
JOIN "catalogo_dev"."peliculas-dev_data" p
    ON h.movie_id = p.movie_id;

/*
Vista asociada
*/
CREATE OR REPLACE VIEW "catalogo_dev"."vista_reservas_por_tenant" AS
SELECT 
    r.reservation_id,
    r.tenant_id AS reservation_tenant,
    p.titulo AS movie_title,
    r.function_date,
    r.seats AS reserved_seats
FROM "catalogo_dev"."reservas-dev_data" r
JOIN "catalogo_dev"."horarios-dev_data" h 
    ON r.schedule_id = h.schedule_id
JOIN "catalogo_dev"."peliculas-dev_data" p
    ON h.movie_id = p.movie_id;
