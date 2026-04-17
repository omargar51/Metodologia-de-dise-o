"""
Agregado Repartidor (contexto Operaciones).

Invariantes:
- No puede aceptar pedidos si no está disponible
- No puede superar su capacidad
- Puede manejar múltiples pedidos simultáneamente
"""
from __future__ import annotations
from dataclasses import dataclass, field


class CapacidadExcedida(Exception):
    pass


class RepartidorNoDisponible(Exception):
    pass


@dataclass
class Repartidor:
    id: str
    nombre: str
    capacidad_maxima: int
    disponible: bool = True
    pedidos_asignados: list[str] = field(default_factory=list)
    ubicacion_actual: tuple[float, float] = (0.0, 0.0)  # (lat, lon) simplificado

    def puede_aceptar_pedido(self) -> bool:
        return self.disponible and len(self.pedidos_asignados) < self.capacidad_maxima

    def asignar_pedido(self, pedido_id: str) -> None:
        if not self.disponible:
            raise RepartidorNoDisponible(f"Repartidor {self.id} no disponible")
        if len(self.pedidos_asignados) >= self.capacidad_maxima:
            raise CapacidadExcedida(
                f"Repartidor {self.id} alcanzó su capacidad máxima ({self.capacidad_maxima})"
            )
        self.pedidos_asignados.append(pedido_id)

    def liberar_pedido(self, pedido_id: str) -> None:
        if pedido_id in self.pedidos_asignados:
            self.pedidos_asignados.remove(pedido_id)

    def marcar_no_disponible(self) -> None:
        self.disponible = False

    def marcar_disponible(self) -> None:
        self.disponible = True

    def actualizar_ubicacion(self, lat: float, lon: float) -> None:
        self.ubicacion_actual = (lat, lon)

    def carga_actual(self) -> int:
        return len(self.pedidos_asignados)
