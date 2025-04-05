from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QAbstractItemView, QHeaderView, QWidget, QTabWidget
from datetime import datetime,timedelta
import os
import csv
from TabWidget_1 import Ui_Form
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 啟用標籤頁的關閉按鈕
        self.setTabsClosable(True)#外觀
        self.tabCloseRequested.connect(self.confirmCloseTab)#功能
        #啟用移動標籤頁
        #self.setMovable(True)
        #啟用標籤形狀
        self.setTabShape(1)

        # 初始化第一個標籤頁
        self.initNewTab()

        # 添加 "新增標籤頁" 按鈕
        self.addTab(QWidget(), "+")
        self.currentChanged.connect(self.handleTabChange)
        
        # 連接雙擊標籤的信號
        self.tabBarDoubleClicked.connect(self.renameTab)

    def initNewTab(self):
        """初始化新標籤頁"""
        new_tab = QWidget()
        tab_ui = TabUI(new_tab)  # 創建每個標籤頁的 UI 和邏輯實例
        tab_index = self.count()-1  # 新標籤插入到 "+" 之前的位置
        self.insertTab(tab_index, new_tab, f"Tab {tab_index}")  # 設置標籤名稱
        self.setCurrentWidget(new_tab)  # 切換到新建的標籤頁

    def handleTabChange(self, index):
        """處理標籤頁切換事件"""
        if index == self.count() - 1:  # 如果點擊的是最後一個 "+" 標籤頁
            self.initNewTab()

    def renameTab(self, index):
        """雙擊標籤觸發改名功能"""
        if index == self.count() - 1:
            # 禁止對 "+" 標籤改名
            return
        
        # 彈出輸入框，讓用戶輸入新標籤名稱
        new_name, ok = QInputDialog.getText(self, "改名", "輸入新的標籤名稱:")
        if ok and new_name.strip():
            self.setTabText(index, new_name.strip())
    def confirmCloseTab(self, index):
        """顯示關閉確認對話框"""
        if index == self.count() - 1:
            # 禁止關閉 "+" 標籤
            print("無法關閉 '+' 標籤頁")
            return

            # 顯示確認對話框
        reply = QMessageBox.question(
            self,
            "確認關閉",
            f"確定要關閉標籤頁 {self.tabText(index)} 嗎？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            print(f"關閉標籤頁: {self.tabText(index)}")
            if self.currentIndex() == index:
                # 如果有前一個標籤，則切換到前一個，否則切換到下一個
                new_index = index - 1 if index > 0 else index + 1
                self.setCurrentIndex(new_index)
            self.removeTab(index)  # 刪除標籤頁       
        else:
            print(f"取消關閉標籤頁: {self.tabText(index)}")


class TabUI:
    def __init__(self, tab):
        self.tab = tab
        self.ui = Ui_Form()
        self.ui.setupUi(tab)

        # 初始化屬性
        self.folder_path = ""
        self.station_name = ""
        self.operator_name = ""
        self.current_row = 0
        self.active_button = None
        self.start_time=None
        self.end_time=None

        # 初始化按鈕和表格
        self.setup_control()

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
        self.note=self.ui.note_plainTextEdit.toPlainText().strip()

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
        file_name = f"TestTimeLog_{self.station_name}.csv"
        file_path = os.path.join(self.folder_path, file_name)

        if self.active_button == button:
            # 結束時間
            self.ui.tableWidget.setItem(self.current_row, 2, QTableWidgetItem(current_time))
            self.active_button = None
            self.toggle_buttons(enable=True)
            self.ui.station_lineEdit.setDisabled(False)
            self.ui.operator_lineEdit.setDisabled(False)
            self.end_time=datetime.now()
            print(self.end_time)
            print(self.start_time)
            print(type(self.end_time))

            time_diff = self.end_time - self.start_time
            print(time_diff)
            print(type(time_diff))
            #計算天和秒
            days=time_diff.days
            total_seconds= time_diff.seconds
            #計算時分秒
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            formatted_time_diff= f"{days}:{hours:02}:{minutes:02}:{seconds:02}"

            # 寫入結束時間
            with open(file_path, "a", encoding="utf-8") as file:     
                #csv_writer = csv.writer(file, delimiter='\t')
                #csv_writer.writerow([current_time,formatted_time_diff])
                
                file.write(f"{current_time},{formatted_time_diff}\n")
            QtWidgets.QMessageBox.information(None, "訊息", f"結束時間已記錄至 {file_name}!")
        else:
            # 開始時間
            self.ui.tableWidget.setItem(self.current_row, 0, QTableWidgetItem(name))
            self.ui.tableWidget.setItem(self.current_row, 1, QTableWidgetItem(current_time))
            self.ui.tableWidget.setItem(self.current_row, 2, QTableWidgetItem(" "))
            self.ui.tableWidget.setItem(self.current_row, 3,QTableWidgetItem(self.note))
            self.toggle_buttons(enable=False, exclude=button)
            self.active_button = button
            self.ui.station_lineEdit.setDisabled(True)
            self.ui.operator_lineEdit.setDisabled(True)
            self.start_time=datetime.now()
            # 寫入開始時間
            # 在寫入時檢查檔案是否存在
            if not os.path.exists(file_path):
                with open(file_path, "a", encoding="utf-8-sig") as file:
                    #csv_writer=csv.writer(file,delimiter="\t")
                    #csv_writer.writerow([self.station_name,self.operator_name,name,self.note,current_time,])                    
                    file.write(f"Station:,Operator:,Status:,Note,Start time:,End time:,Time diff:\n")

            # 後續正常寫入數據
            with open(file_path, "a", encoding="utf-8-sig") as file:
                #csv_writer=csv.writer(file,delimiter="\t")
                #csv_writer.writerow([self.station_name,self.operator_name,name,self.note,current_time,])
                
                # 手動處理 Note 欄位，將其用雙引號包裹
                formatted_note = f'"{self.note}"'  # 包住 Note 欄位以防逗號分隔
                file.write(f"{self.station_name},{self.operator_name},{name},{formatted_note},{current_time},")                    
            QtWidgets.QMessageBox.information(None, "訊息", f"開始時間已記錄至 {file_name}!")


    def toggle_buttons(self, enable, exclude=None):
        """切換按鈕啟用狀態。"""
        for btn in self.buttons.values():
            btn.setEnabled(enable or btn == exclude)

    def display_datetime(self):
        """顯示當前時間。"""
        now = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        self.ui.time_label.setText(now)

    def open_folder(self):
        """選擇目錄存放路徑。"""
        self.folder_path = QFileDialog.getExistingDirectory(None, "Open folder", "./")
        self.ui.path_textEdit.setText(self.folder_path)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("站點工時紀錄-程式Ver2.2 2025-01-21 by_Curtis")
        self.setWindowIcon(QIcon(r'C:\Users\T450\Desktop\VS Code_program\PyQt5-Qt Designer\test1\Oxygen-Icons.org-Oxygen-Apps-preferences-system-time.256.png'))
        #self.setGeometry(250, 250, 590, 300)  # 更新視窗大小以適應多標籤頁
        self.setFixedSize(590,310)
        # 創建 TabWidget 並設置為中央視窗
        self.tabWidget = TabWidget(self)
        self.setCentralWidget(self.tabWidget)

