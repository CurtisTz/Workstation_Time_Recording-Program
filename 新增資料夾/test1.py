from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QAbstractItemView, QHeaderView, QWidget, QTabWidget
import datetime
import os
from TabWidget_1 import Ui_Form  # 假設 TabWidget_1 定義了 Ui_Form

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("站點工時紀錄-程式V20241216 by Curtis")
        self.setGeometry(500, 250, 800, 500)  # 設定適合的視窗大小
        # 初始化 Ui_Form
        self.ui = Ui_Form()
        central_widget = QWidget()
        self.ui.setupUi(central_widget)  # 設定 Ui_Form 的布局到中央窗口
        self.setCentralWidget(central_widget)

        # 獲取 Ui_Form 中的 tabWidget
        self.tabWidget = self.ui.tabWidget

        # 初始化屬性
        self.folder_path = ""
        self.station_name = ""
        self.operator_name = ""
        self.current_row = 0
        self.active_button = None

        # 初始化按鈕和表格
        self.setup_control()

        # 初始化第一個標籤頁
        self.init_new_tab()

        # 添加 "+" 按鈕作為新增標籤頁功能
        self.add_plus_tab()

        # 設置標籤頁切換事件
        self.tabWidget.currentChanged.connect(self.handle_tab_change)

    def setup_control(self):
        self.ui.path_pushButton.clicked.connect(self.open_folder)

        # 設定表格格式
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁用編輯

        # 設定定時器來更新時間
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.display_datetime)
        self.timer.start(1000)  # 每秒更新

        # 初始化按鈕
        self.buttons = {
            "Run": self.ui.run_button,
            "Idle": self.ui.idle_button,
            "Down": self.ui.down_button,
            "ENG": self.ui.eng_button,
        }
        for name, button in self.buttons.items():
            button.clicked.connect(lambda _, n=name: self.handle_button_click(n))

    def handle_button_click(self, name):
        button = self.buttons[name]
        current_time = self.ui.time_label.text()
        self.station_name = self.ui.station_lineEdit.text().strip()
        self.operator_name = self.ui.operator_lineEdit.text().strip()
        self.folder_path = self.ui.path_textEdit.toPlainText().strip()

        if not self.station_name:
            QtWidgets.QMessageBox.warning(None, "錯誤", "請填寫站點名稱！")
            return
        if not self.operator_name:
            QtWidgets.QMessageBox.warning(None, "錯誤", "請填寫操作者名稱！")
            return
        if not self.folder_path:
            QtWidgets.QMessageBox.warning(None, "錯誤", "請先選擇存取路徑！")
            return

        # 建立獨立的檔案名稱
        file_name = f"TestTimeLog_{self.station_name}_{self.operator_name}.csv"
        file_path = os.path.join(self.folder_path, file_name)

        if self.active_button == button:
            # 結束時間
            self.ui.tableWidget.setItem(self.current_row, 2, QTableWidgetItem(current_time))
            self.active_button = None
            self.toggle_buttons(enable=True)
            self.ui.station_lineEdit.setDisabled(False)
            self.ui.operator_lineEdit.setDisabled(False)

            # 寫入結束時間
            with open(file_path, "a", encoding="utf-8") as file:
                file.write(f"End time:,{current_time}\n")
            QtWidgets.QMessageBox.information(None, "訊息", f"結束時間已記錄至 {file_name}!")
        else:
            # 開始時間
            self.ui.tableWidget.setItem(self.current_row, 0, QTableWidgetItem(name))
            self.ui.tableWidget.setItem(self.current_row, 1, QTableWidgetItem(current_time))
            self.ui.tableWidget.setItem(self.current_row, 2, QTableWidgetItem(" "))
            self.toggle_buttons(enable=False, exclude=button)
            self.active_button = button
            self.ui.station_lineEdit.setDisabled(True)
            self.ui.operator_lineEdit.setDisabled(True)

            # 寫入開始時間
            with open(file_path, "a", encoding="utf-8-sig") as file:
                file.write(f"Station:,{self.station_name},Operator:,{self.operator_name},Status:,{name},Start time:,{current_time},")
            QtWidgets.QMessageBox.information(None, "訊息", f"開始時間已記錄至 {file_name}!")

    def toggle_buttons(self, enable, exclude=None):
        """切換按鈕啟用狀態。"""
        for btn in self.buttons.values():
            btn.setEnabled(enable or btn == exclude)

    def display_datetime(self):
        """顯示當前時間。"""
        now = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        self.ui.time_label.setText(now)

    def open_folder(self):
        """選擇目錄存放路徑。"""
        self.folder_path = QFileDialog.getExistingDirectory(None, "Open folder", "./")
        self.ui.path_textEdit.setText(self.folder_path)



    def init_new_tab(self):
        """新增標籤頁並初始化控件"""
        new_tab = QWidget()  # 創建新標籤頁
        tab_index = self.tabWidget.count() - 1  # 插入到 "+" 標籤前的位置
        self.tabWidget.insertTab(tab_index, new_tab, f"Tab {tab_index + 1}")  # 命名標籤頁
        self.tabWidget.setCurrentWidget(new_tab)  # 切換到新標籤頁

    def add_plus_tab(self):
        """添加 '+' 標籤頁按鈕"""
        self.tabWidget.addTab(QWidget(), "+")  # 添加 "+" 標籤頁

    def handle_tab_change(self, index):
        """當點擊最後一個標籤時，新增標籤頁"""
        if index == self.tabWidget.count() - 1:  # 如果是 "+" 標籤頁
            self.init_new_tab()

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
