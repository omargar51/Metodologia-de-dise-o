"""Repositorio del contexto Tracking."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from ..dominio.seguimiento import SeguimientoPedido


class IRepositorioSeguimientos(ABC):
    @abstractmethod
    def guardar(self, seguimiento: SeguimientoPedido) -> None: ...

    @abstractmethod
    def obtener(self, pedido_id: str) -> Optional[SeguimientoPedido]: ...

    @abstractmethod
    def obtener_o_crear(self, pedido_id: str) -> SeguimientoPedido: ...


class RepositorioSeguimientosEnMemoria(IRepositorioSeguimientos):
    def __init__(self) -> None:
        self._datos: dict[str, SeguimientoPedido] = {}

    def guardar(self, seguimiento: SeguimientoPedido) -> None:
        self._datos[seguimiento.pedido_id] = seguimiento

    def obtener(self, pedido_id: str) -> Optional[SeguimientoPedido]:
        return self._datos.get(pedido_id)

    def obtener_o_crear(self, pedido_id: str) -> SeguimientoPedido:
        if pedido_id not in self._datos:
            self._datos[pedido_id] = SeguimientoPedido(pedido_id=pedido_id)
        return self._datos[pedido_id]
