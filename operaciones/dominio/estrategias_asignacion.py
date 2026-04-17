"""
Patrón Strategy para la asignación automática de repartidores.

Diferentes algoritmos pueden coexistir y cambiarse en runtime:
  - por menor carga actual
  - por orden de registro (round-robin simplificado)
  - (futuro) por cercanía geográfica, por zona, etc.

Cumple OCP: agregar una estrategia nueva no modifica las existentes.
Cumple DIP: el servicio de asignación depende de la abstracción IEstrategiaAsignacion.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from .repartidor import Repartidor


class IEstrategiaAsignacion(ABC):
    @abstractmethod
    def elegir(self, repartidores: list[Repartidor]) -> Optional[Repartidor]: ...


class EstrategiaMenorCarga(IEstrategiaAsignacion):
    """Elige el repartidor disponible con menos pedidos activos."""
    def elegir(self, repartidores: list[Repartidor]) -> Optional[Repartidor]:
        candidatos = [r for r in repartidores if r.puede_aceptar_pedido()]
        if not candidatos:
            return None
        return min(candidatos, key=lambda r: r.carga_actual())


class EstrategiaRoundRobin(IEstrategiaAsignacion):
    """Rota entre repartidores en el orden en que aparecen."""
    def __init__(self) -> None:
        self._indice = 0

    def elegir(self, repartidores: list[Repartidor]) -> Optional[Repartidor]:
        candidatos = [r for r in repartidores if r.puede_aceptar_pedido()]
        if not candidatos:
            return None
        elegido = candidatos[self._indice % len(candidatos)]
        self._indice += 1
        return elegido


class EstrategiaPorCercania(IEstrategiaAsignacion):
    """
    Elige el repartidor disponible más cercano a un punto de referencia.
    Demuestra cómo extender sin tocar lo existente (OCP).
    """
    def __init__(self, punto_referencia: tuple[float, float]) -> None:
        self._punto = punto_referencia

    def elegir(self, repartidores: list[Repartidor]) -> Optional[Repartidor]:
        candidatos = [r for r in repartidores if r.puede_aceptar_pedido()]
        if not candidatos:
            return None
        ref_lat, ref_lon = self._punto

        def distancia_cuadrada(r: Repartidor) -> float:
            lat, lon = r.ubicacion_actual
            return (lat - ref_lat) ** 2 + (lon - ref_lon) ** 2

        return min(candidatos, key=distancia_cuadrada)
