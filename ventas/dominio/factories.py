"""
Factory Method + Adapter para creación de pedidos desde distintos canales.

Cada canal (ecommerce, comercio aliado, canal propio) trae datos en
formato diferente (diccionarios con distintas claves). Las factories:
  - Actúan como Adapter: traducen el formato externo al modelo de dominio
  - Usan Factory Method: cada subclase define cómo construir el Pedido
  - Cumplen OCP: agregar un canal nuevo = crear una clase nueva sin tocar las existentes
  - Cumplen SRP: cada factory solo sabe traducir SU canal
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
import uuid
from .pedido import Pedido
from .value_objects import (
    Direccion, Destinatario, Carga, VentanaEntrega, TipoEntrega, Canal
)


class PedidoFactory(ABC):
    """Factory Method abstracto: define el esqueleto de creación."""

    @abstractmethod
    def crear(self, datos_crudos: dict[str, Any]) -> Pedido: ...

    def _generar_id(self) -> str:
        return f"PED-{uuid.uuid4().hex[:8].upper()}"


class PedidoFactoryEcommerce(PedidoFactory):
    """
    Adapta datos de plataformas ecommerce (formato típico con order_id,
    shipping_address, customer, etc.)
    """
    def crear(self, datos_crudos: dict[str, Any]) -> Pedido:
        shipping = datos_crudos["shipping_address"]
        warehouse = datos_crudos["warehouse"]
        customer = datos_crudos["customer"]
        item = datos_crudos["item"]

        return Pedido(
            id=self._generar_id(),
            canal=Canal.ECOMMERCE,
            origen_direccion=Direccion(
                calle=warehouse["street"],
                numero=warehouse["number"],
                ciudad=warehouse["city"],
            ),
            origen_punto_id=warehouse["id"],
            destino_direccion=Direccion(
                calle=shipping["street"],
                numero=shipping["number"],
                ciudad=shipping["city"],
                referencia=shipping.get("notes", ""),
            ),
            destinatario=Destinatario(
                nombre=customer["name"],
                medio_contacto=customer["email"],
            ),
            tipo_entrega=TipoEntrega(datos_crudos.get("delivery_type", "normal")),
            carga=Carga(tipo=item["type"], peso_kg=item["weight_kg"]),
        )


class PedidoFactoryComercio(PedidoFactory):
    """Adapta datos de comercios aliados (formato más plano)."""
    def crear(self, datos_crudos: dict[str, Any]) -> Pedido:
        ventana = None
        if datos_crudos.get("tipo_entrega") == "programada":
            ventana = VentanaEntrega(
                desde=datos_crudos["hora_desde"],
                hasta=datos_crudos["hora_hasta"],
            )

        return Pedido(
            id=self._generar_id(),
            canal=Canal.COMERCIO,
            origen_direccion=Direccion(
                calle=datos_crudos["origen_calle"],
                numero=datos_crudos["origen_numero"],
                ciudad=datos_crudos["origen_ciudad"],
            ),
            origen_punto_id=datos_crudos["sucursal_id"],
            destino_direccion=Direccion(
                calle=datos_crudos["destino_calle"],
                numero=datos_crudos["destino_numero"],
                ciudad=datos_crudos["destino_ciudad"],
            ),
            destinatario=Destinatario(
                nombre=datos_crudos["cliente_nombre"],
                medio_contacto=datos_crudos["cliente_telefono"],
            ),
            tipo_entrega=TipoEntrega(datos_crudos.get("tipo_entrega", "normal")),
            carga=Carga(
                tipo=datos_crudos["carga_tipo"],
                peso_kg=datos_crudos["carga_peso"],
            ),
            ventana_entrega=ventana,
        )


class PedidoFactoryPropio(PedidoFactory):
    """Canal propio de la empresa (ya usa el lenguaje del dominio)."""
    def crear(self, datos_crudos: dict[str, Any]) -> Pedido:
        return Pedido(
            id=self._generar_id(),
            canal=Canal.PROPIO,
            origen_direccion=datos_crudos["origen_direccion"],
            origen_punto_id=datos_crudos["origen_punto_id"],
            destino_direccion=datos_crudos["destino_direccion"],
            destinatario=datos_crudos["destinatario"],
            tipo_entrega=datos_crudos["tipo_entrega"],
            carga=datos_crudos["carga"],
            ventana_entrega=datos_crudos.get("ventana_entrega"),
        )


class RegistroFactoriesPedido:
    """
    Registro que despacha según el canal.
    Permite agregar canales nuevos sin modificar este código (OCP).
    """
    def __init__(self) -> None:
        self._factories: dict[Canal, PedidoFactory] = {}

    def registrar(self, canal: Canal, factory: PedidoFactory) -> None:
        self._factories[canal] = factory

    def obtener(self, canal: Canal) -> PedidoFactory:
        if canal not in self._factories:
            raise ValueError(f"No hay factory registrada para el canal {canal}")
        return self._factories[canal]
