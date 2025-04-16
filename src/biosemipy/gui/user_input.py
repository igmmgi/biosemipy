import sys
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QLineEdit,
    QFormLayout,
    QLabel,
    QDialogButtonBox,
)


class UserInput(QDialog):
    def __init__(self, question, parent=None):

        QDialog.__init__(self, parent)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.user_input = QLineEdit()

        layout = QFormLayout()
        layout.addRow(QLabel(question), self.user_input)
        layout.addWidget(button_box)

        self.setWindowTitle(question)
        self.setLayout(layout)

    def get_selection(self):

        print("Input: {}\n".format(self.user_input.text()))
        return self.user_input.text()


def main():

    app = QApplication(sys.argv)
    user_input = UserInput("Question?")
    user_input.show()
    if user_input.exec():
        user_input.get_selection()
    sys.exit(app.quit())


if __name__ == "__main__":
    main()
