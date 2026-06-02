"""Application-wide dependency-injection container.

A single Injector wires Settings -> Components -> Services using constructor
type hints. Routers fetch services from `request.state.injector`, which keeps
the HTTP layer ignorant of how components are constructed.
"""

from __future__ import annotations

from injector import Injector

from hexrag.settings.models import Settings, unsafe_typed_settings


def create_injector() -> Injector:
    injector = Injector(auto_bind=True)
    injector.binder.bind(Settings, to=unsafe_typed_settings)
    return injector


# Avoid importing this directly in components; use the request-scoped injector
# (request.state.injector) so code stays testable.
global_injector: Injector = create_injector()
