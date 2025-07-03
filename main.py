import sys
import subprocess
import winreg
import re
import json
import os
import ctypes
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QListWidget, QMessageBox, QTabWidget,
                             QGroupBox, QGridLayout, QCheckBox, QTextEdit, QStyleFactory,
                             QMenu, QMenuBar, QComboBox, QSizePolicy)
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QPixmap,QAction,QIcon
from PyQt6.QtCore import Qt, QTranslator, QLocale

class PowerManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 初始化语言
        self.translator = QTranslator()
        self.current_language = "en_US"
        self.languages = {
            "en_US": "English",
            "zh_CN": "简体中文",
            "es_ES": "Español",
            "fr_FR": "Français",
            "de_DE": "Deutsch"
        }
        
        # 加载语言
        self.load_language()
        
        # 电源计划GUID
        self.power_guids = {
            self.tr("节能"): "a1841308-3541-4fab-bc81-f71556f20b4a",
            self.tr("平衡"): "381b4222-f694-41f0-9685-ff5bb260df2e",
            self.tr("高性能"): "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
            self.tr("卓越性能"): "e9a42b02-d5df-448d-aa00-03f14749eb61"
        }
        
        self.initUI()
        self.refresh_power_plans()
        self.check_registry_settings()
        
    def load_language(self):
        """加载当前语言设置"""
        # 尝试加载语言文件
        lang_file = f"locales/{self.current_language}.json"
        if os.path.exists(lang_file):
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    self.translations = json.load(f)
                print(f"成功加载语言文件: {self.current_language}")
            except:
                print(f"无法加载语言文件: {self.current_language}")
                self.translations = {}
        else:
            print(f"语言文件不存在: {lang_file}")
            self.translations = {}
    
    def tr(self, text):
        """自定义翻译函数"""
        return self.translations.get(text, text)
    
    def initUI(self):
        """初始化用户界面"""
        self.setWindowTitle(self.tr('高级电源管理工具'))
        self.setGeometry(300, 300, 850, 650)
        self.setWindowIcon(QIcon('icon/power_manager.ico'))
        
        # 设置应用样式
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        
        # 创建深色调色板
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197).lighter())
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(dark_palette)
        
        # 创建菜单栏
        self.create_menus()
        
        # 创建主标签页
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # 创建电源计划标签页
        self.power_tab = QWidget()
        self.tabs.addTab(self.power_tab, self.tr("电源计划"))
        self.create_power_plan_tab()
        
        # 创建高级设置标签页
        self.advanced_tab = QWidget()
        self.tabs.addTab(self.advanced_tab, self.tr("高级设置"))
        self.create_advanced_tab()
        
        # 创建关于标签页
        self.about_tab = QWidget()
        self.tabs.addTab(self.about_tab, self.tr("关于"))
        self.create_about_tab()
        
        # 状态栏
        self.statusBar().showMessage(self.tr("就绪"))
    
    def create_menus(self):
        """创建菜单栏"""
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu(self.tr("文件"))
        
        # 语言菜单
        lang_menu = menu_bar.addMenu(self.tr("语言"))
        
        # 创建语言选项
        for lang_code, lang_name in self.languages.items():
            action = QAction(lang_name, self)
            action.setData(lang_code)
            action.triggered.connect(self.change_language)
            lang_menu.addAction(action)
        
        # 退出动作
        exit_action = QAction(self.tr("退出"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def change_language(self):
        """更改应用程序语言"""
        action = self.sender()
        lang_code = action.data()
        
        if lang_code != self.current_language:
            self.current_language = lang_code
            self.load_language()
            
            # 更新UI
            self.update_ui_text()
            
            # 更新状态栏
            self.statusBar().showMessage(self.tr("语言已切换到: ") + self.languages[lang_code])
    
    def update_ui_text(self):
        """更新所有UI文本以反映新语言"""
        # 更新窗口标题
        self.setWindowTitle(self.tr('高级电源管理工具'))
        
        # 更新标签页标题
        self.tabs.setTabText(0, self.tr("电源计划"))
        self.tabs.setTabText(1, self.tr("高级设置"))
        self.tabs.setTabText(2, self.tr("关于"))
        
        # 更新电源计划标签页
        self.title.setText(self.tr("电源计划管理"))
        self.active_plan_label.setText(self.tr("当前激活计划: ") + self.active_plan_name)
        self.eco_btn.setText(self.tr("节能模式"))
        self.balanced_btn.setText(self.tr("平衡模式"))
        self.high_perf_btn.setText(self.tr("高性能模式"))
        self.ultimate_btn.setText(self.tr("卓越性能模式"))
        self.plan_list_label.setText(self.tr("当前电源计划列表:"))
        self.refresh_btn.setText(self.tr("刷新列表"))
        self.delete_btn.setText(self.tr("删除选中计划"))
        
        # 更新高级设置标签页
        self.advanced_title.setText(self.tr("高级电源设置"))
        self.warning.setText(self.tr("警告: 以下高级设置可能影响系统稳定性或功能!"))
        self.reg_group.setTitle(self.tr("注册表设置"))
        self.reg_info.setText(self.tr("修改 PlatformAoAcOverride 注册表值可能禁用现代待机功能，\n"
                                      "导致睡眠选项消失，但可能解决某些电源计划问题。"))
        self.reg_checkbox.setText(self.tr("设置 PlatformAoAcOverride = 0"))
        self.apply_reg_btn.setText(self.tr("应用注册表设置"))
        self.cmd_group.setTitle(self.tr("执行PowerShell命令"))
        self.cmd_input.setPlaceholderText(self.tr("在此输入PowerShell命令..."))
        self.execute_btn.setText(self.tr("执行命令"))
        self.clear_btn.setText(self.tr("清除"))
        
        # 更新关于标签页
        self.about_title.setText(self.tr("高级电源管理工具"))
        self.version.setText(self.tr("版本 1.0"))
        self.features.setText(self.tr("功能:\n"
                                      "• 快速切换电源计划（节能、平衡、高性能、卓越性能）\n"
                                      "• 查看和管理所有电源计划\n"
                                      "• 修改高级电源相关注册表设置\n"
                                      "• 执行自定义PowerShell命令"))
        self.warning_label.setText(self.tr("注意:\n"
                                           "• 某些操作需要管理员权限\n"
                                           "• 修改注册表设置可能导致系统不稳定\n"
                                           "• 删除电源计划操作不可逆"))
        self.copyright.setText(self.tr("© 2025 高级电源管理工具 | 保留所有权利"))
        
        # 更新菜单
        self.menuBar().actions()[0].setText(self.tr("文件"))
        self.menuBar().actions()[1].setText(self.tr("语言"))
        self.menuBar().actions()[0].menu().actions()[-1].setText(self.tr("退出"))
        
        # 更新状态栏
        self.statusBar().showMessage(self.tr("就绪"))
    
    def create_power_plan_tab(self):
        """创建电源计划标签页"""
        layout = QVBoxLayout(self.power_tab)
        
        # 标题
        self.title = QLabel(self.tr("电源计划管理"))
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        self.title.setFont(title_font)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)
        
        # 当前激活计划显示
        self.active_plan_label = QLabel(self.tr("当前激活计划: "))
        self.active_plan_label.setFont(QFont("Arial", 10))
        layout.addWidget(self.active_plan_label)
        
        # 分隔线
        layout.addWidget(QLabel(""))
        
        # 创建切换按钮区域
        btn_layout = QGridLayout()
        
        # 创建切换按钮
        self.eco_btn = QPushButton(self.tr("节能模式"))
        self.eco_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.eco_btn.clicked.connect(lambda: self.set_power_plan(self.tr("节能")))
        
        self.balanced_btn = QPushButton(self.tr("平衡模式"))
        self.balanced_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        self.balanced_btn.clicked.connect(lambda: self.set_power_plan(self.tr("平衡")))
        
        self.high_perf_btn = QPushButton(self.tr("高性能模式"))
        self.high_perf_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        self.high_perf_btn.clicked.connect(lambda: self.set_power_plan(self.tr("高性能")))
        
        self.ultimate_btn = QPushButton(self.tr("卓越性能模式"))
        self.ultimate_btn.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold;")
        self.ultimate_btn.clicked.connect(lambda: self.set_power_plan(self.tr("卓越性能")))
        
        # 添加到布局
        btn_layout.addWidget(self.eco_btn, 0, 0)
        btn_layout.addWidget(self.balanced_btn, 0, 1)
        btn_layout.addWidget(self.high_perf_btn, 1, 0)
        btn_layout.addWidget(self.ultimate_btn, 1, 1)
        
        layout.addLayout(btn_layout)
        
        # 分隔线
        layout.addWidget(QLabel(""))
        
        # 电源计划列表
        self.plan_list_label = QLabel(self.tr("当前电源计划列表:"))
        self.plan_list_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.plan_list_label)
        
        self.plan_list = QListWidget()
        self.plan_list.setFont(QFont("Consolas", 9))
        layout.addWidget(self.plan_list)
        
        # 操作按钮
        btn_layout2 = QHBoxLayout()
        
        self.refresh_btn = QPushButton(self.tr("刷新列表"))
        self.refresh_btn.setStyleSheet("background-color: #607D8B; color: white;")
        self.refresh_btn.clicked.connect(self.refresh_power_plans)
        
        self.delete_btn = QPushButton(self.tr("删除选中计划"))
        self.delete_btn.setStyleSheet("background-color: #F44336; color: white;")
        self.delete_btn.clicked.connect(self.delete_selected_plan)
        
        btn_layout2.addWidget(self.refresh_btn)
        btn_layout2.addWidget(self.delete_btn)
        
        layout.addLayout(btn_layout2)
        
        # 添加一些间距
        layout.addStretch(1)
    
    def create_advanced_tab(self):
        """创建高级设置标签页"""
        layout = QVBoxLayout(self.advanced_tab)
        
        # 标题
        self.advanced_title = QLabel(self.tr("高级电源设置"))
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        self.advanced_title.setFont(title_font)
        self.advanced_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.advanced_title)
        
        # 警告框
        self.warning = QLabel(self.tr("警告: 以下高级设置可能影响系统稳定性或功能!"))
        self.warning.setStyleSheet("color: #FF5722; font-weight: bold;")
        self.warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.warning)
        
        # 分隔线
        layout.addWidget(QLabel(""))
        
        # 注册表设置组
        self.reg_group = QGroupBox(self.tr("注册表设置"))
        reg_layout = QVBoxLayout(self.reg_group)
        
        # 注册表设置说明
        self.reg_info = QLabel(self.tr("修改 PlatformAoAcOverride 注册表值可能禁用现代待机功能，\n"
                                      "导致睡眠选项消失，但可能解决某些电源计划问题。"))
        self.reg_info.setWordWrap(True)
        reg_layout.addWidget(self.reg_info)
        
        # 注册表设置复选框
        self.reg_checkbox = QCheckBox(self.tr("设置 PlatformAoAcOverride = 0"))
        self.reg_checkbox.setFont(QFont("Arial", 10))
        self.reg_checkbox.stateChanged.connect(self.toggle_registry_setting)
        reg_layout.addWidget(self.reg_checkbox)
        
        # 应用按钮
        self.apply_reg_btn = QPushButton(self.tr("应用注册表设置"))
        self.apply_reg_btn.setStyleSheet("background-color: #673AB7; color: white;")
        self.apply_reg_btn.clicked.connect(self.apply_registry_settings)
        reg_layout.addWidget(self.apply_reg_btn)
        
        layout.addWidget(self.reg_group)
        
        # 添加间距
        layout.addWidget(QLabel(""))
        
        # 命令执行区域
        self.cmd_group = QGroupBox(self.tr("执行PowerShell命令"))
        cmd_layout = QVBoxLayout(self.cmd_group)
        
        self.cmd_input = QTextEdit()
        self.cmd_input.setPlaceholderText(self.tr("在此输入PowerShell命令..."))
        self.cmd_input.setFont(QFont("Consolas", 9))
        cmd_layout.addWidget(self.cmd_input)
        
        # 命令按钮
        cmd_btn_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton(self.tr("执行命令"))
        self.execute_btn.setStyleSheet("background-color: #009688; color: white;")
        self.execute_btn.clicked.connect(self.execute_command)
        
        self.clear_btn = QPushButton(self.tr("清除"))
        self.clear_btn.setStyleSheet("background-color: #795548; color: white;")
        self.clear_btn.clicked.connect(lambda: self.cmd_input.clear())
        
        cmd_btn_layout.addWidget(self.execute_btn)
        cmd_btn_layout.addWidget(self.clear_btn)
        
        cmd_layout.addLayout(cmd_btn_layout)
        
        layout.addWidget(self.cmd_group)
        
        # 添加一些间距
        layout.addStretch(1)
    
    def create_about_tab(self):
        """创建关于标签页"""
        layout = QVBoxLayout(self.about_tab)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 标题
        self.about_title = QLabel(self.tr("高级电源管理工具"))
        title_font = QFont("Arial", 20, QFont.Weight.Bold)
        self.about_title.setFont(title_font)
        self.about_title.setStyleSheet("color: #2196F3;")
        layout.addWidget(self.about_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 版本信息
        self.version = QLabel(self.tr("版本 1.0"))
        self.version.setFont(QFont("Arial", 12))
        layout.addWidget(self.version, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 分隔线
        layout.addWidget(QLabel(""))
        
        # 语言选择
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()
        
        lang_label = QLabel(self.tr("选择语言:"))
        lang_label.setFont(QFont("Arial", 10))
        lang_layout.addWidget(lang_label)
        
        self.lang_combo = QComboBox()
        for lang_code, lang_name in self.languages.items():
            self.lang_combo.addItem(lang_name, lang_code)
        self.lang_combo.setCurrentText(self.languages[self.current_language])
        self.lang_combo.currentIndexChanged.connect(self.change_language_from_combo)
        lang_layout.addWidget(self.lang_combo)
        
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # 分隔线
        layout.addWidget(QLabel(""))
        
        # 功能列表
        self.features = QLabel(self.tr("功能:\n"
                                      "• 快速切换电源计划（节能、平衡、高性能、卓越性能）\n"
                                      "• 查看和管理所有电源计划\n"
                                      "• 修改高级电源相关注册表设置\n"
                                      "• 执行自定义PowerShell命令"))
        self.features.setFont(QFont("Arial", 11))
        layout.addWidget(self.features)
        
        # 分隔线
        layout.addWidget(QLabel(""))
        
        # 警告信息
        self.warning_label = QLabel(self.tr("注意:\n"
                                           "• 某些操作需要管理员权限\n"
                                           "• 修改注册表设置可能导致系统不稳定\n"
                                           "• 删除电源计划操作不可逆"))
        self.warning_label.setStyleSheet("color: #FF5722;")
        self.warning_label.setFont(QFont("Arial", 10))
        layout.addWidget(self.warning_label)
        
        # 添加一些间距
        layout.addStretch(1)
        
        # 版权信息
        self.copyright = QLabel(self.tr("© 2023 高级电源管理工具 | 保留所有权利"))
        self.copyright.setFont(QFont("Arial", 9))
        self.copyright.setStyleSheet("color: #9E9E9E;")
        layout.addWidget(self.copyright, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def change_language_from_combo(self):
        """从组合框更改语言"""
        lang_code = self.lang_combo.currentData()
        if lang_code != self.current_language:
            self.current_language = lang_code
            self.load_language()
            self.update_ui_text()
            self.statusBar().showMessage(self.tr("语言已切换到: ") + self.languages[lang_code])
    
    def refresh_power_plans(self):
        """刷新电源计划列表"""
        self.plan_list.clear()
        
        try:
            # 获取电源计划列表
            result = subprocess.run(["powercfg", "/L"], capture_output=True, text=True, check=True)
            output = result.stdout
            
            # 解析输出
            lines = output.split('\n')
            self.active_plan_name = ""
            
            for line in lines:
                if "电源方案" in line or "Power Scheme" in line:
                    # 提取GUID和名称
                    match = re.search(r'电源方案: (\S+) \(([^)]+)\)|Power Scheme: (\S+) \(([^)]+)\)', line)
                    if match:
                        if match.group(1):  # 中文匹配
                            guid = match.group(1)
                            name = match.group(2)
                        else:  # 英文匹配
                            guid = match.group(3)
                            name = match.group(4)
                        
                        # 检查是否是当前激活的计划
                        if '*' in line:
                            self.active_plan_name = name
                            self.active_plan_label.setText(self.tr("当前激活计划: ") + name)
                            item_text = f"[{self.tr('激活')}] {name} ({guid})"
                        else:
                            item_text = f"{name} ({guid})"
                        
                        self.plan_list.addItem(item_text)
            
            # 更新状态栏
            self.statusBar().showMessage(self.tr("已加载 {0} 个电源计划").format(self.plan_list.count()))
            
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, self.tr("错误"), self.tr("获取电源计划失败:\n{0}").format(e.stderr))
    
    def set_power_plan(self, plan_name):
        """设置指定的电源计划"""
        guid = self.power_guids.get(plan_name)
        if not guid:
            QMessageBox.warning(self, self.tr("错误"), self.tr("找不到 {0} 的GUID").format(plan_name))
            return
        
        try:
            # 复制电源方案（如果不存在）
            subprocess.run(["powercfg", "-duplicatescheme", guid], check=True, stdout=subprocess.DEVNULL)
            
            # 激活电源方案
            subprocess.run(["powercfg", "-setactive", guid], check=True)
            
            # 刷新列表
            self.refresh_power_plans()
            
            # 显示成功消息
            QMessageBox.information(self, self.tr("成功"), self.tr("已切换到 {0} 模式").format(plan_name))
            self.statusBar().showMessage(self.tr("已切换到 {0} 模式").format(plan_name))
            
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, self.tr("错误"), self.tr("切换电源计划失败:\n{0}").format(e.stderr))
    
    def delete_selected_plan(self):
        """删除选中的电源计划"""
        selected_items = self.plan_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.tr("警告"), self.tr("请先选择一个电源计划"))
            return
        
        selected_text = selected_items[0].text()
        
        # 提取GUID
        match = re.search(r'\(([a-fA-F0-9\-]+)\)', selected_text)
        if not match:
            QMessageBox.warning(self, self.tr("错误"), self.tr("无法从选中项中提取GUID"))
            return
        
        guid = match.group(1)
        
        # 检查是否是系统内置计划
        if guid in self.power_guids.values():
            QMessageBox.warning(self, self.tr("警告"), self.tr("无法删除系统内置电源计划!"))
            return
        
        # 确认对话框
        reply = QMessageBox.question(
            self, self.tr("确认删除"),
            self.tr("确定要删除电源计划?\n{0}").format(selected_text),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 删除电源计划
                subprocess.run(["powercfg", "/d", guid], check=True)
                
                # 刷新列表
                self.refresh_power_plans()
                
                QMessageBox.information(self, self.tr("成功"), self.tr("电源计划已成功删除"))
                self.statusBar().showMessage(self.tr("电源计划已删除"))
                
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, self.tr("错误"), self.tr("删除电源计划失败:\n{0}").format(e.stderr))
    
    def check_registry_settings(self):
        """检查注册表设置状态"""
        try:
            # 打开注册表键
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"System\CurrentControlSet\Control\Power",
                0,
                winreg.KEY_READ
            )
            
            # 读取值
            value, _ = winreg.QueryValueEx(key, "PlatformAoAcOverride")
            
            # 更新复选框状态
            self.reg_checkbox.setChecked(value == 0)
            
            # 关闭键
            winreg.CloseKey(key)
            
        except FileNotFoundError:
            # 键不存在
            self.reg_checkbox.setChecked(False)
        except Exception as e:
            QMessageBox.warning(self, self.tr("注册表错误"), self.tr("读取注册表失败: {0}").format(str(e)))
    
    def toggle_registry_setting(self, state):
        """切换注册表设置复选框状态"""
        if state == Qt.CheckState.Checked.value:
            self.reg_checkbox.setText(self.tr("设置 PlatformAoAcOverride = 0 (已选中)"))
        else:
            self.reg_checkbox.setText(self.tr("设置 PlatformAoAcOverride = 0"))
    
    def apply_registry_settings(self):
        """应用注册表设置"""
        value = 0 if self.reg_checkbox.isChecked() else None
        
        try:
            # 打开注册表键（可写）
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"System\CurrentControlSet\Control\Power",
                0,
                winreg.KEY_WRITE
            )
            
            if value is not None:
                # 设置值
                winreg.SetValueEx(key, "PlatformAoAcOverride", 0, winreg.REG_DWORD, value)
                status = self.tr("已设置") if value == 0 else self.tr("已删除")
                QMessageBox.information(self, self.tr("成功"), self.tr("注册表设置已更新: {0}").format(status))
                self.statusBar().showMessage(self.tr("注册表更新: PlatformAoAcOverride = {0}").format(value))
            else:
                # 删除值
                winreg.DeleteValue(key, "PlatformAoAcOverride")
                QMessageBox.information(self, self.tr("成功"), self.tr("注册表设置已删除"))
                self.statusBar().showMessage(self.tr("注册表设置已删除"))
            
            # 关闭键
            winreg.CloseKey(key)
            
        except PermissionError:
            QMessageBox.critical(
                self, self.tr("权限错误"), 
                self.tr("需要管理员权限修改注册表!\n请以管理员身份运行此程序。")
            )
        except Exception as e:
            QMessageBox.critical(self, self.tr("错误"), self.tr("更新注册表失败: {0}").format(str(e)))
    
    def execute_command(self):
        """执行PowerShell命令"""
        command = self.cmd_input.toPlainText().strip()
        if not command:
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("请输入要执行的命令"))
            return
        
        try:
            # 执行命令
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                check=True
            )
            
            # 显示结果
            output = result.stdout if result.stdout else self.tr("命令执行成功，无输出")
            QMessageBox.information(self, self.tr("命令执行结果"), output)
            self.statusBar().showMessage(self.tr("命令执行成功"))
            
        except subprocess.CalledProcessError as e:
            error_msg = self.tr("命令执行失败:\n错误代码: {0}\n错误信息: {1}").format(e.returncode, e.stderr)
            QMessageBox.critical(self, self.tr("错误"), error_msg)
            self.statusBar().showMessage(self.tr("命令执行失败"))
    
    def closeEvent(self, event):
        """关闭窗口时的事件处理"""
        reply = QMessageBox.question(
            self, self.tr("确认退出"),
            self.tr("确定要退出电源管理工具吗?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    # 检查是否以管理员身份运行
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            # 请求管理员权限
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, None, 1
            )
            sys.exit(0)
    except:
        pass
    app = QApplication(sys.argv)
    window = PowerManager()
    window.show()
    sys.exit(app.exec())