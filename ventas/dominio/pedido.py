"""
Agregado raíz Pedido.

Contiene invariantes del dominio y delega el manejo de estados
al patrón State. Las transiciones válidas son las únicas formas
legítimas de modificar el estado del pedido.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from .value_objects import Direccion, Destinatario, Carga, VentanaEntrega, TipoEntrega, Canal
from .estados import EstadoPedido, Creado


class InformacionIncompleta(Exception):
    """Falta información mínima para validar el pedido."""
    pass


@dataclass
class Pedido:
    id: str
    canal: Canal
    origen_direccion: Direccion
    origen_punto_id: str
    destino_direccion: Direccion
    destinatario: Destinatario
    tipo_entrega: TipoEntrega
    carga: Carga
    ventana_entrega: Optional[VentanaEntrega] = None
    repartidor_id: Optional[str] = None
    _estado: EstadoPedido = field(default_factory=Creado)

    @property
    def estado(self) -> str:
        return self._estado.nombre

    # --- Transiciones (delegadas al State) ---
    def validar(self) -> None:
        self._estado.validar(self)

    def marcar_pendiente_asignacion(self) -> None:
        self._estado.marcar_pendiente_asignacion(self)

    def asignar_a(self, repartidor_id: str) -> None:
        self._estado.asignar(self)
        self.repartidor_id = repartidor_id

    def reasignar_a(self, nuevo_repartidor_id: str) -> None:
        # Asignado -> PendienteAsignacion -> Asignado
        self._estado.marcar_pendiente_asignacion(self)
        self._estado.asignar(self)
        self.repartidor_id = nuevo_repartidor_id

    def iniciar_ruta(self) -> None:
        self._estado.iniciar_ruta(self)

    def registrar_intento_fallido(self) -> None:
        self._estado.registrar_intento_fallido(self)

    def reprogramar(self) -> None:
        self._estado.reprogramar(self)

    def entregar(self) -> None:
        self._estado.entregar(self)

    def cancelar(self) -> None:
        self._estado.cancelar(self)

    # --- Invariantes del dominio ---
    def _verificar_informacion_minima(self) -> None:
        """
        Regla de negocio: un pedido solo puede validarse si tiene
        información mínima en todas las dimensiones.
        """
        faltantes = []
        if not self.origen_direccion.es_interpretable():
            faltantes.append("dirección de origen no interpretable")
        if not self.origen_punto_id.strip():
            faltantes.append("identificación del punto de origen")
        if not self.destino_direccion.es_interpretable():
            faltantes.append("dirección de destino no interpretable")
        if not self.destinatario.es_valido():
            faltantes.append("datos del destinatario")
        if not self.carga.es_valida():
            faltantes.append("tipo o peso de carga")
        if self.tipo_entrega == TipoEntrega.PROGRAMADA and self.ventana_entrega is None:
            faltantes.append("ventana de tiempo requerida para entrega programada")

        if faltantes:
            raise InformacionIncompleta(
                f"No se puede validar el pedido {self.id}: {', '.join(faltantes)}"
            )
