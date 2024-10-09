import sys
import threading

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QCalendarWidget
from PyQt6.QtCore import QDate
from main import automated_login


class ReservationInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setGeometry(100, 100, 400, 500)  # 调整窗口大小以适应日历

    def initUI(self):
        layout = QVBoxLayout()

        # 使用 QCalendarWidget 替代 QDateEdit
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        layout.addWidget(self.calendar)

        self.activity_combo = QComboBox()
        self.activity_combo.addItems(["游泳", "健身"])
        self.activity_combo.currentTextChanged.connect(self.update_time_slots)
        layout.addWidget(self.activity_combo)

        self.time_slot_combo = QComboBox()
        layout.addWidget(self.time_slot_combo)

        confirm_button = QPushButton("确认")
        confirm_button.clicked.connect(self.confirm_selection)
        layout.addWidget(confirm_button)

        self.setLayout(layout)
        self.setWindowTitle('预约系统')

        self.update_time_slots("游泳")

    def update_time_slots(self, activity):
        self.time_slot_combo.clear()
        if activity == "游泳":
            slots = ["09:30-11:00", "12:00-14:00", "14:30-16:00", "16:30-18:00", "18:30-20:30"]
        else:  # 健身
            slots = ["10:30-12:00", "12:00-13:30", "13:30-15:00", "15:00-16:30", "16:30-18:00", "18:00-19:30",
                     "19:30-21:00"]
        self.time_slot_combo.addItems(slots)

    def confirm_selection(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        selected_activity = self.activity_combo.currentText()
        selected_time_slot = self.time_slot_combo.currentText()

        result = {
            "date": selected_date,
            "activity": selected_activity,
            "time_slot": selected_time_slot
        }
        print(result)

        # 创建新线程运行 automated_login 函数
        thread = threading.Thread(target=automated_login,
                                  args=(selected_activity, selected_date, selected_time_slot))
        thread.start()
        # 关闭窗口
        self.close()


def main():
    app = QApplication(sys.argv)
    ex = ReservationInterface()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()