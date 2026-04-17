"""
Caso de uso 2: Gestión de Repartidores
  a. Registrar repartidores
  b. Gestionar disponibilidad
  c. Asignar pedidos (con Strategy)
  d. Monitorear ubicación

El servicio de asignación depende de:
  - IRepositorioRepartidores (DIP)
  - IRepositorioPedidos (DIP, cross-context pero desde la capa de aplicación)
  - IEstrategiaAsignacion (Strategy, inyectable)
  - BusEventos (Observer / Published Language)
"""
from __future__ import annotations
from ..dominio.repartidor import Repartidor
from ..dominio.estrategias_asignacion import IEstrategiaAsignacion
from ..infraestructura.repositorio import IRepositorioRepartidores
from ventas.infraestructura.repositorio import IRepositorioPedidos
from compartido.eventos import BusEventos, PedidoAsignado, PedidoReasignado


class NoHayRepartidoresDisponibles(Exception):
    pass


class ServicioRepartidores:
    def __init__(
        self,
        repo_repartidores: IRepositorioRepartidores,
        repo_pedidos: IRepositorioPedidos,
        estrategia: IEstrategiaAsignacion,
        bus: BusEventos,
    ) -> None:
        self._repo_repartidores = repo_repartidores
        self._repo_pedidos = repo_pedidos
        self._estrategia = estrategia
        self._bus = bus

    # Caso 2.a — Registrar repartidor
    def registrar_repartidor(
        self, id_: str, nombre: str, capacidad: int
    ) -> str:
        repartidor = Repartidor(id=id_, nombre=nombre, capacidad_maxima=capacidad)
        self._repo_repartidores.guardar(repartidor)
        return repartidor.id

    # Caso 2.b — Gestionar disponibilidad
    def marcar_disponible(self, repartidor_id: str) -> None:
        repartidor = self._repo_repartidores.obtener(repartidor_id)
        if repartidor is None:
            raise ValueError(f"Repartidor {repartidor_id} no existe")
        repartidor.marcar_disponible()
        self._repo_repartidores.guardar(repartidor)

    def marcar_no_disponible(self, repartidor_id: str) -> None:
        repartidor = self._repo_repartidores.obtener(repartidor_id)
        if repartidor is None:
            raise ValueError(f"Repartidor {repartidor_id} no existe")
        repartidor.marcar_no_disponible()
        self._repo_repartidores.guardar(repartidor)

    # Caso 2.c — Asignar pedido (automático via Strategy)
    def asignar_pedido(self, pedido_id: str) -> str:
        pedido = self._repo_pedidos.obtener(pedido_id)
        if pedido is None:
            raise ValueError(f"Pedido {pedido_id} no existe")

        disponibles = self._repo_repartidores.listar_disponibles()
        elegido = self._estrategia.elegir(disponibles)
        if elegido is None:
            raise NoHayRepartidoresDisponibles(
                "Ningún repartidor con capacidad disponible"
            )

        elegido.asignar_pedido(pedido_id)
        pedido.asignar_a(elegido.id)

        self._repo_repartidores.guardar(elegido)
        self._repo_pedidos.guardar(pedido)

        self._bus.publicar(PedidoAsignado(
            pedido_id=pedido_id, repartidor_id=elegido.id,
        ))
        return elegido.id

    # Caso 2.c (variante) — Re-asignación
    def reasignar_pedido(self, pedido_id: str) -> str:
        pedido = self._repo_pedidos.obtener(pedido_id)
        if pedido is None:
            raise ValueError(f"Pedido {pedido_id} no existe")
        if pedido.repartidor_id is None:
            raise ValueError(f"Pedido {pedido_id} no estaba asignado")

        repartidor_anterior = self._repo_repartidores.obtener(pedido.repartidor_id)
        if repartidor_anterior is not None:
            repartidor_anterior.liberar_pedido(pedido_id)
            self._repo_repartidores.guardar(repartidor_anterior)

        disponibles = [
            r for r in self._repo_repartidores.listar_disponibles()
            if r.id != pedido.repartidor_id
        ]
        nuevo = self._estrategia.elegir(disponibles)
        if nuevo is None:
            raise NoHayRepartidoresDisponibles(
                "No hay otro repartidor disponible para reasignar"
            )

        id_anterior = pedido.repartidor_id
        nuevo.asignar_pedido(pedido_id)
        pedido.reasignar_a(nuevo.id)

        self._repo_repartidores.guardar(nuevo)
        self._repo_pedidos.guardar(pedido)

        self._bus.publicar(PedidoReasignado(
            pedido_id=pedido_id,
            repartidor_anterior=id_anterior,
            repartidor_nuevo=nuevo.id,
        ))
        return nuevo.id

    # Caso 2.d — Monitorear ubicación
    def actualizar_ubicacion(
        self, repartidor_id: str, lat: float, lon: float
    ) -> None:
        repartidor = self._repo_repartidores.obtener(repartidor_id)
        if repartidor is None:
            raise ValueError(f"Repartidor {repartidor_id} no existe")
        repartidor.actualizar_ubicacion(lat, lon)
        self._repo_repartidores.guardar(repartidor)

    def consultar_ubicacion(self, repartidor_id: str) -> tuple[float, float]:
        repartidor = self._repo_repartidores.obtener(repartidor_id)
        if repartidor is None:
            raise ValueError(f"Repartidor {repartidor_id} no existe")
        return repartidor.ubicacion_actual

    def cambiar_estrategia(self, estrategia: IEstrategiaAsignacion) -> None:
        """Permite cambiar la estrategia en runtime (OCP / Strategy)."""
        self._estrategia = estrategia
