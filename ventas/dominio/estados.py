"""
Patrón State aplicado al ciclo de vida del Pedido.

El enunciado es explícito: el flujo NO es lineal. Hay re-asignaciones,
cancelaciones desde cualquier estado, y un pedido entregado puede
generar eventos posteriores (reclamos).

El patrón State:
  - hace cada estado una clase con sus transiciones válidas
  - evita un if/else gigante en Pedido
  - cumple OCP: agregar un estado no modifica los existentes
  - cumple LSP: todos los estados son intercambiables donde se espere EstadoPedido
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pedido import Pedido


class TransicionInvalida(Exception):
    """Se intentó una transición de estado no permitida por las reglas del dominio."""
    pass


class EstadoPedido(ABC):
    """Clase base abstracta para todos los estados del pedido."""

    @property
    @abstractmethod
    def nombre(self) -> str: ...

    # Por defecto, ninguna transición es válida.
    # Cada estado concreto habilita solo las que le corresponden.
    def validar(self, pedido: "Pedido") -> None:
        raise TransicionInvalida(f"No se puede validar un pedido en estado {self.nombre}")

    def marcar_pendiente_asignacion(self, pedido: "Pedido") -> None:
        raise TransicionInvalida(f"No se puede marcar como pendiente desde {self.nombre}")

    def asignar(self, pedido: "Pedido") -> None:
        raise TransicionInvalida(f"No se puede asignar un pedido en estado {self.nombre}")

    def iniciar_ruta(self, pedido: "Pedido") -> None:
        raise TransicionInvalida(f"No se puede iniciar ruta desde {self.nombre}")

    def registrar_intento_fallido(self, pedido: "Pedido") -> None:
        raise TransicionInvalida(f"No se puede registrar intento fallido desde {self.nombre}")

    def reprogramar(self, pedido: "Pedido") -> None:
        raise TransicionInvalida(f"No se puede reprogramar desde {self.nombre}")

    def entregar(self, pedido: "Pedido") -> None:
        raise TransicionInvalida(f"No se puede entregar un pedido en estado {self.nombre}")

    # La cancelación está permitida desde casi cualquier estado;
    # cada estado decide si la acepta.
    def cancelar(self, pedido: "Pedido") -> None:
        pedido._estado = Cancelado()


class Creado(EstadoPedido):
    @property
    def nombre(self) -> str: return "Creado"

    def validar(self, pedido: "Pedido") -> None:
        pedido._verificar_informacion_minima()
        pedido._estado = Validado()


class Validado(EstadoPedido):
    @property
    def nombre(self) -> str: return "Validado"

    def marcar_pendiente_asignacion(self, pedido: "Pedido") -> None:
        pedido._estado = PendienteAsignacion()


class PendienteAsignacion(EstadoPedido):
    @property
    def nombre(self) -> str: return "PendienteAsignacion"

    def asignar(self, pedido: "Pedido") -> None:
        pedido._estado = Asignado()


class Asignado(EstadoPedido):
    @property
    def nombre(self) -> str: return "Asignado"

    def iniciar_ruta(self, pedido: "Pedido") -> None:
        pedido._estado = EnRuta()

    # Re-asignación: Asignado -> PendienteAsignacion (permitido)
    def marcar_pendiente_asignacion(self, pedido: "Pedido") -> None:
        pedido._estado = PendienteAsignacion()


class EnRuta(EstadoPedido):
    @property
    def nombre(self) -> str: return "EnRuta"

    def registrar_intento_fallido(self, pedido: "Pedido") -> None:
        pedido._estado = IntentoFallido()

    def entregar(self, pedido: "Pedido") -> None:
        pedido._estado = Entregado()


class IntentoFallido(EstadoPedido):
    @property
    def nombre(self) -> str: return "IntentoFallido"

    def reprogramar(self, pedido: "Pedido") -> None:
        pedido._estado = Reprogramado()


class Reprogramado(EstadoPedido):
    @property
    def nombre(self) -> str: return "Reprogramado"

    def asignar(self, pedido: "Pedido") -> None:
        pedido._estado = Asignado()


class Entregado(EstadoPedido):
    @property
    def nombre(self) -> str: return "Entregado"

    # Regla: un pedido entregado NO puede volver a estados anteriores.
    # Pero sí puede generar incidencias (eso se maneja en el contexto de Incidencias,
    # no como transición de estado aquí).

    # Regla: un pedido entregado tampoco puede cancelarse.
    def cancelar(self, pedido: "Pedido") -> None:
        raise TransicionInvalida("Un pedido entregado no puede ser cancelado")


class Cancelado(EstadoPedido):
    @property
    def nombre(self) -> str: return "Cancelado"

    # Regla: un pedido cancelado no puede continuar el flujo.
    # Todos los métodos heredados de EstadoPedido ya lanzan TransicionInvalida,
    # incluyendo cancelar() que también bloqueamos explícitamente.
    def cancelar(self, pedido: "Pedido") -> None:
        raise TransicionInvalida("El pedido ya está cancelado")
