from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QPainter, QPixmap, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QSizePolicy,
    QToolButton,
    QPushButton,
    QLabel,
    QSplitter,
    QScrollArea,
    QFrame,
)


@dataclass
class _Series:
    name: str
    values: np.ndarray


class GraphPanel(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.app = parent  # Main window reference for polling current frame
        self._series: Dict[str, _Series] = {}
        self._series_order: List[str] = []
        self._link_pt_map: List[Tuple[int, int]] | None = None
        self.series_colors: Dict[str, str] = {}
        self._sections: List["GraphSection"] = []
        self.add_button: QPushButton | None = None
        self.remove_button: QPushButton | None = None
        self._last_frames: List[dict] | None = None
        self._last_delta_time: float | None = None
        self._cursor_idx: int | None = None
        self._last_polled_frame: int | None = None
        self._needs_render = False

        # Lightweight polling to move the cursor line without touching OpenGL code
        self._cursor_timer = QTimer(self)
        self._cursor_timer.setInterval(42)  # ~24 FPS
        self._cursor_timer.timeout.connect(self._poll_cursor)
        self._cursor_timer.start()

        self.colors = {
            "face": "#2c2c2c",
            "spine": "#808080",
            "ticks": "#dcdcdc",
            "grid": "#444444",
            "text": "#dcdcdc",
            "line": "#59b8ff",
        }
        self.font_sizes = {"tick": 8, "label": 8}
        self.height_scale = 1.0

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(4)
        self.root_layout.setAlignment(Qt.AlignTop)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.root_layout.addWidget(self.scroll_area, 1)

        self.splitter = QSplitter(Qt.Vertical, self)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(2)
        self.splitter_container = QWidget()
        self.splitter_layout = QVBoxLayout(self.splitter_container)
        self.splitter_layout.setContentsMargins(0, 0, 0, 0)
        self.splitter_layout.setSpacing(0)
        self.splitter_layout.addWidget(self.splitter)
        self.scroll_area.setWidget(self.splitter_container)

        # Add initial graph section
        self._add_section()

        controls_row = QHBoxLayout()
        controls_row.setContentsMargins(0, 0, 0, 0)
        controls_row.setSpacing(6)

        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(32, 32)
        self.add_button.clicked.connect(lambda: self._add_section(copy_state=True))

        self.remove_button = QPushButton("\u2212")
        self.remove_button.setFixedSize(32, 32)
        self.remove_button.clicked.connect(self._remove_last_section)

        controls_row.addWidget(self.add_button)
        controls_row.addWidget(self.remove_button)
        controls_row.addStretch(1)
        self.root_layout.addLayout(controls_row, 0)
        self._update_remove_enabled()
        self._rebalance_splitter()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def load_from_simulation(self, frames: List[dict], delta_time: float) -> None:
        if not frames:
            self._series.clear()
            self._series_order.clear()
            self._show_empty_message()
            return

        self._series.clear()
        self._series_order.clear()
        self._link_pt_map = None
        delta_time = float(delta_time) if delta_time else 0.0
        time_axis = np.arange(len(frames)) * (delta_time if delta_time > 0 else 1.0)
        self._add_series("Time", time_axis)

        first = frames[0]
        if "link_extra_points_per_link" in first:
            self._link_pt_map = [
                (lnk_id, pt_id)
                for lnk_id, pts in enumerate(first["link_extra_points_per_link"])
                for pt_id, _ in enumerate(pts)
            ]

        self._gather_node_series(frames)
        self._gather_cg_series(frames)
        self._gather_link_point_series(frames)
        self._gather_force_series(frames)
        self._gather_independent_variable_series(frames)

        # store last dataset for new sections
        self._last_frames = frames
        self._last_delta_time = delta_time
        if self._is_panel_open():
            self._render_all_sections()
        else:
            self._needs_render = True

    # ------------------------------------------------------------------ #
    # Series extraction helpers
    # ------------------------------------------------------------------ #
    def _stack(self, frames: List[dict], key: str):
        try:
            arrs = [np.asarray(f[key]) for f in frames]
        except KeyError:
            return None
        if not arrs:
            return None
        try:
            return np.stack(arrs)
        except ValueError:
            return None

    def _add_series(self, name: str, values: Iterable[float]) -> None:
        vals = np.asarray(values, dtype=float).ravel()
        self._series[name] = _Series(name, vals)
        self._series_order.append(name)

    def _gather_node_series(self, frames: List[dict]) -> None:
        pos = self._stack(frames, "node_coordinates")
        if pos is not None and pos.ndim == 3:
            self._add_vector_components(pos, "Paths | Node", include_mag=True)

        vel = self._stack(frames, "node_coordinates_dt")
        if vel is not None and vel.ndim == 3:
            self._add_vector_components(vel, "Velocity | Node", include_mag=True, comp_labels=("Vx", "Vy"))

        acc = self._stack(frames, "node_coordinates_ddt")
        if acc is not None and acc.ndim == 3:
            self._add_vector_components(acc, "Acceleration | Node", include_mag=True, comp_labels=("Ax", "Ay"))

    def _gather_cg_series(self, frames: List[dict]) -> None:
        cg = self._stack(frames, "cg_global_cord")
        if cg is not None and cg.size and cg.ndim == 3:
            self._add_vector_components(cg, "Paths | CG", include_mag=True)

        cg_v = self._stack(frames, "cg_global_cord_dt")
        if cg_v is not None and cg_v.size and cg_v.ndim == 3:
            self._add_vector_components(cg_v, "Velocity | CG", include_mag=True, comp_labels=("Vx", "Vy"))

        cg_a = self._stack(frames, "cg_global_cord_ddt")
        if cg_a is not None and cg_a.size and cg_a.ndim == 3:
            self._add_vector_components(cg_a, "Acceleration | CG", include_mag=True, comp_labels=("Ax", "Ay"))

    def _gather_link_point_series(self, frames: List[dict]) -> None:
        pts = self._stack(frames, "link_extra_points")
        if pts is not None and pts.size and pts.ndim == 3:
            self._add_vector_components(
                pts,
                "Paths | Point",
                include_mag=True,
                point_labels=self._link_pt_map,
            )

        pts_v = self._stack(frames, "link_extra_points_dt")
        if pts_v is not None and pts_v.size and pts_v.ndim == 3:
            self._add_vector_components(
                pts_v,
                "Velocity | Point",
                include_mag=True,
                comp_labels=("Vx", "Vy"),
                point_labels=self._link_pt_map,
            )

        pts_a = self._stack(frames, "link_extra_points_ddt")
        if pts_a is not None and pts_a.size and pts_a.ndim == 3:
            self._add_vector_components(
                pts_a,
                "Acceleration | Point",
                include_mag=True,
                comp_labels=("Ax", "Ay"),
                point_labels=self._link_pt_map,
            )

    def _gather_force_series(self, frames: List[dict]) -> None:
        forces = self._stack(frames, "node_reactions")
        if forces is not None and forces.size and forces.ndim == 3:
            self._add_vector_components(forces, "Forces | Node", include_mag=True, comp_labels=("Fx", "Fy"))

    def _gather_independent_variable_series(self, frames: List[dict]) -> None:
        indep = self._stack(frames, "independent_variable")
        if indep is None or not indep.size:
            return

        indep = np.asarray(indep)
        if indep.ndim == 1:
            self._add_series("Input | independent_variable", indep)
        elif indep.ndim == 2:
            for idx in range(indep.shape[1]):
                self._add_series(f"Input | independent_variable {idx + 1}", indep[:, idx])

        dep = self._stack(frames, "dependent_variable")
        if dep is None or not dep.size:
            return

        dep = np.asarray(dep)
        if dep.ndim == 1:
            self._add_series("Input | dependent_variable", dep)
        elif dep.ndim == 2:
            for idx in range(dep.shape[1]):
                self._add_series(f"Input | dependent_variable {idx + 1}", dep[:, idx])

    def _add_vector_components(
        self,
        data: np.ndarray,
        prefix: str,
        *,
        include_mag: bool,
        comp_labels: Tuple[str, str] = ("X", "Y"),
        point_labels: List[Tuple[int, int]] | None = None,
    ) -> None:
        n_points = data.shape[1]
        for idx in range(n_points):
            label_suffix = self._format_point_suffix(idx, point_labels)
            for comp_idx, comp_name in enumerate(comp_labels):
                name = f"{prefix} {label_suffix} {comp_name}"
                self._add_series(name, data[:, idx, comp_idx])
            if include_mag and data.shape[2] >= 2:
                mag = np.linalg.norm(data[:, idx, :2], axis=1)
                self._add_series(f"{prefix} {label_suffix} |mag|", mag)

    @staticmethod
    def _format_point_suffix(idx: int, point_labels: List[Tuple[int, int]] | None) -> str:
        if point_labels and idx < len(point_labels):
            lnk, pt = point_labels[idx]
            return f"Link {lnk + 1} Pt {pt + 1}"
        return f"{idx + 1}"

    # UI helpers
    def _populate_axis_selectors(self, section: "GraphSection") -> None:
        selected_category = section.category_combo.currentText() or "All"
        cur_x = section.x_combo.currentText()
        cur_y = section.y_combo.currentText()
        section.x_combo.blockSignals(True)
        section.y_combo.blockSignals(True)
        section.x_combo.clear()
        section.y_combo.clear()

        def _allow_x(name: str) -> bool:
            if name == "Time":
                return True
            if selected_category == "All":
                return True
            return self._category_for_series(name) == selected_category

        def _allow_y(name: str) -> bool:
            if selected_category == "All":
                return True
            return self._category_for_series(name) == selected_category

        allowed_x = [n for n in self._series_order if _allow_x(n)]
        allowed_y = [n for n in self._series_order if _allow_y(n)]

        # Always keep current selections in the list so they don't disappear when filtering
        if cur_x and cur_x not in allowed_x:
            allowed_x.insert(0, cur_x)
        if cur_y and cur_y not in allowed_y:
            allowed_y.insert(0, cur_y)

        for name in allowed_x:
            section.x_combo.addItem(name)
        for name in allowed_y:
            section.y_combo.addItem(name)

        # Preserve previous selections when still available; otherwise keep current text untouched
        if cur_x and section.x_combo.findText(cur_x) != -1:
            section.x_combo.setCurrentText(cur_x)
        elif not cur_x and "Time" in self._series:
            section.x_combo.setCurrentText("Time")

        if cur_y and section.y_combo.findText(cur_y) != -1:
            section.y_combo.setCurrentText(cur_y)

        section.x_combo.blockSignals(False)
        section.y_combo.blockSignals(False)

    def _plot_current_selection(self, section: "GraphSection") -> None:
        if not self._series:
            section.show_empty(self.colors)
            return
        x_name = section.x_combo.currentText()
        y_name = section.y_combo.currentText()
        if not x_name or not y_name:
            return

        x = self._series.get(x_name)
        y = self._series.get(y_name)
        if x is None or y is None:
            return

        x_vals = x.values
        y_vals = y.values
        n = min(len(x_vals), len(y_vals))
        if n == 0:
            section.show_empty(self.colors)
            return

        needs_rebuild = (
            section.data_line is None
            or section.current_x_name != x_name
            or section.current_y_name != y_name
        )

        if needs_rebuild:
            section.ax.clear()
            section.style_axes(self.colors, self.font_sizes)
            line_color = self._get_line_color(y_name)
            section.data_line = section.ax.plot(
                x_vals[:n], y_vals[:n], color=line_color, linewidth=1.5
            )[0]
            section.current_x_name = x_name
            section.current_y_name = y_name
            section._bg_cache = None
        else:
            section.data_line.set_data(x_vals[:n], y_vals[:n])
            section.data_line.set_color(self._get_line_color(y_name))
            section.ax.relim()
            section.ax.autoscale_view()
            section._bg_cache = None

        section.ax.set_xlabel(x_name, color=self.colors["text"])
        section.ax.set_ylabel(y_name, color=self.colors["text"])
        section.canvas.draw_idle()
        section.update_cursor_line(self._cursor_idx, self._series)

    # ------------------------------------------------------------------ #
    # Theme handling
    # ------------------------------------------------------------------ #
    def apply_palette(self, palette: dict) -> None:
        """
        Update colors for the graph and redraw.
        Expected keys: face, spine, ticks, grid, text, line
        """
        self.colors.update(palette or {})
        for section in self._sections:
            section.apply_palette(self.colors, self.font_sizes)
        for section in self._sections:
            self._plot_current_selection(section)
        # Refresh add button styling to match theme
        if self.add_button:
            self.add_button.setStyleSheet(
                "QPushButton {"
                "  background-color: transparent;"
                "  border: none;"
                "  padding: 4px;"
                f"  color: {self.colors['text']};"
                "  font-size: 18px;"
                "  font-weight: bold;"
                "}"
                "QPushButton:hover {"
                f"  color: {self.colors['spine']};"
                "}"
                "QPushButton:pressed {"
                f"  color: {self.colors['grid']};"
                "}"
            )
        if self.remove_button:
            self.remove_button.setStyleSheet(
                "QPushButton {"
                "  background-color: transparent;"
                "  border: none;"
                "  padding: 4px;"
                f"  color: {self.colors['text']};"
                "  font-size: 18px;"
                "  font-weight: bold;"
                "}"
                "QPushButton:hover {"
                f"  color: {self.colors['spine']};"
                "}"
                "QPushButton:pressed {"
                f"  color: {self.colors['grid']};"
                "}"
                "QPushButton:disabled {"
                "  color: rgba(128,128,128,0.6);"
                "}"
            )

    def set_series_colors(self, mapping: Dict[str, str]) -> None:
        """Set category -> color hex mapping for lines (Paths, Velocity, etc.)."""
        self.series_colors = mapping or {}
        if self._is_panel_open():
            for section in self._sections:
                self._plot_current_selection(section)
            self._update_cursor_lines()
        else:
            self._needs_render = True

    def set_cursor(self, frame_idx: int | None) -> None:
        """Update vertical cursor line to match current frame."""
        self._cursor_idx = None if frame_idx is None else int(frame_idx)
        if self._is_panel_open():
            self._update_cursor_lines()

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _category_for_series(self, name: str) -> str:
        if "|" in name:
            return name.split("|", 1)[0].strip()
        return "Other"

    def _get_line_color(self, series_name: str) -> str:
        cat = self._category_for_series(series_name)
        if cat in self.series_colors:
            return self.series_colors[cat]
        return self.colors.get("line", "#59b8ff")

    def _collect_categories(self) -> List[str]:
        cats = sorted({self._category_for_series(n) for n in self._series_order})
        if "All" not in cats:
            cats.insert(0, "All")
        return cats

    def _update_remove_enabled(self) -> None:
        if self.remove_button:
            self.remove_button.setEnabled(len(self._sections) > 1)

    def _rebalance_splitter(self) -> None:
        if not self._sections:
            return
        h = self.splitter.height()
        if h <= 0:
            QTimer.singleShot(0, self._rebalance_splitter)
            return
        count = len(self._sections)
        per = max(160, h // count)
        self.splitter.setSizes([per] * count)

    def _update_cursor_lines(self) -> None:
        for section in self._sections:
            section.update_cursor_line(self._cursor_idx, self._series)

    def _poll_cursor(self) -> None:
        """Poll the OpenGL widget for current frame and update the vline efficiently."""
        if not self.isVisible():
            return
        app = self.app
        if app is None or not hasattr(app, "opengl_widget"):
            return
        if not self._is_panel_open():
            return
        if self._needs_render and self._last_frames is not None:
            self._render_all_sections()
        frame = getattr(app.opengl_widget, "current_frame", None)
        if frame is None or frame == self._cursor_idx or not self._series:
            return
        self._last_polled_frame = frame
        self.set_cursor(frame)

    def _render_all_sections(self) -> None:
        self._populate_categories()
        for section in self._sections:
            self._populate_axis_selectors(section)
            self._plot_current_selection(section)
        self._needs_render = False
        self._update_cursor_lines()

    def _is_panel_open(self) -> bool:
        """Return True if the right splitter pane is visible (>0 size)."""
        try:
            sizes = self.app.ui.splitter.sizes()
            return bool(sizes and sizes[-1] > 1)
        except Exception:
            return True  # default to updating if unknown

    def _populate_categories(self) -> None:
        current = None
        if self._sections:
            current = self._sections[0].category_combo.currentText()
        cats = self._collect_categories()
        for section in self._sections:
            section.populate_categories(cats, current or "All")

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        for section in self._sections:
            section.enforce_aspect(self.height_scale)
        self._rebalance_splitter()

    # Section management
    def _add_section(self, copy_state: bool = False) -> None:
        section = GraphSection(self)
        self._sections.append(section)
        self.splitter.addWidget(section)
        section.apply_palette(self.colors, self.font_sizes)
        section.enforce_aspect(self.height_scale)
        cats = self._collect_categories()
        preferred_cat = "All"
        if copy_state and len(self._sections) > 1:
            preferred_cat = self._sections[-2].category_combo.currentText() or preferred_cat
            section.copy_selection_from(self._sections[-2])
        elif self._sections:
            preferred_cat = self._sections[0].category_combo.currentText() or preferred_cat

        section.populate_categories(cats, preferred_cat)
        self._populate_axis_selectors(section)

        section.category_combo.currentIndexChanged.connect(lambda _=None, s=section: self._populate_axis_selectors(s))
        section.x_combo.currentIndexChanged.connect(lambda _=None, s=section: self._plot_current_selection(s))
        section.y_combo.currentIndexChanged.connect(lambda _=None, s=section: self._plot_current_selection(s))
        section.show_empty(self.colors)
        self._update_remove_enabled()
        self._rebalance_splitter()
        # If we already have data loaded, populate selectors/plot immediately
        if self._last_frames is not None:
            if self._is_panel_open():
                self._populate_axis_selectors(section)
                self._plot_current_selection(section)
            else:
                self._needs_render = True
            section.update_cursor_line(self._cursor_idx, self._series)

    def _remove_last_section(self) -> None:
        if len(self._sections) <= 1:
            return
        section = self._sections.pop()
        section.setParent(None)
        section.deleteLater()
        self._update_remove_enabled()
        self._rebalance_splitter()
        if self._sections:
            self._plot_current_selection(self._sections[-1])


class GraphSection(QWidget):
    def __init__(self, panel: GraphPanel):
        super().__init__(panel)
        self.panel = panel
        self.setMinimumHeight(160)
        self.data_line = None
        self.current_x_name = None
        self.current_y_name = None
        self.cursor_line = None
        self._last_cursor_idx = None
        self._last_cursor_x = None
        self._bg_cache = None

        self.figure = Figure(facecolor=panel.colors["face"])
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        ctrl_row = QHBoxLayout()
        ctrl_row.setContentsMargins(0, 0, 0, 0)
        ctrl_row.setSpacing(2)

        self.category_label = QToolButton()
        self.category_label.setText("Group")
        self.category_label.setEnabled(False)
        self.category_label.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.category_combo = QComboBox()

        self.x_label = QToolButton()
        self.x_label.setText("X")
        self.x_label.setEnabled(False)
        self.x_label.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.x_combo = QComboBox()
        self.y_label = QToolButton()
        self.y_label.setText("Y")
        self.y_label.setEnabled(False)
        self.y_label.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.y_combo = QComboBox()
        for cmb in (self.category_combo, self.x_combo, self.y_combo):
            cmb.setMinimumWidth(60)

        self.value_label = QLabel("X: --  Y: --")
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        ctrl_row.addWidget(self.category_label, 0, Qt.AlignVCenter)
        ctrl_row.addWidget(self.category_combo, 1)
        ctrl_row.addWidget(self.x_label, 0, Qt.AlignVCenter)
        ctrl_row.addWidget(self.x_combo, 1)
        ctrl_row.addWidget(self.y_label, 0, Qt.AlignVCenter)
        ctrl_row.addWidget(self.y_combo, 1)
        ctrl_row.addWidget(self.value_label, 0, Qt.AlignVCenter)

        root = QVBoxLayout(self)
        root.setContentsMargins(1, 1, 1, 1)
        root.setSpacing(1)
        root.addLayout(ctrl_row)
        root.addWidget(self.canvas, 1)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setIconSize(QSize(35, 35))
        root.addWidget(self.toolbar, 0, Qt.AlignTop)

    def apply_palette(self, colors: dict, font_sizes: dict) -> None:
        self.style_axes(colors, font_sizes)
        btn_style = (
            f"QToolButton {{ background-color: {colors['face']};"
            f" color: {colors['text']}; border: none; }}"
            f"QToolButton:disabled {{ color: {colors['text']}; }}"
        )
        for btn in (self.category_label, self.x_label, self.y_label):
            btn.setStyleSheet(btn_style)

        combo_style = (
            f"QComboBox {{ background-color: {colors['face']};"
            f" color: {colors['text']}; border: 1px solid {colors['spine']}; padding: 4px 6px; }}"
            f"QComboBox QAbstractItemView {{ background-color: {colors['face']}; color: {colors['text']};"
            f" selection-background-color: {colors['grid']}; }}"
        )
        for cmb in (self.category_combo, self.x_combo, self.y_combo):
            cmb.setStyleSheet(combo_style)

        dim_gray = "dimgray"
        self.toolbar.setStyleSheet(
            f"QToolBar {{ background: {colors['face']}; border: 0; }} "
            f"QToolButton {{ color: {dim_gray}; background: {colors['face']}; }}"
            f"QToolButton:hover {{ background: {colors['grid']}; }}"
        )
        self.value_label.setStyleSheet(
            f"QLabel {{ color: {colors['text']}; background: transparent; padding: 0 4px; }}"
        )
        self._tint_toolbar_icons(colors.get("spine", dim_gray))
        self._bg_cache = None

    def style_axes(self, colors: dict, font_sizes: dict) -> None:
        self.ax.set_facecolor(colors["face"])
        for spine in self.ax.spines.values():
            spine.set_color(colors["spine"])
        self.ax.tick_params(colors=colors["ticks"], labelsize=font_sizes["tick"], pad=2)
        self.ax.grid(True, color=colors["grid"], linestyle="--", alpha=0.4, linewidth=0.6)
        self.ax.xaxis.label.set_color(colors["text"])
        self.ax.yaxis.label.set_color(colors["text"])
        self.ax.xaxis.label.set_size(font_sizes["label"])
        self.ax.yaxis.label.set_size(font_sizes["label"])
        self.figure.set_facecolor(colors["face"])
        # Fixed margins so all plots share the same layout while keeping axis labels visible
        self.figure.subplots_adjust(left=0.12, right=0.98, top=0.95, bottom=0.12)

    def populate_categories(self, cats: List[str], preferred: str) -> None:
        self.category_combo.blockSignals(True)
        cur = self.category_combo.currentText() or preferred
        self.category_combo.clear()
        for c in cats:
            self.category_combo.addItem(c)
        if cur in cats:
            self.category_combo.setCurrentText(cur)
        self.category_combo.blockSignals(False)

    def show_empty(self, colors: dict) -> None:
        self.ax.clear()
        self.style_axes(colors, {"tick": 8, "label": 8})
        self.ax.text(
            0.5,
            0.5,
            "Run a simulation",
            color=colors["text"],
            ha="center",
            va="center",
            transform=self.ax.transAxes,
        )
        self.canvas.draw_idle()
        self._bg_cache = None

    def _tint_toolbar_icons(self, color_hex: str) -> None:
        """Re-color Matplotlib toolbar icons to match the UI chrome."""
        if not self.toolbar:
            return
        color = QColor(color_hex)
        size = self.toolbar.iconSize()
        for act in self.toolbar.actions():
            icon = act.icon()
            if icon.isNull():
                continue
            pm = icon.pixmap(size)
            if pm.isNull():
                continue
            tinted = QPixmap(pm.size())
            tinted.fill(Qt.transparent)
            painter = QPainter(tinted)
            painter.drawPixmap(0, 0, pm)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(tinted.rect(), color)
            painter.end()
            act.setIcon(QIcon(tinted))

    def enforce_aspect(self, scale: float) -> None:
        w = max(40, self.canvas.width())
        max_h = int(w * 1 * scale)
        self.canvas.setMaximumHeight(max(120, max_h))
        self.canvas.setMinimumHeight(0)
        self._bg_cache = None

    def copy_selection_from(self, other: "GraphSection") -> None:
        self.category_combo.setCurrentText(other.category_combo.currentText())
        self.x_combo.setCurrentText(other.x_combo.currentText())
        self.y_combo.setCurrentText(other.y_combo.currentText())
        self.value_label.setText(other.value_label.text())

    def update_cursor_line(self, frame_idx: int | None, series: Dict[str, _Series]) -> None:
        """Draw or move a red dashed vline to the given frame index."""
        if not self.canvas.isVisible():
            return

        if frame_idx is None:
            if self.cursor_line:
                self.cursor_line.remove()
                self.cursor_line = None
                self._last_cursor_idx = None
                self._last_cursor_x = None
                self.canvas.draw_idle()
            self._set_value_text(None, None)
            return

        x_name = self.x_combo.currentText()
        data = series.get(x_name)
        y_name = self.y_combo.currentText()
        y_data = series.get(y_name)
        if data is None or y_data is None or data.values.size == 0 or y_data.values.size == 0:
            self._set_value_text(None, None)
            return

        idx = max(0, min(int(frame_idx), len(data.values) - 1))
        x_val = float(data.values[idx])
        y_val = float(y_data.values[min(idx, len(y_data.values) - 1)])
        self._set_value_text(x_val, y_val)

        if self.cursor_line is None:
            self.cursor_line = self.ax.axvline(
                x_val, color="#e74c3c", linestyle="--", linewidth=1.0, zorder=5
            )
            self._last_cursor_idx = idx
            self._last_cursor_x = x_val
            # Build a clean background without the cursor line
            self.cursor_line.set_visible(False)
            self.canvas.draw()
            self._bg_cache = self.canvas.copy_from_bbox(self.ax.bbox)
            self.cursor_line.set_visible(True)

        if self._last_cursor_idx == idx and self._last_cursor_x == x_val:
            return

        self.cursor_line.set_xdata([x_val, x_val])
        self._last_cursor_idx = idx
        self._last_cursor_x = x_val
        if self._bg_cache is None:
            self.cursor_line.set_visible(False)
            self.canvas.draw()
            self._bg_cache = self.canvas.copy_from_bbox(self.ax.bbox)
            self.cursor_line.set_visible(True)

        self.canvas.restore_region(self._bg_cache)
        self.ax.draw_artist(self.cursor_line)
        self.canvas.blit(self.ax.bbox)

    def _set_value_text(self, x_val: float | None, y_val: float | None) -> None:
        if x_val is None or y_val is None:
            self.value_label.setText("X: --  Y: --")
            return
        self.value_label.setText(f"X: {x_val:.3g}  Y: {y_val:.3g}")
