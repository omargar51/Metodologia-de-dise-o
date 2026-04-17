"""
Caso de uso 5: Monitoreo y Tracking
  a. Visualizar estados
  b. Notificar clientes
  c. Registrar eventos

Este servicio materializa dos cosas:
  1. El rol CONFORMIST del contexto Tracking: se suscribe a eventos
     de Ventas y Operaciones y construye su propia proyección.
  2. El patrón OBSERVER: reacciona a eventos del bus de forma desacoplada.

El servicio también usa Strategy (canales de notificación inyectables).
"""
from __future__ import annotations
from ..dominio.canales_notificacion import ICanalNotificacion
from ..infraestructura.repositorio import IRepositorioSeguimientos
from ventas.infraestructura.repositorio import IRepositorioPedidos
from compartido.eventos import (
    BusEventos,
    PedidoCreado, PedidoValidado, PedidoAsignado, PedidoReasignado,
    PedidoEnRuta, IntentoEntregaFallido, PedidoEntregado, PedidoCancelado,
)


class ServicioTracking:
    def __init__(
        self,
        repo_seguimientos: IRepositorioSeguimientos,
        repo_pedidos: IRepositorioPedidos,
        canales: list[ICanalNotificacion],
        bus: BusEventos,
    ) -> None:
        self._repo_seguimientos = repo_seguimientos
        self._repo_pedidos = repo_pedidos
        self._canales = canales
        self._suscribirse_a_eventos(bus)

    # ---- Suscripción a eventos (Observer) ----
    def _suscribirse_a_eventos(self, bus: BusEventos) -> None:
        bus.suscribir(PedidoCreado, self._al_crear)
        bus.suscribir(PedidoValidado, self._al_validar)
        bus.suscribir(PedidoAsignado, self._al_asignar)
        bus.suscribir(PedidoReasignado, self._al_reasignar)
        bus.suscribir(PedidoEnRuta, self._al_iniciar_ruta)
        bus.suscribir(IntentoEntregaFallido, self._al_intento_fallido)
        bus.suscribir(PedidoEntregado, self._al_entregar)
        bus.suscribir(PedidoCancelado, self._al_cancelar)

    # ---- Handlers (Caso 5.c: registrar eventos + 5.b: notificar) ----
    def _al_crear(self, evento: PedidoCreado) -> None:
        seg = self._repo_seguimientos.obtener_o_crear(evento.pedido_id)
        seg.registrar("Creado", f"Pedido creado por canal {evento.canal}", "Creado")
        self._repo_seguimientos.guardar(seg)

    def _al_validar(self, evento: PedidoValidado) -> None:
        seg = self._repo_seguimientos.obtener_o_crear(evento.pedido_id)
        seg.registrar("Validado", "Pedido validado y pendiente de asignación", "PendienteAsignacion")
        self._repo_seguimientos.guardar(seg)
        self._notificar(evento.pedido_id, "Tu pedido fue validado y está listo para despacho")

    def _al_asignar(self, evento: PedidoAsignado) -> None:
        seg = self._repo_seguimientos.obtener_o_crear(evento.pedido_id)
        seg.registrar(
            "Asignado",
            f"Asignado al repartidor {evento.repartidor_id}",
            "Asignado",
        )
        self._repo_seguimientos.guardar(seg)
        self._notificar(evento.pedido_id, "Un repartidor fue asignado a tu pedido")

    def _al_reasignar(self, evento: PedidoReasignado) -> None:
        seg = self._repo_seguimientos.obtener_o_crear(evento.pedido_id)
        seg.registrar(
            "Reasignado",
            f"Reasignado de {evento.repartidor_anterior} a {evento.repartidor_nuevo}",
            "Asignado",
        )
        self._repo_seguimientos.guardar(seg)
        self._notificar(evento.pedido_id, "Tu pedido fue reasignado a otro repartidor")

    def _al_iniciar_ruta(self, evento: PedidoEnRuta) -> None:
        seg = self._repo_seguimientos.obtener_o_crear(evento.pedido_id)
        seg.registrar("EnRuta", "El repartidor inició el trayecto", "EnRuta")
        self._repo_seguimientos.guardar(seg)
        self._notificar(evento.pedido_id, "Tu pedido está en camino")

    def _al_intento_fallido(self, evento: IntentoEntregaFallido) -> None:
        seg = self._repo_seguimientos.obtener_o_crear(evento.pedido_id)
        seg.registrar(
            "IntentoFallido",
            f"Intento fallido: {evento.motivo}",
            "IntentoFallido",
        )
        self._repo_seguimientos.guardar(seg)
        self._notificar(evento.pedido_id, f"Intento de entrega fallido: {evento.motivo}")

    def _al_entregar(self, evento: PedidoEntregado) -> None:
        seg = self._repo_seguimientos.obtener_o_crear(evento.pedido_id)
        seg.registrar("Entregado", "Pedido entregado al destinatario", "Entregado")
        self._repo_seguimientos.guardar(seg)
        self._notificar(evento.pedido_id, "Tu pedido fue entregado. ¡Gracias!")

    def _al_cancelar(self, evento: PedidoCancelado) -> None:
        seg = self._repo_seguimientos.obtener_o_crear(evento.pedido_id)
        seg.registrar("Cancelado", "Pedido cancelado", "Cancelado")
        self._repo_seguimientos.guardar(seg)
        self._notificar(evento.pedido_id, "Tu pedido fue cancelado")

    # ---- Notificación (Caso 5.b) ----
    def _notificar(self, pedido_id: str, mensaje: str) -> None:
        pedido = self._repo_pedidos.obtener(pedido_id)
        if pedido is None:
            return
        destinatario = pedido.destinatario.medio_contacto
        for canal in self._canales:
            canal.enviar(destinatario, mensaje)

    # ---- Consulta (Caso 5.a) ----
    def visualizar_estado(self, pedido_id: str) -> dict:
        seg = self._repo_seguimientos.obtener(pedido_id)
        if seg is None:
            return {"pedido_id": pedido_id, "estado_actual": "sin seguimiento", "historial": []}
        return {
            "pedido_id": seg.pedido_id,
            "estado_actual": seg.estado_actual,
            "historial": [
                {
                    "tipo": e.tipo,
                    "descripcion": e.descripcion,
                    "timestamp": e.timestamp.isoformat(timespec="seconds"),
                }
                for e in seg.historial
            ],
        }
