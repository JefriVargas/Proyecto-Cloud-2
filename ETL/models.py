from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Usuarios(BaseModel):
    email: str
    tenant_id: str
    nombre: str
    created_at: datetime

class Reservas(BaseModel):
    reservation_id: str
    email: str
    tenant_id: str
    function_date: Optional[datetime] = None
    movie_title: Optional[str] = None
    schedule_id: str
    seats: int

class Horarios(BaseModel):
    schedule_id: str
    movie_id: str
    tenant_id: str
    available_seats: int
    function_date: datetime

class Peliculas(BaseModel):
    movie_id: str
    tenant_id: str
    created_at: Optional[datetime] = None
    descripcion: Optional[str] = None
    genero: str
    release_date: datetime
    titulo: str

class Ordenes(BaseModel):
    order_id: str
    email: str
    tenant_id: str
    created_at: Optional[datetime] = None
    total_price: float

class OrdenesProductos(BaseModel):
    order_id: str
    product_id: str

class Productos(BaseModel):
    product_id: str
    tenant_id: str
    description: str
    name: str
    price: float
