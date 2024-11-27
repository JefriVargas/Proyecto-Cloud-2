from pydantic import BaseModel

class Transform:
    def __init__(
            self,
            primary_schema: BaseModel,
            related_schema: BaseModel = None,
            relation_field: str = None
    ):
        self.primary_schema = primary_schema
        self.related_schema = related_schema
        self.relation_field = relation_field

    def transform(self, data: list[dict[str, None]]) -> dict[str, list[BaseModel]]:
        primary_entities = []
        related_entities = []

        for item in data:
            # Validar y procesar la entidad principal
            primary_entity = self._transform_item(item, self.primary_schema)
            primary_entities.append(primary_entity)

            # Procesar datos relacionados si están presentes
            if self.related_schema and self.relation_field and self.relation_field in item:
                related_items = item[self.relation_field]
                for related_item in related_items:
                    related_item["order_id"] = item["order_id"]  # Añade la clave de relación
                    related_entity = self._transform_item(related_item, self.related_schema)
                    related_entities.append(related_entity)

        return {"primary": primary_entities, "related": related_entities}

    def _transform_item(self, item: dict[str, None], schema: BaseModel) -> BaseModel:
        try:
            return schema(**item)
        except Exception as e:
            raise ValueError(f"Error al transformar el item: {item}. Detalle: {e}")

