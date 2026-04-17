"""
Patrón State aplicado también al ciclo de vida de la Incidencia.

Estados: Abierta → EnAnalisis → EnResolucion → Resuelta.

Muestra que el patrón State es reutilizable y coherente en otro agregado
distinto al Pedido, manteniendo el lenguaje ubicuo y cumpliendo OCP.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .incidencia import Incidencia


class TransicionIncidenciaInvalida(Exception):
    pass


class EstadoIncidencia(ABC):
    @property
    @abstractmethod
    def nombre(self) -> str: ...

    def analizar(self, incidencia: "Incidencia") -> None:
        raise TransicionIncidenciaInvalida(
            f"No se puede analizar una incidencia {self.nombre}"
        )

    def resolver(self, incidencia: "Incidencia", resolucion: str) -> None:
        raise TransicionIncidenciaInvalida(
            f"No se puede resolver una incidencia en estado {self.nombre}"
        )

    def cerrar(self, incidencia: "Incidencia") -> None:
        raise TransicionIncidenciaInvalida(
            f"No se puede cerrar una incidencia en estado {self.nombre}"
        )


class Abierta(EstadoIncidencia):
    @property
    def nombre(self) -> str: return "Abierta"

    def analizar(self, incidencia: "Incidencia") -> None:
        incidencia._estado = EnAnalisis()


class EnAnalisis(EstadoIncidencia):
    @property
    def nombre(self) -> str: return "EnAnalisis"

    def resolver(self, incidencia: "Incidencia", resolucion: str) -> None:
        if not resolucion.strip():
            raise TransicionIncidenciaInvalida(
                "No se puede pasar a EnResolucion sin una resolución propuesta"
            )
        incidencia.resolucion_propuesta = resolucion
        incidencia._estado = EnResolucion()


class EnResolucion(EstadoIncidencia):
    @property
    def nombre(self) -> str: return "EnResolucion"

    def cerrar(self, incidencia: "Incidencia") -> None:
        # Regla: no se puede cerrar sin resolución
        if not incidencia.resolucion_propuesta:
            raise TransicionIncidenciaInvalida(
                "Una incidencia no puede cerrarse sin resolución"
            )
        incidencia._estado = Resuelta()


class Resuelta(EstadoIncidencia):
    @property
    def nombre(self) -> str: return "Resuelta"
    # Estado terminal: ninguna transición heredada funciona.
