"""
=============================================================================
  DEMO — Arquitectura DDD de logística de última milla
  4 casos de uso implementados: Pedidos, Repartidores, Tracking, Incidencias
=============================================================================
"""
from __future__ import annotations

# --- Compartido ---
from compartido.eventos import BusEventos

# --- Ventas ---
from ventas.dominio.value_objects import Canal
from ventas.dominio.factories import (
    RegistroFactoriesPedido,
    PedidoFactoryEcommerce,
    PedidoFactoryComercio,
    PedidoFactoryPropio,
)
from ventas.infraestructura.repositorio import RepositorioPedidosEnMemoria
from ventas.aplicacion.servicio_pedidos import ServicioPedidos

# --- Operaciones ---
from operaciones.dominio.estrategias_asignacion import (
    EstrategiaMenorCarga, EstrategiaRoundRobin,
)
from operaciones.infraestructura.repositorio import RepositorioRepartidoresEnMemoria
from operaciones.aplicacion.servicio_repartidores import ServicioRepartidores

# --- Tracking ---
from tracking.dominio.canales_notificacion import CanalConsola, CanalEmailFake
from tracking.infraestructura.repositorio import RepositorioSeguimientosEnMemoria
from tracking.aplicacion.servicio_tracking import ServicioTracking

# --- Incidencias ---
from incidencias.dominio.incidencia import TipoIncidencia
from incidencias.infraestructura.repositorio import RepositorioIncidenciasEnMemoria
from incidencias.aplicacion.servicio_incidencias import ServicioIncidencias


def separador(titulo: str) -> None:
    print("\n" + "═" * 75)
    print(f"  {titulo}")
    print("═" * 75)


def wire_up():
    """
    Composición raíz (Composition Root).
    Todas las dependencias concretas se inyectan aquí,
    materializando el DIP: el resto del código depende solo de abstracciones.
    """
    bus = BusEventos()

    # Ventas
    repo_pedidos = RepositorioPedidosEnMemoria()
    factories = RegistroFactoriesPedido()
    factories.registrar(Canal.ECOMMERCE, PedidoFactoryEcommerce())
    factories.registrar(Canal.COMERCIO, PedidoFactoryComercio())
    factories.registrar(Canal.PROPIO, PedidoFactoryPropio())
    srv_pedidos = ServicioPedidos(factories, repo_pedidos, bus)

    # Operaciones
    repo_repartidores = RepositorioRepartidoresEnMemoria()
    srv_repartidores = ServicioRepartidores(
        repo_repartidores, repo_pedidos,
        EstrategiaMenorCarga(),  # Strategy inyectada
        bus,
    )

    # Tracking (se auto-suscribe a los eventos del bus)
    repo_seguimientos = RepositorioSeguimientosEnMemoria()
    canales = [CanalConsola(), CanalEmailFake()]
    ServicioTracking(repo_seguimientos, repo_pedidos, canales, bus)

    # Incidencias
    repo_incidencias = RepositorioIncidenciasEnMemoria()
    srv_incidencias = ServicioIncidencias(repo_incidencias, repo_pedidos, bus)

    return srv_pedidos, srv_repartidores, srv_incidencias, repo_seguimientos


def main() -> None:
    srv_pedidos, srv_repartidores, srv_incidencias, repo_seguimientos = wire_up()

    # =========================================================================
    # CASO DE USO 1 — GESTIÓN DE PEDIDOS
    # =========================================================================
    separador("CASO 1 — Gestión de Pedidos (crear desde canales + validar + estados)")

    # 1.a Crear pedidos desde distintos canales (Factory Method + Adapter)
    datos_ecommerce = {
        "shipping_address": {
            "street": "Av. Libertad", "number": "1234",
            "city": "Viña del Mar", "notes": "Depto 502",
        },
        "warehouse": {
            "id": "WH-001", "street": "Ruta 68", "number": "km 12",
            "city": "Valparaíso",
        },
        "customer": {"name": "María Pérez", "email": "maria@example.cl"},
        "item": {"type": "electrónica", "weight_kg": 2.5},
        "delivery_type": "express",
    }
    id1 = srv_pedidos.crear_pedido(Canal.ECOMMERCE, datos_ecommerce)
    print(f"✅ Pedido ecommerce creado: {id1}")

    datos_comercio = {
        "origen_calle": "Calle Condell", "origen_numero": "1700",
        "origen_ciudad": "Valparaíso",
        "sucursal_id": "SUC-42",
        "destino_calle": "Av. Marina", "destino_numero": "890",
        "destino_ciudad": "Viña del Mar",
        "cliente_nombre": "Carlos Soto",
        "cliente_telefono": "+56 9 1234 5678",
        "tipo_entrega": "normal",
        "carga_tipo": "ropa", "carga_peso": 1.0,
    }
    id2 = srv_pedidos.crear_pedido(Canal.COMERCIO, datos_comercio)
    print(f"✅ Pedido comercio creado:  {id2}")

    # 1.b Validar información
    srv_pedidos.validar_pedido(id1)
    srv_pedidos.validar_pedido(id2)
    print(f"✅ Ambos pedidos validados → estado: {srv_pedidos.consultar_estado(id1)}")

    # 1.c Gestionar estados — intentar transición inválida
    print("\n→ Probando transición inválida (entregar sin asignar):")
    try:
        from ventas.dominio.estados import TransicionInvalida
        # El pedido está en PendienteAsignacion, no puede ser entregado
        from ventas.infraestructura.repositorio import RepositorioPedidosEnMemoria  # noqa
        # Accedemos vía repo para probar la regla (la demo sigue siendo válida)
        # Aquí simplemente llamamos un método incompatible y capturamos
        pedido = srv_pedidos._repositorio.obtener(id1)
        pedido.entregar()
    except Exception as e:
        print(f"   ✋ Bloqueado por la regla de dominio: {e}")

    # =========================================================================
    # CASO DE USO 2 — GESTIÓN DE REPARTIDORES
    # =========================================================================
    separador("CASO 2 — Gestión de Repartidores (registrar + disponibilidad + asignar + ubicación)")

    # 2.a Registrar repartidores
    srv_repartidores.registrar_repartidor("REP-01", "Juan Gómez", capacidad=3)
    srv_repartidores.registrar_repartidor("REP-02", "Ana López",  capacidad=2)
    srv_repartidores.registrar_repartidor("REP-03", "Luis Vera",  capacidad=2)
    print("✅ 3 repartidores registrados")

    # 2.b Gestionar disponibilidad
    srv_repartidores.marcar_no_disponible("REP-03")
    print("✅ REP-03 marcado como no disponible (en descanso)")

    # 2.d Monitorear ubicación
    srv_repartidores.actualizar_ubicacion("REP-01", -33.04, -71.63)
    srv_repartidores.actualizar_ubicacion("REP-02", -33.02, -71.55)
    lat, lon = srv_repartidores.consultar_ubicacion("REP-01")
    print(f"✅ Ubicación REP-01: ({lat}, {lon})")

    # 2.c Asignación automática con Strategy
    print("\n→ Asignación automática (estrategia: MenorCarga)")
    rep_asignado_1 = srv_repartidores.asignar_pedido(id1)
    rep_asignado_2 = srv_repartidores.asignar_pedido(id2)
    print(f"   Pedido {id1} → {rep_asignado_1}")
    print(f"   Pedido {id2} → {rep_asignado_2}")

    # 2.c Re-asignación
    print(f"\n→ Re-asignación del pedido {id1} (simulando problema con repartidor)")
    nuevo_rep = srv_repartidores.reasignar_pedido(id1)
    print(f"   Pedido {id1} reasignado a {nuevo_rep}")

    # Cambiar estrategia en runtime (demuestra Strategy)
    print("\n→ Cambiando estrategia a RoundRobin en runtime (OCP/Strategy)")
    srv_repartidores.cambiar_estrategia(EstrategiaRoundRobin())
    print("   ✅ Estrategia cambiada sin modificar código existente")

    # =========================================================================
    # CASO DE USO 5 — MONITOREO Y TRACKING
    # =========================================================================
    separador("CASO 5 — Monitoreo y Tracking (visualizar + notificar + eventos)")

    # Simulamos el resto del flujo del pedido id1 para enriquecer el tracking
    from compartido.eventos import PedidoEnRuta, PedidoEntregado
    pedido_1 = srv_pedidos._repositorio.obtener(id1)
    pedido_1.iniciar_ruta()
    srv_pedidos._repositorio.guardar(pedido_1)
    srv_pedidos._bus.publicar(PedidoEnRuta(pedido_id=id1))

    pedido_1.entregar()
    srv_pedidos._repositorio.guardar(pedido_1)
    srv_pedidos._bus.publicar(PedidoEntregado(pedido_id=id1))

    # 5.a Visualizar estados y 5.c ver eventos registrados
    print(f"\n→ Historial de tracking del pedido {id1}:")
    estado = repo_seguimientos.obtener(id1)
    print(f"   Estado actual: {estado.estado_actual}")
    print(f"   Eventos registrados ({len(estado.historial)}):")
    for i, evt in enumerate(estado.historial, 1):
        print(f"     {i}. [{evt.tipo}] {evt.descripcion}")

    # =========================================================================
    # CASO DE USO 6 — GESTIÓN DE INCIDENCIAS
    # =========================================================================
    separador("CASO 6 — Gestión de Incidencias (registrar + gestionar + resolver)")

    # 6.a Registrar reclamo sobre un pedido YA ENTREGADO
    # Regla de negocio: un pedido entregado puede generar una incidencia
    print(f"\n→ El cliente del pedido {id1} reclama que NO recibió el producto")
    inc_id = srv_incidencias.registrar_incidencia(
        pedido_id=id1,
        tipo=TipoIncidencia.RECLAMO_NO_RECIBIDO,
        descripcion="Cliente indica que no recibió el paquete pese a estar marcado como entregado",
    )
    print(f"   ✅ Incidencia abierta: {inc_id}")

    # Probar regla: no puede cerrarse sin pasar por el flujo
    print("\n→ Probando regla: no se puede cerrar sin resolución (desde Abierta)")
    try:
        srv_incidencias.resolver(inc_id)
    except Exception as e:
        print(f"   ✋ Bloqueado por invariante del dominio: {e}")

    # 6.b Gestionar caso: analizar → pasar a resolución
    print("\n→ Gestionando el caso (flujo completo)")
    srv_incidencias.analizar(inc_id)
    print("   → Incidencia en análisis")
    srv_incidencias.pasar_a_resolucion(
        inc_id,
        resolucion="Se compensa al cliente con reenvío del producto",
        accion_sobre_pedido="generar_nuevo_envio",
    )
    print("   → Resolución propuesta registrada")

    # Probar: no se puede cerrar sin resolución (reintentar desde Abierta hipotética)
    # Aquí ya hay resolución, así que se puede cerrar:
    accion = srv_incidencias.resolver(inc_id)
    print(f"   ✅ Incidencia resuelta. Acción disparada sobre pedido: '{accion}'")

    # Listar incidencias del pedido
    print(f"\n→ Incidencias asociadas al pedido {id1}:")
    for inc in srv_incidencias.listar_por_pedido(id1):
        print(f"   • {inc['id']} [{inc['estado']}] - {inc['tipo']}")
        print(f"     Descripción: {inc['descripcion']}")
        print(f"     Resolución:  {inc['resolucion']}")

    # =========================================================================
    separador("✨ DEMO COMPLETADA — Los 4 casos de uso se ejecutaron correctamente")


if __name__ == "__main__":
    main()
