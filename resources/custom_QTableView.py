from PyQt5.QtWidgets import QTableView

class CustomQTableView(QTableView):
    def focusOutEvent(self, event):
        self.clearSelection()
        super().focusOutEvent(event)