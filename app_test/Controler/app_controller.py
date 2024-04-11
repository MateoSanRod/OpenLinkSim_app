from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import Qt

from app_test.Controler.run_model import run_image, run_simulation
from app_test.Model.model import Simulation



class AppController(QObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = app.ui
        self.view = app.plot_widget
        self.input = app.input
        self.status_bar = self.ui.statusbar  # Accessing the status bar
        self.global_key_actions = {
            (Qt.Key_Tab, Qt.ControlModifier): self.handle_ctrl_tab,
        }
        self.plain_text_edit_key_actions = {
            (Qt.Key_Escape, Qt.NoModifier): self.handle_escape,
            (Qt.Key_Return, Qt.ShiftModifier): self.handle_shift_return,
        }

    def eventFilter(self, obj, event):
        if obj == self.ui.plainTextEdit:
            return self.handle_plain_text_edit_event(event)
        else:
            return self.handle_global_event(event)

    def handle_plain_text_edit_event(self, event):
        if event.type() == QEvent.KeyPress:
            key_combo = (event.key(), event.modifiers())
            if key_combo in self.plain_text_edit_key_actions:
                self.update_status_bar(f"{Qt.Key(event.key())} with modifiers: {event.modifiers()}")
                self.plain_text_edit_key_actions[key_combo]()
                return True
        return False

    def handle_global_event(self, event):
        if event.type() == QEvent.KeyPress:
            key_combo = (event.key(), event.modifiers())
            if key_combo in self.global_key_actions:
                self.update_status_bar(f"{Qt.Key(event.key())} with modifiers: {event.modifiers()}")
                self.global_key_actions[key_combo]()
                return True
        return False

    def handle_ctrl_tab(self):
        self.input.compile()
        run_simulation(self.view, self.input)

    def handle_shift_return(self):
        self.input.compile()
        run_image(self.view, self.input)

    def handle_escape(self):
        self.ui.plainTextEdit.clearFocus()

    def update_status_bar(self, message):
        self.status_bar.showMessage(message)
