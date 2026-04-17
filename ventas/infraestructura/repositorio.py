"""
Repositorio de Pedidos.

Patrón Repository: abstrae la persistencia del dominio.
- El dominio depende de la interfaz (DIP).
- La interfaz solo contiene lo que un cliente de pedidos necesita (ISP).
- Implementación en memoria para simular sin motor de BD.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from ..dominio.pedido import Pedido


class IRepositorioPedidos(ABC):
    @abstractmethod
    def guardar(self, pedido: Pedido) -> None: ...

    @abstractmethod
    def obtener(self, pedido_id: str) -> Optional[Pedido]: ...

    @abstractmethod
    def listar(self) -> list[Pedido]: ...


class RepositorioPedidosEnMemoria(IRepositorioPedidos):
    def __init__(self) -> None:
        self._datos: dict[str, Pedido] = {}

    def guardar(self, pedido: Pedido) -> None:
        self._datos[pedido.id] = pedido

    def obtener(self, pedido_id: str) -> Optional[Pedido]:
        return self._datos.get(pedido_id)

    def listar(self) -> list[Pedido]:
        return list(self._datos.values())
