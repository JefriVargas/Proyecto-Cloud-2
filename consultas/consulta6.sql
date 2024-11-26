/*
Consulta: Reservas y sus ingresos por tenant
Agrupa las reservas por tenant y calcula el total de ingresos relacionados.
*/
SELECT 
    r.tenant_id AS reservation_tenant,
    COUNT(r.reservation_id) AS total_reservations,
    SUM(o.total_price) AS total_revenue
FROM "catalogo_dev"."reservas-dev_data" r
JOIN "catalogo_dev"."ordenes-dev_data" o
    ON r.email = o.email
    AND r.tenant_id = o.tenant_id
GROUP BY r.tenant_id;

/*
Vista asociada
*/
CREATE OR REPLACE VIEW "catalogo_dev"."vista_reservas_ingresos" AS
SELECT 
    r.tenant_id AS reservation_tenant,
    COUNT(r.reservation_id) AS total_reservations,
    SUM(o.total_price) AS total_revenue
FROM "catalogo_dev"."reservas-dev_data" r
JOIN "catalogo_dev"."ordenes-dev_data" o
    ON r.email = o.email
    AND r.tenant_id = o.tenant_id
GROUP BY r.tenant_id;
