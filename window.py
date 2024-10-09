import sys
import threading

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QCalendarWidget, QLabel, \
    QListWidget
from PyQt6.QtCore import QDate
from main import automated_login


class ReservationInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setGeometry(100, 100, 400, 600)  # Increased height to accommodate new elements

    def initUI(self):
        layout = QVBoxLayout()

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        layout.addWidget(self.calendar)

        self.activity_combo = QComboBox()
        self.activity_combo.addItems(["游泳", "健身"])
        self.activity_combo.currentTextChanged.connect(self.update_time_slots)
        layout.addWidget(self.activity_combo)

        layout.addWidget(QLabel("首选时间段:"))
        self.time_slot_combo = QComboBox()
        layout.addWidget(self.time_slot_combo)

        layout.addWidget(QLabel("备选时间段 (最多选择3个):"))
        self.alternative_slots = QListWidget()
        self.alternative_slots.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.alternative_slots)

        confirm_button = QPushButton("确认")
        confirm_button.clicked.connect(self.confirm_selection)
        layout.addWidget(confirm_button)

        self.setLayout(layout)
        self.setWindowTitle('预约系统')

        self.update_time_slots("游泳")

    def update_time_slots(self, activity):
        self.time_slot_combo.clear()
        self.alternative_slots.clear()
        if activity == "游泳":
            slots = ["09:30-11:00", "12:00-14:00", "14:30-16:00", "16:30-18:00", "18:30-20:30"]
        else:  # 健身
            slots = ["10:30-12:00", "12:00-13:30", "13:30-15:00", "15:00-16:30", "16:30-18:00", "18:00-19:30",
                     "19:30-21:00"]
        self.time_slot_combo.addItems(slots)
        self.alternative_slots.addItems(slots)

    def confirm_selection(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        selected_activity = self.activity_combo.currentText()
        primary_time_slot = self.time_slot_combo.currentText()

        alternative_slots = [item.text() for item in self.alternative_slots.selectedItems()]

        # Ensure we have at most 3 alternative slots
        alternative_slots = alternative_slots[:3]

        # Combine primary and alternative slots into a single list
        all_slots = [primary_time_slot] + alternative_slots

        result = {
            "date": selected_date,
            "activity": selected_activity,
            "time_slots": all_slots
        }
        print(result)

        # Create a new thread to run the automated_login function
        thread = threading.Thread(target=automated_login,
                                  args=(selected_activity, selected_date, all_slots))
        thread.start()
        # Close the window
        self.close()


def main():
    app = QApplication(sys.argv)
    ex = ReservationInterface()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()