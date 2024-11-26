/*
Consulta: Productos más Vendidos por Tenant
Calcula los productos más vendidos para cada tenant
*/

/*Precalculo*/

CREATE OR REPLACE VIEW "catalogo_dev"."vista_ventas_productos" AS
SELECT 
    p.product_id,
    o.tenant_id,
    COUNT(*) AS cantidad_vendida,
    SUM(p.price) AS ingresos_totales
FROM "catalogo_dev"."ordenes-dev_data" o
CROSS JOIN UNNEST(o.products) AS t (p)
GROUP BY p.product_id, o.tenant_id;



SELECT
    pd.product_id,
    pd.name AS nombre_producto,
    pd.tenant_id,
    v.cantidad_vendida,
    v.ingresos_totales
FROM "catalogo_dev"."vista_ventas_productos" v
JOIN "catalogo_dev"."productos-dev_data" pd
    ON v.product_id = pd.product_id
ORDER BY pd.tenant_id, v.cantidad_vendida DESC;


/*
Vista asociada
*/

CREATE OR REPLACE VIEW "catalogo_dev"."vista_ingresos_productos" AS
SELECT
    pd.product_id,
    pd.name AS nombre_producto,
    pd.tenant_id,
    v.cantidad_vendida,
    v.ingresos_totales
FROM "catalogo_dev"."vista_ventas_productos" v
JOIN "catalogo_dev"."productos-dev_data" pd
    ON v.product_id = pd.product_id
ORDER BY pd.tenant_id, v.cantidad_vendida DESC;
