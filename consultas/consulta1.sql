/*
Consulta: Órdenes con detalle de productos y tenants
Desglosa cada orden con el detalle de los productos comprados y sus tenants
*/
SELECT 
    o.order_id,
    o.tenant_id AS order_tenant,
    o.email AS customer_email,
    p.name AS product_name,
    p.price AS product_price,
    o.total_price,
    o.created_at AS order_date
FROM "catalogo_dev"."ordenes-dev_data" o
CROSS JOIN UNNEST(o.products) AS t (p);

/*
Vista asociada
*/
CREATE OR REPLACE VIEW "catalogo_dev"."vista_detalle_ordenes" AS
SELECT 
    o.order_id,
    o.tenant_id AS order_tenant,
    o.email AS customer_email,
    p.name AS product_name,
    p.price AS product_price,
    o.total_price,
    o.created_at AS order_date
FROM "catalogo_dev"."ordenes-dev_data" o
CROSS JOIN UNNEST(o.products) AS t (p);
