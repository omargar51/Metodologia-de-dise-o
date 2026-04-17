"""
Value Objects del contexto Ventas.

Son objetos inmutables definidos por sus atributos (sin identidad propia).
Representan conceptos del dominio que no necesitan seguirse en el tiempo.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class TipoEntrega(Enum):
    NORMAL = "normal"
    EXPRESS = "express"
    PROGRAMADA = "programada"


class Canal(Enum):
    ECOMMERCE = "ecommerce"
    COMERCIO = "comercio"
    PROPIO = "propio"


@dataclass(frozen=True)
class Direccion:
    calle: str
    numero: str
    ciudad: str
    referencia: str = ""

    def es_interpretable(self) -> bool:
        """Regla de negocio: la dirección debe ser mínimamente interpretable."""
        return bool(self.calle.strip()) and bool(self.numero.strip()) and bool(self.ciudad.strip())


@dataclass(frozen=True)
class Destinatario:
    nombre: str
    medio_contacto: str  # email o teléfono

    def es_valido(self) -> bool:
        return bool(self.nombre.strip()) and bool(self.medio_contacto.strip())


@dataclass(frozen=True)
class Carga:
    tipo: str
    peso_kg: float

    def es_valida(self) -> bool:
        return bool(self.tipo.strip()) and self.peso_kg > 0


@dataclass(frozen=True)
class VentanaEntrega:
    desde: str  # formato HH:MM
    hasta: str
