import sys
from PyQt5.QtWidgets import QApplication, QDialog, QGroupBox, QComboBox, \
    QLineEdit, QFormLayout, QLabel, QDialogButtonBox, QVBoxLayout


class ChannelDifference(QDialog):

    def __init__(self, labels, parent=None):

        QDialog.__init__(self, parent)

        channels = QGroupBox()

        self.selection1 = QComboBox()
        self.selection1.addItems(labels)
        self.selection2 = QComboBox()
        self.selection2.addItems(labels)
        self.selection3 = QLineEdit()

        layout = QFormLayout()
        layout.addRow(QLabel("Channel 1:"), self.selection1)
        layout.addRow(QLabel("Channel 2:"), self.selection2)
        layout.addRow(QLabel("Output Label:"), self.selection3)

        channels.setLayout(layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(channels)
        layout.addWidget(button_box)

        self.setWindowTitle("Channel Difference")
        self.setLayout(layout)

    def get_selection(self):

        s1 = str(self.selection1.currentText())
        s2 = str(self.selection2.currentText())
        s3 = str(self.selection3.text())

        print("Selection 1: {}\nSelection 2: {}\nOutput:{}".format(s1, s2, s3))

        return s1, s2, s3


def main():

    app = QApplication(sys.argv)
    channel_difference = ChannelDifference(["a1", "b1",  "a2", "b2"])
    channel_difference.show()
    if channel_difference.exec_():
        channel_difference.get_selection()
    sys.exit(app.quit())


if __name__ == '__main__':
    main()
