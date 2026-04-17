"""
Caso de uso 1: Gestión de Pedidos
  a. Crear pedidos desde distintos canales
  b. Validar información
  c. Gestionar estados

El servicio de aplicación orquesta el dominio sin contener lógica de negocio.
Cumple SRP (una razón para cambiar: el flujo del caso de uso) y DIP
(depende de abstracciones: repositorio y bus de eventos).
"""
from __future__ import annotations
from typing import Any
from ..dominio.factories import RegistroFactoriesPedido
from ..dominio.value_objects import Canal
from ..infraestructura.repositorio import IRepositorioPedidos
from compartido.eventos import BusEventos, PedidoCreado, PedidoValidado


class ServicioPedidos:
    def __init__(
        self,
        factories: RegistroFactoriesPedido,
        repositorio: IRepositorioPedidos,
        bus: BusEventos,
    ) -> None:
        self._factories = factories
        self._repositorio = repositorio
        self._bus = bus

    # Caso 1.a — Crear pedido desde cualquier canal
    def crear_pedido(self, canal: Canal, datos_crudos: dict[str, Any]) -> str:
        factory = self._factories.obtener(canal)
        pedido = factory.crear(datos_crudos)
        self._repositorio.guardar(pedido)
        self._bus.publicar(PedidoCreado(pedido_id=pedido.id, canal=canal.value))
        return pedido.id

    # Caso 1.b — Validar información
    def validar_pedido(self, pedido_id: str) -> None:
        pedido = self._repositorio.obtener(pedido_id)
        if pedido is None:
            raise ValueError(f"Pedido {pedido_id} no existe")
        pedido.validar()
        # Tras validar, queda listo para asignación
        pedido.marcar_pendiente_asignacion()
        self._repositorio.guardar(pedido)
        self._bus.publicar(PedidoValidado(pedido_id=pedido.id))

    # Caso 1.c — Consultar estado (parte de "gestionar estados")
    def consultar_estado(self, pedido_id: str) -> str:
        pedido = self._repositorio.obtener(pedido_id)
        if pedido is None:
            raise ValueError(f"Pedido {pedido_id} no existe")
        return pedido.estado

    # Caso 1.c — Cancelar (transición disponible desde casi cualquier estado)
    def cancelar_pedido(self, pedido_id: str) -> None:
        pedido = self._repositorio.obtener(pedido_id)
        if pedido is None:
            raise ValueError(f"Pedido {pedido_id} no existe")
        pedido.cancelar()
        self._repositorio.guardar(pedido)
        from compartido.eventos import PedidoCancelado
        self._bus.publicar(PedidoCancelado(pedido_id=pedido.id))
