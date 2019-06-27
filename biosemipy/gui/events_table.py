import sys
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
)


class EventsTable(QDialog):
    def __init__(self, event_dict, parent=None):

        QDialog.__init__(self, parent)

        event_table = QTableWidget()
        event_table.setColumnCount(2)
        event_table.setHorizontalHeaderLabels(["Value", "Count"])
        event_table.setRowCount(len(event_dict.keys()))
        event_table.verticalHeader().setVisible(False)
        for idx, item in enumerate(event_dict.items()):
            event_table.setItem(idx, 0, QTableWidgetItem(str(item[0])))
            event_table.setItem(idx, 1, QTableWidgetItem(str(item[1])))

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(event_table)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setWindowTitle("Events")


def main():

    app = QApplication(sys.argv)
    events = EventsTable({"1": 1, "2": 2})
    events.show()
    if events.exec_():
        pass
    sys.exit(app.quit())


if __name__ == "__main__":
    main()
