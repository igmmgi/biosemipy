import sys
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QComboBox,
    QLabel,
    QHBoxLayout,
)


class Crop(QDialog):
    def __init__(self, triggers, n_records, parent=None):

        QDialog.__init__(self, parent)

        self.triggers = triggers
        self.n_records = n_records

        self.selection_box = QComboBox()
        self.selection_box.addItem("Select")
        self.selection_box.addItem("Triggers")
        self.selection_box.addItem("Records")

        self.selection_box.currentIndexChanged.connect(self.set_available_crop_values)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.crop_start = QComboBox()
        self.crop_end = QComboBox()

        crop_labels = QHBoxLayout()
        crop_labels.addWidget(QLabel("Crop Start"))
        crop_labels.addWidget(QLabel("Crop End"))

        crop_values = QHBoxLayout()
        crop_values.addWidget(self.crop_start)
        crop_values.addWidget(self.crop_end)

        layout_main = QVBoxLayout()
        layout_main.addWidget(QLabel("Crop Method"))
        layout_main.addWidget(self.selection_box)
        layout_main.addLayout(crop_labels)
        layout_main.addLayout(crop_values)
        layout_main.addWidget(button_box)

        self.setLayout(layout_main)
        self.setWindowTitle("Crop Settings")

    def set_available_crop_values(self):
        selection = self.selection_box.currentText()
        if selection == "Triggers":
            vals = self.triggers
            self.crop_start.addItem(str(0))
            self.crop_end.addItem(str(0))
        elif selection == "Records":
            vals = range(1, self.n_records + 1)
        else:
            return
        for val in vals:
            self.crop_start.addItem(str(val))
            self.crop_end.addItem(str(val))

    def get_selection(self):

        crop_selection_type = self.selection_box.currentText().lower()
        crop_start_value = int(self.crop_start.currentText())
        crop_end_value = int(self.crop_end.currentText())
        print(
            "Crop Type: {}\t Range: {}-{}".format(
                crop_selection_type, crop_start_value, crop_end_value
            )
        )

        return crop_selection_type, crop_start_value, crop_end_value


def main():

    app = QApplication(sys.argv)
    app.setApplicationName("Channel Selection")
    crop_selection = Crop([1, 2, 3, 4], 100)
    crop_selection.show()
    if crop_selection.exec():
        crop_selection.get_selection()
    sys.exit(app.quit())


if __name__ == "__main__":
    main()
