import sys
from PyQt5.QtWidgets import QApplication, QDialog, QDialogButtonBox, \
    QVBoxLayout, QComboBox, QLabel


class Decimate(QDialog):

    def __init__(self, factors, parent=None):

        QDialog.__init__(self, parent)

        self.factors = factors

        self.selection_box = QComboBox()
        for factor in factors:
            self.selection_box.addItem(str(factor))

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout_main = QVBoxLayout()
        layout_main.addWidget(QLabel("Decimate Factor"))
        layout_main.addWidget(self.selection_box)
        layout_main.addWidget(button_box)

        self.setLayout(layout_main)
        self.setWindowTitle("Decimate Settings")

    def get_selection(self):

        decimate_factor = int(self.selection_box.currentText())
        print("Decimate Factor: {}".format(decimate_factor))

        return decimate_factor


def main():

    app = QApplication(sys.argv)
    app.setApplicationName('Decimate')
    decimate_selection = Decimate([2, 4, 8])
    decimate_selection.show()
    if decimate_selection.exec_():
        decimate_selection.get_selection()
    sys.exit(app.quit())


if __name__ == '__main__':
    main()
