"""Soft-cancel flag for long-running fits (Layer 1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Event


@dataclass
class CancelToken:
    """Cooperative cancel: check ``is_cancelled`` inside loops."""

    _event: Event = field(default_factory=Event)

    def cancel(self) -> None:
        self._event.set()

    def reset(self) -> None:
        self._event.clear()

    @property
    def is_cancelled(self) -> bool:
        return self._event.is_set()
