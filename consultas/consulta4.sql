/*
Consulta: Usuarios y su historial de compras
Une usuarios con órdenes para mostrar el historial de compras de cada usuario en su tenant.
*/
SELECT 
    u.email AS user_email,
    u.tenant_id AS user_tenant,
    o.order_id,
    o.total_price,
    o.created_at AS purchase_date
FROM "catalogo_dev"."usuarios-dev_data" u
JOIN "catalogo_dev"."ordenes-dev_data" o
    ON u.email = o.email
    AND u.tenant_id = o.tenant_id;

/*
Vista asociada
*/
CREATE OR REPLACE VIEW "catalogo_dev"."vista_historial_usuarios" AS
SELECT 
    u.email AS user_email,
    u.tenant_id AS user_tenant,
    o.order_id,
    o.total_price,
    o.created_at AS purchase_date
FROM "catalogo_dev"."usuarios-dev_data" u
JOIN "catalogo_dev"."ordenes-dev_data" o
    ON u.email = o.email
    AND u.tenant_id = o.tenant_id;
