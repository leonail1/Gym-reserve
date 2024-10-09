import json
import os
import sys
import threading
import time
from datetime import datetime

from PyQt6.QtCore import QDate, QTime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox,
                             QCalendarWidget, QLabel, QHBoxLayout, QTimeEdit, QMessageBox, QDateEdit, QCheckBox,
                             QLineEdit)

from main import automated_login


class ReservationInterface(QWidget):
    """
    预约系统界面类

    这个类创建了一个图形用户界面，允许用户选择日期、活动和时间段来进行预约。
    它还包括一个定时功能，可以在指定时间自动开始预约过程。

    属性:
        calendar (QCalendarWidget): 用于选择预约日期的日历控件
        activity_combo (QComboBox): 用于选择活动类型的下拉框
        primary_time_slot (QComboBox): 用于选择首选时间段的下拉框
        alternative_slots (list): 包含三个用于选择备选时间段的下拉框列表
        start_time_edit (QTimeEdit): 用于设置自动开始时间的时间编辑器
    """

    def __init__(self):
        """初始化预约界面"""
        super().__init__()
        self.settings_file = "reservation_settings.json"
        self.initUI()
        self.setGeometry(100, 100, 400, 700)  # 增加高度以容纳新的控件

    def initUI(self):
        layout = QVBoxLayout()

        # 读取上次的设置
        settings = self.load_settings()

        # 学号输入
        student_id_layout = QHBoxLayout()
        student_id_layout.addWidget(QLabel("学号:"))
        self.student_id_input = QLineEdit()
        if 'student_id' in settings:
            self.student_id_input.setText(settings['student_id'])
        student_id_layout.addWidget(self.student_id_input)
        layout.addLayout(student_id_layout)

        # 密码输入
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("密码:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        if 'password' in settings:
            self.password_input.setText(settings['password'])
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # 日历控件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        if 'selected_date' in settings:
            self.calendar.setSelectedDate(QDate.fromString(settings['selected_date'], "yyyy-MM-dd"))
        layout.addWidget(self.calendar)

        # 活动选择
        self.activity_combo = QComboBox()
        self.activity_combo.addItems(["游泳", "健身"])
        if 'activity' in settings:
            self.activity_combo.setCurrentText(settings['activity'])
        self.activity_combo.currentTextChanged.connect(self.update_time_slots)
        layout.addWidget(self.activity_combo)

        # 首选时间段
        layout.addWidget(QLabel("首选时间段:"))
        self.primary_time_slot = QComboBox()
        layout.addWidget(self.primary_time_slot)

        # 备选时间段
        alternative_layout = QHBoxLayout()
        self.alternative_slots = []
        for i in range(3):
            slot = QComboBox()
            slot.setFixedWidth(110)
            alternative_layout.addWidget(QLabel(f"备选 {i + 1}:"))
            alternative_layout.addWidget(slot)
            self.alternative_slots.append(slot)
        layout.addLayout(alternative_layout)

        # 预约时间执行选择框
        self.scheduled_execution_checkbox = QCheckBox("预约时间执行")
        if 'scheduled_execution' in settings:
            self.scheduled_execution_checkbox.setChecked(settings['scheduled_execution'])
        self.scheduled_execution_checkbox.stateChanged.connect(self.toggle_scheduled_execution)
        layout.addWidget(self.scheduled_execution_checkbox)

        # 预约开始时间控件
        self.scheduled_time_widget = QWidget()
        scheduled_time_layout = QHBoxLayout()
        scheduled_time_layout.addWidget(QLabel("预约开始日期时间:"))
        self.start_date_edit = QDateEdit()
        if 'start_date' in settings:
            self.start_date_edit.setDate(QDate.fromString(settings['start_date'], "yyyy-MM-dd"))
        else:
            self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        scheduled_time_layout.addWidget(self.start_date_edit)
        self.start_time_edit = QTimeEdit()
        if 'start_time' in settings:
            self.start_time_edit.setTime(QTime.fromString(settings['start_time'], "HH:mm"))
        else:
            self.start_time_edit.setTime(QTime.currentTime())
        scheduled_time_layout.addWidget(self.start_time_edit)
        self.scheduled_time_widget.setLayout(scheduled_time_layout)
        self.scheduled_time_widget.setVisible(self.scheduled_execution_checkbox.isChecked())
        layout.addWidget(self.scheduled_time_widget)

        # 确认按钮
        confirm_button = QPushButton("确认")
        confirm_button.clicked.connect(self.confirm_selection)
        layout.addWidget(confirm_button)

        self.setLayout(layout)
        self.setWindowTitle('预约系统')

        self.update_time_slots(self.activity_combo.currentText())

        # 设置时间槽的默认值
        if 'primary_slot' in settings:
            index = self.primary_time_slot.findText(settings['primary_slot'])
            if index >= 0:
                self.primary_time_slot.setCurrentIndex(index)
        if 'alternative_slots' in settings:
            for i, slot in enumerate(self.alternative_slots):
                if i < len(settings['alternative_slots']):
                    index = slot.findText(settings['alternative_slots'][i])
                    if index >= 0:
                        slot.setCurrentIndex(index)

    def load_settings(self):
        """从文件加载设置"""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return {}

    def save_settings(self):
        """保存设置到文件"""
        settings = {
            'student_id': self.student_id_input.text(),
            'password': self.password_input.text(),
            'selected_date': self.calendar.selectedDate().toString("yyyy-MM-dd"),
            'activity': self.activity_combo.currentText(),
            'primary_slot': self.primary_time_slot.currentText(),
            'alternative_slots': [slot.currentText() for slot in self.alternative_slots if slot.currentText()],
            'scheduled_execution': self.scheduled_execution_checkbox.isChecked(),
            'start_date': self.start_date_edit.date().toString("yyyy-MM-dd"),
            'start_time': self.start_time_edit.time().toString("HH:mm")
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)

    def update_time_slots(self, activity):
        """
        更新时间段选项

        根据选择的活动类型更新可用的时间段。

        参数:
            activity (str): 选择的活动类型
        """
        if activity == "游泳":
            slots = ["09:30-11:00", "12:00-14:00", "14:30-16:00", "16:30-18:00", "18:30-20:30"]
        else:  # 健身
            slots = ["10:30-12:00", "12:00-13:30", "13:30-15:00", "15:00-16:30", "16:30-18:00", "18:00-19:30",
                     "19:30-21:00"]

        self.primary_time_slot.clear()
        for slot in self.alternative_slots:
            slot.clear()

        self.primary_time_slot.addItems(slots)
        self.primary_time_slot.currentTextChanged.connect(self.update_alternative_slots)

        self.update_alternative_slots()

    def update_alternative_slots(self):
        """更新备选时间段的可选项"""
        current_slots = self.get_current_slots()
        available_slots = [slot for slot in self.get_all_slots() if slot not in current_slots]

        for slot in self.alternative_slots:
            self.update_combo_box(slot, available_slots)

    def update_combo_box(self, combo_box, available_slots):
        """
        更新下拉框的选项

        参数:
            combo_box (QComboBox): 要更新的下拉框
            available_slots (list): 可用的时间段列表
        """
        current_text = combo_box.currentText()
        combo_box.clear()
        combo_box.addItem("")  # 添加空选项
        combo_box.addItems(available_slots)
        if current_text in available_slots:
            combo_box.setCurrentText(current_text)

    def get_all_slots(self):
        """获取所有可用的时间段"""
        return [self.primary_time_slot.itemText(i) for i in range(self.primary_time_slot.count())]

    def get_current_slots(self):
        """获取当前选择的所有时间段"""
        return [self.primary_time_slot.currentText()] + [slot.currentText() for slot in self.alternative_slots]

    def toggle_scheduled_execution(self, state):
        """切换预约时间执行界面的显示状态"""
        if state == 2:  # 选中状态
            self.scheduled_time_widget.show()
        else:
            self.scheduled_time_widget.hide()

    def confirm_selection(self):
        """确认选择并开始预约任务"""
        student_id = self.student_id_input.text()
        password = self.password_input.text()

        if not student_id or not password:
            self.show_error_message("信息不完整", "请输入学号和密码。")
            return

        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        selected_activity = self.activity_combo.currentText()
        primary_time_slot = self.primary_time_slot.currentText()
        alternative_slots = [slot.currentText() for slot in self.alternative_slots if slot.currentText()]
        all_slots = [primary_time_slot] + alternative_slots
        result = {
            "student_id": student_id,
            "date": selected_date,
            "activity": selected_activity,
            "time_slots": all_slots
        }
        print("预约信息:", result)

        if self.scheduled_execution_checkbox.isChecked():
            start_date = self.start_date_edit.date().toPyDate()
            start_time = self.start_time_edit.time().toPyTime()
            start_datetime = datetime.combine(start_date, start_time)
            current_datetime = datetime.now()
            if start_datetime <= current_datetime:
                self.show_error_message("预约时间错误",
                                        f"预约开始时间 {start_datetime.strftime('%Y-%m-%d %H:%M')} 不能早于当前时间：{current_datetime.strftime('%Y-%m-%d %H:%M')}")
                return
            reservation_date = QDate.fromString(selected_date, "yyyy-MM-dd").toPyDate()
            if reservation_date < start_date:
                self.show_error_message("预约日期错误",
                                        f"预约日期 {selected_date} 不能早于预约开始时间的日期：{start_date.strftime('%Y-%m-%d')}")
                return
            wait_seconds = (start_datetime - current_datetime).total_seconds()
            print(f"系统将在 {start_datetime.strftime('%Y-%m-%d %H:%M:%S')} 开始自动预约，请保持程序运行。")
            # 创建并启动定时线程
            timer_thread = threading.Thread(target=self.timed_execution,
                                            args=(wait_seconds, student_id, password, selected_activity, selected_date,
                                                  all_slots))
            timer_thread.start()
        else:
            print("立即开始预约...")
            immediate_thread = threading.Thread(target=self.immediate_execution,
                                                args=(
                                                student_id, password, selected_activity, selected_date, all_slots))
            immediate_thread.start()
        self.save_settings()
        self.close()

    def show_error_message(self, title, message):
        """显示错误消息"""
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Warning)
        error_msg.setText(title)
        error_msg.setInformativeText(message)
        error_msg.setWindowTitle("错误")
        error_msg.exec()

    def timed_execution(self, wait_seconds,student_id,password, activity, date, slots):
        """
        定时执行预约任务

        参数:
            wait_seconds (float): 等待的秒数
            activity (str): 选择的活动
            date (str): 选择的日期
            slots (list): 选择的时间段列表
        """
        time.sleep(wait_seconds)
        print("开始执行预约...")
        automated_login(student_id, password, activity, date, slots)

    def immediate_execution(self,student_id, password, activity, date, slots):
        """立即执行预约任务"""
        print(f"立即执行预约: 活动 - {activity}, 日期 - {date}, 时间段 - {slots}")
        # 这里调用 automated_login 或其他预约逻辑
        automated_login(student_id, password, activity, date, slots)


def main():
    """主函数，启动应用程序"""
    app = QApplication(sys.argv)
    ex = ReservationInterface()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()