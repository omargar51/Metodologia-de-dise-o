"""Repositorio de Repartidores (Repository + DIP + ISP)."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from ..dominio.repartidor import Repartidor


class IRepositorioRepartidores(ABC):
    @abstractmethod
    def guardar(self, repartidor: Repartidor) -> None: ...

    @abstractmethod
    def obtener(self, repartidor_id: str) -> Optional[Repartidor]: ...

    @abstractmethod
    def listar_disponibles(self) -> list[Repartidor]: ...

    @abstractmethod
    def listar_todos(self) -> list[Repartidor]: ...


class RepositorioRepartidoresEnMemoria(IRepositorioRepartidores):
    def __init__(self) -> None:
        self._datos: dict[str, Repartidor] = {}

    def guardar(self, repartidor: Repartidor) -> None:
        self._datos[repartidor.id] = repartidor

    def obtener(self, repartidor_id: str) -> Optional[Repartidor]:
        return self._datos.get(repartidor_id)

    def listar_disponibles(self) -> list[Repartidor]:
        return [r for r in self._datos.values() if r.disponible]

    def listar_todos(self) -> list[Repartidor]:
        return list(self._datos.values())
