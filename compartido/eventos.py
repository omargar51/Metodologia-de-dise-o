"""
Eventos de dominio compartidos y bus de eventos.

Implementa el patrón Observer: los bounded contexts publican eventos
y otros contextos se suscriben sin acoplamiento directo.

Esto también materializa el Published Language del Context Map:
los eventos son el contrato público entre contextos.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Protocol
from collections import defaultdict


# ---------- Evento de dominio base ----------
@dataclass(frozen=True)
class EventoDominio:
    """Clase base para todos los eventos de dominio (Published Language)."""
    ocurrido_en: datetime = field(default_factory=datetime.now, init=False)


# ---------- Eventos publicados por Ventas ----------
@dataclass(frozen=True)
class PedidoCreado(EventoDominio):
    pedido_id: str = ""
    canal: str = ""


@dataclass(frozen=True)
class PedidoValidado(EventoDominio):
    pedido_id: str = ""


# ---------- Eventos publicados por Operaciones ----------
@dataclass(frozen=True)
class PedidoAsignado(EventoDominio):
    pedido_id: str = ""
    repartidor_id: str = ""


@dataclass(frozen=True)
class PedidoReasignado(EventoDominio):
    pedido_id: str = ""
    repartidor_anterior: str = ""
    repartidor_nuevo: str = ""


@dataclass(frozen=True)
class PedidoEnRuta(EventoDominio):
    pedido_id: str = ""


@dataclass(frozen=True)
class IntentoEntregaFallido(EventoDominio):
    pedido_id: str = ""
    motivo: str = ""


@dataclass(frozen=True)
class PedidoEntregado(EventoDominio):
    pedido_id: str = ""


@dataclass(frozen=True)
class PedidoCancelado(EventoDominio):
    pedido_id: str = ""


# ---------- Eventos publicados por Incidencias ----------
@dataclass(frozen=True)
class IncidenciaAbierta(EventoDominio):
    incidencia_id: str = ""
    pedido_id: str = ""
    tipo: str = ""


@dataclass(frozen=True)
class IncidenciaResuelta(EventoDominio):
    incidencia_id: str = ""
    pedido_id: str = ""


# ---------- Bus de eventos (Observer + Mediator) ----------
class Suscriptor(Protocol):
    def manejar(self, evento: EventoDominio) -> None: ...


class BusEventos:
    """
    Bus de eventos en memoria.
    Permite que los contextos se comuniquen vía Published Language
    sin conocerse entre sí (cumple DIP y bajo acoplamiento).
    """
    def __init__(self) -> None:
        self._suscriptores: dict[type, list[Callable[[EventoDominio], None]]] = defaultdict(list)

    def suscribir(self, tipo_evento: type, manejador: Callable[[EventoDominio], None]) -> None:
        self._suscriptores[tipo_evento].append(manejador)

    def publicar(self, evento: EventoDominio) -> None:
        for manejador in self._suscriptores[type(evento)]:
            manejador(evento)


# Instancia global del bus (inyectable)
bus_eventos = BusEventos()
