from __future__ import annotations

import numpy as np
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QObject
from PySide6.QtWidgets import QPushButton, QSplitter


class SplitterToggle(QPushButton):
    DURATION_MS = 180
    EASE = QEasingCurve.OutCubic

    def __init__(self,
                 app,
                 button: QPushButton,
                 side: str | int = "left",
                 *,
                 min_fraction: float = .15,
                 duration_ms : int   = 180,
                 easing      : QEasingCurve.Type = QEasingCurve.OutCubic) -> None:
        super().__init__()
        self.splitter = app.ui.splitter
        self.button = button
        self.side_idx      = self._norm_side(side)
        self.min_fraction  = float(np.clip(min_fraction, 0.01, .8))
        self.duration_ms   = duration_ms
        self.easing        = easing
        self._backup_sizes = None
        self._anim = None
        self._backup: np.ndarray | None = None
        self._anim   = None

        self.button.clicked.connect(self._toggle)
    def _norm_side(self, side) -> int:
        if isinstance(side, int):
            if not (0 <= side < self.splitter.count()):
                raise IndexError("Splitter section index out of range")
            return side
        side = str(side).lower()
        if side.startswith("l"):
            return 0
        if side.startswith("r"):
            return self.splitter.count() - 1
        raise ValueError(f"Unknown side value {side!r}")

    def _cur_sizes(self) -> np.ndarray:
        return np.asarray(self.splitter.sizes(), dtype=float)

    def _set_sizes(self, arr: np.ndarray):
        arr = np.maximum(0, np.asarray(arr, dtype=int))
        self.splitter.setSizes(arr.tolist())

    def _animate_to(self, target: np.ndarray):
        if self._anim and self._anim.state():
            self._anim.stop()
        self._anim = QPropertyAnimation(self.splitter, b"sizes", self)
        self._anim.setStartValue(self._cur_sizes().tolist())
        self._anim.setEndValue  (np.maximum(0, target).astype(int).tolist())
        self._anim.setDuration(self.duration_ms)
        self._anim.setEasingCurve(self.easing)
        self._anim.start()

    def _redistribute(self, sizes: np.ndarray, delta: float, skip: int) -> None:
        idx = [i for i in range(len(sizes)) if i != skip and sizes[i] > 0]
        if not idx:
            return
        pool = sizes[idx].sum()
        if pool == 0:
            return
        factor = delta / pool
        sizes[idx] += sizes[idx] * factor

    def _toggle(self):
        sizes = self._cur_sizes()
        my_w = sizes[self.side_idx]

        if my_w > 1:
            self._backup_sizes = my_w
            freed = my_w
            sizes[self.side_idx] = 0
            self._redistribute(sizes, +freed, self.side_idx)

        else:
            target = (self._backup_sizes
                      if self._backup_sizes and self._backup_sizes > 1
                      else max(1, sizes.sum() * self.min_fraction))

            inc = target - my_w
            inc = min(inc, sizes.sum() - my_w)
            sizes[self.side_idx] += inc
            self._redistribute(sizes, -inc, self.side_idx)

        self._set_sizes(sizes)
