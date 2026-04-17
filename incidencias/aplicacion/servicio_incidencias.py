"""
Caso de uso 6: Gestión de Incidencias
  a. Registrar reclamos
  b. Gestionar casos (analizar, pasar a resolución)
  c. Resolver incidencias (con posible acción sobre el pedido)

Reglas de negocio implementadas:
- Toda incidencia debe estar asociada a un pedido existente
- Un pedido entregado puede generar una incidencia (reclamo)
- Una incidencia no puede cerrarse sin resolución (invariante del estado EnResolucion)
- Una incidencia resuelta puede gatillar acciones sobre el pedido

Publica eventos (Published Language) para que otros contextos reaccionen.
"""
from __future__ import annotations
from ..dominio.incidencia import Incidencia, TipoIncidencia, generar_id_incidencia
from ..infraestructura.repositorio import IRepositorioIncidencias
from ventas.infraestructura.repositorio import IRepositorioPedidos
from compartido.eventos import (
    BusEventos, IncidenciaAbierta, IncidenciaResuelta,
)


class PedidoInexistente(Exception):
    pass


class ServicioIncidencias:
    def __init__(
        self,
        repo_incidencias: IRepositorioIncidencias,
        repo_pedidos: IRepositorioPedidos,
        bus: BusEventos,
    ) -> None:
        self._repo = repo_incidencias
        self._repo_pedidos = repo_pedidos
        self._bus = bus

    # Caso 6.a — Registrar reclamo / incidencia
    def registrar_incidencia(
        self,
        pedido_id: str,
        tipo: TipoIncidencia,
        descripcion: str,
    ) -> str:
        # Invariante: la incidencia debe estar asociada a un pedido existente
        pedido = self._repo_pedidos.obtener(pedido_id)
        if pedido is None:
            raise PedidoInexistente(
                f"No se puede registrar incidencia: pedido {pedido_id} no existe"
            )

        incidencia = Incidencia(
            id=generar_id_incidencia(),
            pedido_id=pedido_id,
            tipo=tipo,
            descripcion=descripcion,
        )
        self._repo.guardar(incidencia)
        self._bus.publicar(IncidenciaAbierta(
            incidencia_id=incidencia.id,
            pedido_id=pedido_id,
            tipo=tipo.value,
        ))
        return incidencia.id

    # Caso 6.b — Gestionar casos: analizar
    def analizar(self, incidencia_id: str) -> None:
        incidencia = self._obtener_o_error(incidencia_id)
        incidencia.analizar()
        self._repo.guardar(incidencia)

    # Caso 6.b — Gestionar casos: pasar a resolución
    def pasar_a_resolucion(
        self, incidencia_id: str, resolucion: str, accion_sobre_pedido: str = ""
    ) -> None:
        incidencia = self._obtener_o_error(incidencia_id)
        incidencia.pasar_a_resolucion(resolucion, accion_sobre_pedido)
        self._repo.guardar(incidencia)

    # Caso 6.c — Resolver incidencia
    def resolver(self, incidencia_id: str) -> str:
        incidencia = self._obtener_o_error(incidencia_id)
        incidencia.cerrar()
        self._repo.guardar(incidencia)

        self._bus.publicar(IncidenciaResuelta(
            incidencia_id=incidencia.id,
            pedido_id=incidencia.pedido_id,
        ))
        return incidencia.accion_sobre_pedido

    def listar_por_pedido(self, pedido_id: str) -> list[dict]:
        return [
            {
                "id": i.id,
                "tipo": i.tipo.value,
                "estado": i.estado,
                "descripcion": i.descripcion,
                "resolucion": i.resolucion_propuesta,
            }
            for i in self._repo.listar_por_pedido(pedido_id)
        ]

    def _obtener_o_error(self, incidencia_id: str) -> Incidencia:
        incidencia = self._repo.obtener(incidencia_id)
        if incidencia is None:
            raise ValueError(f"Incidencia {incidencia_id} no existe")
        return incidencia
