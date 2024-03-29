import sys
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QListWidget,
    QAbstractItemView,
)


class ChannelSelection(QDialog):
    def __init__(self, labels, parent=None):

        QDialog.__init__(self, parent)

        self.selection_box = QListWidget()
        self.selection_box.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )
        for label in labels:
            self.selection_box.addItem(label)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.selection_box)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setWindowTitle("Channel Selection")

    def get_selection(self):

        selection = []
        print("Selecting Channel:")
        for select in self.selection_box.selectedItems():
            label = select.text()
            print("{}".format(label), end=" ")
            selection.append(select.text())
        print("")
        return selection


def main():

    app = QApplication(sys.argv)
    channel_selection = ChannelSelection(["a1", "b1", "a2", "b2"])
    channel_selection.show()
    if channel_selection.exec():
        channel_selection.get_selection()
    sys.exit(app.quit())


if __name__ == "__main__":
    main()
