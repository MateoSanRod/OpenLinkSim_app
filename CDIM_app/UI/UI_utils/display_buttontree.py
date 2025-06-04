from __future__ import annotations
from typing import Dict, Tuple, List
import numpy as np
from PySide6.QtCore import Qt, Signal, QSize, QSignalBlocker
from PySide6.QtGui import QPalette, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QWidget, QTreeView, QVBoxLayout

#  helpers
class _BoolItem(QStandardItem):
    def __init__(self, txt: str = "") -> None:
        super().__init__(txt)
        self.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        self.setCheckState(Qt.Unchecked)


class _TransparentView(QTreeView):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.viewport().setAttribute(Qt.WA_TranslucentBackground)
        pal = self.viewport().palette()
        pal.setColor(QPalette.Base, Qt.transparent)
        self.viewport().setPalette(pal)
        self.setStyleSheet("""
        QTreeView {
            background: transparent;
            border: 0;
        }
        QTreeView::item {
            padding: 1px 4px;
            color: #606060;
        }
        QTreeView::item:selected {
            background: #303030;
        }

        /* Scrollbar styling for QTreeView */
        QTreeView QScrollBar:vertical {
            background: #F3F3F3;
            width: 8px;
            margin: 0;
            border: none;
        }

        QTreeView QScrollBar::handle:vertical {
            background: #BDBDBD;
            border: none;
            min-height: 20px;
        }

        QTreeView QScrollBar::add-line:vertical,
        QTreeView QScrollBar::sub-line:vertical,
        QTreeView QScrollBar::up-arrow:vertical,
        QTreeView QScrollBar::down-arrow:vertical,
        QTreeView QScrollBar::add-page:vertical,
        QTreeView QScrollBar::sub-page:vertical {
            background: none;
            height: 0px;
        }

        QTreeView QScrollBar:horizontal {
            height: 8px;
            background: #303030;
            border: none;
        }

        QTreeView QScrollBar::handle:horizontal {
            background: #CCCCCC;
            border: none;
            min-width: 20px;
        }
        """)

        self.setUniformRowHeights(True)
        self.setIndentation(12)

    def sizeHint(self) -> QSize:
        vt = self.parentWidget()
        plot = vt.parentWidget() if vt else None

        if plot is not None:
            return QSize(125, plot.height()-10)
        return QSize(125, 400)

class VectorTree(QWidget):
    layerToggled = Signal(str, bool)
    nodeShown    = Signal(str, int, bool)
    cgShown      = Signal(str, int, bool)
    ptShown      = Signal(str, int, int, bool)

    def __init__(self,
                 n_nodes: int,
                 n_cg: int,
                 extra_layout: List[List] | None,
                 parent=None) -> None:
        super().__init__(parent)

        self._view  = _TransparentView(self)
        self._model = QStandardItemModel(0, 1, self)
        self._view.setHeaderHidden(True)
        self._view.setModel(self._model)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._view, alignment=Qt.AlignTop | Qt.AlignRight)

        self._layer_item: Dict[str, _BoolItem] = {}
        self._node_leaf : Dict[Tuple[str, int], _BoolItem] = {}
        self._cg_leaf   : Dict[Tuple[str, int], _BoolItem] = {}
        self._pt_leaf   : Dict[Tuple[str, int, int], _BoolItem] = {}

        self._add_layer("Paths"      , n_nodes, n_cg, extra_layout)
        self._add_layer("Velocity"   , n_nodes, n_cg, extra_layout)
        self._add_layer("Acceleration", n_nodes, n_cg, extra_layout)
        self._add_layer("Forces"     , n_nodes, 0    , [])

        self._model.itemChanged.connect(self._on_item_changed)

    def set_layer_state(self, layer: str, on: bool) -> None:
        self._layer_item[layer].setCheckState(Qt.Checked if on else Qt.Unchecked)

    def _add_layer(self, title: str, n_nodes: int, n_cg: int,
                   extra_layout: List[List] | None) -> None:
        root = _BoolItem(title)
        self._model.appendRow(root)
        self._layer_item[title] = root

        if n_nodes:
            branch = _BoolItem("nodes")
            branch.setAutoTristate(True)
            root.appendRow(branch)
            for i in range(n_nodes):
                leaf = _BoolItem(str(i + 1))
                branch.appendRow(leaf)
                self._node_leaf[(title, i)] = leaf

        if n_cg:
            branch = _BoolItem("cg")
            branch.setAutoTristate(True)
            root.appendRow(branch)
            for i in range(n_cg):
                leaf = _BoolItem(str(i + 1))
                branch.appendRow(leaf)
                self._cg_leaf[(title, i)] = leaf

        # extra points
        extr = self._to_py_list(extra_layout)
        if any(len(sub) for sub in extr):
            branch = _BoolItem("points")
            branch.setAutoTristate(True)
            root.appendRow(branch)
            for lnk_id, pts in enumerate(extr):
                if not len(pts):
                    continue
                hdr = _BoolItem(f"link {lnk_id + 1}")
                branch.appendRow(hdr)
                for pt_id, _ in enumerate(pts):
                    leaf = _BoolItem(str(pt_id + 1))
                    hdr.appendRow(leaf)
                    self._pt_leaf[(title, lnk_id, pt_id)] = leaf

    def _on_item_changed(self, it: _BoolItem):
        if not it.isCheckable():
            return

        if it.rowCount():
            self._cascade_down(it, it.checkState())

        self._propagate_up(it.parent())

        if it in self._layer_item.values():
            self.layerToggled.emit(it.text(), it.checkState() == Qt.Checked)
            return

        if not it.text().isdigit():
            self._emit_descendants(it)
            return

        self._emit_leaf(it)

    def _emit_leaf(self, leaf: _BoolItem) -> None:
        txt = leaf.text()
        state = leaf.checkState() == Qt.Checked

        for (lay, idx), node in self._node_leaf.items():
            if node is leaf:
                self.nodeShown.emit(lay, idx, state)
                return
        for (lay, idx), cg in self._cg_leaf.items():
            if cg is leaf:
                self.cgShown.emit(lay, idx, state)
                return
        for (lay, lnk, pt), p in self._pt_leaf.items():
            if p is leaf:
                self.ptShown.emit(lay, lnk, pt, state)
                return

    def _emit_descendants(self, parent: _BoolItem) -> None:
        stack = [parent]
        while stack:
            node = stack.pop()
            for r in range(node.rowCount()):
                ch = node.child(r)
                if ch.isCheckable():
                    if ch.rowCount():
                        stack.append(ch)
                    else:
                        self._emit_leaf(ch)

    @staticmethod
    def _to_py_list(seq):
        if seq is None:
            return []
        if isinstance(seq, np.ndarray) and seq.dtype == object:
            return list(seq)
        return seq

    def _cascade_down(self, parent: _BoolItem, state: int) -> None:
        stack = [parent]
        while stack:
            node = stack.pop()
            for r in range(node.rowCount()):
                ch = node.child(r)
                if ch.isCheckable():
                    with QSignalBlocker(self._model):
                        ch.setCheckState(state)
                stack.append(ch)

    def _propagate_up(self, node: _BoolItem | None) -> None:
        while node is not None:
            any_checked = any(
                node.child(r).checkState() == Qt.Checked
                for r in range(node.rowCount())
            )
            new_state = Qt.Checked if any_checked else Qt.Unchecked
            if node.checkState() != new_state:
                self._model.blockSignals(True)
                node.setCheckState(new_state)
                self._model.blockSignals(False)
            node = node.parent()
