"""Repositorio de Incidencias (Repository + DIP + ISP)."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from ..dominio.incidencia import Incidencia


class IRepositorioIncidencias(ABC):
    @abstractmethod
    def guardar(self, incidencia: Incidencia) -> None: ...

    @abstractmethod
    def obtener(self, incidencia_id: str) -> Optional[Incidencia]: ...

    @abstractmethod
    def listar_por_pedido(self, pedido_id: str) -> list[Incidencia]: ...

    @abstractmethod
    def listar_todas(self) -> list[Incidencia]: ...


class RepositorioIncidenciasEnMemoria(IRepositorioIncidencias):
    def __init__(self) -> None:
        self._datos: dict[str, Incidencia] = {}

    def guardar(self, incidencia: Incidencia) -> None:
        self._datos[incidencia.id] = incidencia

    def obtener(self, incidencia_id: str) -> Optional[Incidencia]:
        return self._datos.get(incidencia_id)

    def listar_por_pedido(self, pedido_id: str) -> list[Incidencia]:
        return [i for i in self._datos.values() if i.pedido_id == pedido_id]

    def listar_todas(self) -> list[Incidencia]:
        return list(self._datos.values())
