import sys
from PyQt5.QtWidgets import QApplication, QDialog, QPlainTextEdit, \
    QDialogButtonBox, QVBoxLayout


class DisplayText(QDialog):

    def __init__(self, title, txt, parent=None):

        QDialog.__init__(self, parent)

        text_box = QPlainTextEdit(self)
        text_box.insertPlainText(txt)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(text_box)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setWindowTitle(title)


def main():

    app = QApplication(sys.argv)
    display_text = DisplayText("Dispaly Text", "text")
    display_text.show()
    if display_text.exec_():
        pass
    sys.exit(app.quit())


if __name__ == '__main__':
    main()
