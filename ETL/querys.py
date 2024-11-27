class Queries:

    @staticmethod
    def ordenes_query():
        return """
        SELECT 
            order_id,
            tenant_id,
            email,
            total_price,
            created_at,
            CAST(products AS JSON) AS products
        FROM "catalogo_dev"."ordenes-dev_data";
        """

    @staticmethod
    def horarios_query():
        return """
        SELECT 
            schedule_id,
            movie_id,
            tenant_id,
            function_date,
            available_seats
        FROM "catalogo_dev"."horarios-dev_data";
        """

    @staticmethod
    def peliculas_query():
        return """
        SELECT 
            movie_id,
            titulo,
            tenant_id,
            genero,
            release_date,
            created_at,
            descripcion
        FROM "catalogo_dev"."peliculas-dev_data";
        """

    @staticmethod
    def productos_query():
        return """
        SELECT 
            product_id,
            name,
            description,
            price,
            tenant_id
        FROM "catalogo_dev"."productos-dev_data";
        """

    @staticmethod
    def reservas_query():
        return """
        SELECT 
            reservation_id,
            tenant_id,
            email,
            function_date,
            movie_title,
            schedule_id,
            seats
        FROM "catalogo_dev"."reservas-dev_data";
        """

    @staticmethod
    def usuarios_query():
        return """
        SELECT 
            email,
            tenant_id,
            nombre,
            created_at
        FROM "catalogo_dev"."usuarios-dev_data";
        """
