"""
Contexto Tracking.

Rol en el Context Map: CONFORMIST. Consume el Published Language
(eventos de dominio) de Ventas y Operaciones sin pedir cambios.

Mantiene una vista de lectura optimizada del estado actual y el
historial de eventos de cada pedido, sin replicar lógica de negocio.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EventoRegistrado:
    """Evento histórico del seguimiento (no confundir con EventoDominio del bus)."""
    tipo: str
    descripcion: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SeguimientoPedido:
    """
    Agregado raíz del contexto Tracking.
    Proyección de solo-lectura construida a partir de eventos publicados.
    """
    pedido_id: str
    estado_actual: str = "Creado"
    historial: list[EventoRegistrado] = field(default_factory=list)

    def registrar(self, tipo: str, descripcion: str, nuevo_estado: str = "") -> None:
        self.historial.append(EventoRegistrado(tipo=tipo, descripcion=descripcion))
        if nuevo_estado:
            self.estado_actual = nuevo_estado
