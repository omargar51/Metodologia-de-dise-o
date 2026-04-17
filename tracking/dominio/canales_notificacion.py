"""
Canales de notificación al cliente.

Patrón Strategy: distintas formas de notificar (email, SMS, push, consola).
Cumple OCP e ISP: agregar un canal = nueva clase, sin tocar nada.
"""
from __future__ import annotations
from abc import ABC, abstractmethod


class ICanalNotificacion(ABC):
    @abstractmethod
    def enviar(self, destinatario: str, mensaje: str) -> None: ...


class CanalConsola(ICanalNotificacion):
    """Canal de notificación que imprime por consola (útil para la demo)."""
    def enviar(self, destinatario: str, mensaje: str) -> None:
        print(f"   📨 [Notificación → {destinatario}] {mensaje}")


class CanalEmailFake(ICanalNotificacion):
    """Simula envío por email sin dependencias externas."""
    def __init__(self) -> None:
        self.enviados: list[tuple[str, str]] = []

    def enviar(self, destinatario: str, mensaje: str) -> None:
        self.enviados.append((destinatario, mensaje))
        print(f"   ✉️  [Email → {destinatario}] {mensaje}")


class CanalSMSFake(ICanalNotificacion):
    """Simula envío por SMS sin dependencias externas."""
    def __init__(self) -> None:
        self.enviados: list[tuple[str, str]] = []

    def enviar(self, destinatario: str, mensaje: str) -> None:
        self.enviados.append((destinatario, mensaje))
        print(f"   📱 [SMS → {destinatario}] {mensaje}")
