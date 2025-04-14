from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLineEdit, QSizePolicy, QLabel, QMessageBox
)
import sys
import requests


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_employee_id = None
        self.setup_ui()
        self.get_all_employees()

    def setup_ui(self):
        self.setWindowTitle("Управление сотрудниками")
        self.setFixedSize(QSize(900, 650))

        # Главный контейнер
        main_container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # Верхняя панель с кнопками
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.btn_get_all = QPushButton("Обновить список")
        self.btn_get_one = QPushButton("Найти по ID")
        self.btn_create = QPushButton("Добавить")
        self.btn_update = QPushButton("Сохранить")
        self.btn_delete = QPushButton("Удалить")

        # Стилизация кнопок
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """
        for btn in [self.btn_get_all, self.btn_get_one, self.btn_create,
                    self.btn_update, self.btn_delete]:
            btn.setStyleSheet(button_style)

        button_layout.addWidget(self.btn_get_all)
        button_layout.addWidget(self.btn_get_one)
        button_layout.addWidget(self.btn_create)
        button_layout.addWidget(self.btn_update)
        button_layout.addWidget(self.btn_delete)
        button_container.setLayout(button_layout)

        # Поля ввода с подписями
        input_container = QWidget()
        input_layout = QHBoxLayout()
        input_layout.setSpacing(20)

        # Группа для ФИО
        name_group = QWidget()
        name_layout = QVBoxLayout()
        name_layout.addWidget(QLabel("ФИО сотрудника:"))
        self.input_name = QLineEdit()
        self.input_name.setFixedSize(300, 35)
        self.input_name.setPlaceholderText("Введите ФИО")
        name_layout.addWidget(self.input_name)
        name_group.setLayout(name_layout)

        # Группа для должности
        position_group = QWidget()
        position_layout = QVBoxLayout()
        position_layout.addWidget(QLabel("Должность:"))
        self.input_position = QLineEdit()
        self.input_position.setFixedSize(300, 35)
        self.input_position.setPlaceholderText("Введите должность")
        position_layout.addWidget(self.input_position)
        position_group.setLayout(position_layout)

        input_layout.addWidget(name_group)
        input_layout.addWidget(position_group)
        input_container.setLayout(input_layout)

        # Таблица сотрудников
        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(3)  # ФИО, Должность, ID (скрыт)
        self.table.setHorizontalHeaderLabels(["ФИО", "Должность", "ID"])
        self.table.setColumnHidden(2, True)  # Скрываем колонку с ID

        # Настройки таблицы
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Запрет редактирования

        # Стилизация таблицы
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                font-size: 14px;
                selection-background-color: #0026e6;
            }
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
        """)

        # Настройка столбцов
        self.table.setColumnWidth(0, 400)
        self.table.setColumnWidth(1, 300)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Подключение обработчика выделения строки
        self.table.itemSelectionChanged.connect(self.on_row_selected)

        # Добавление всех виджетов
        main_layout.addWidget(button_container)
        main_layout.addWidget(input_container)
        main_layout.addWidget(self.table, stretch=1)
        main_container.setLayout(main_layout)

        self.setCentralWidget(main_container)

        # Подключение кнопок
        self.btn_get_all.clicked.connect(self.get_all_employees)
        self.btn_get_one.clicked.connect(self.get_employee_by_id)
        self.btn_create.clicked.connect(self.create_employee)
        self.btn_update.clicked.connect(self.update_employee)
        self.btn_delete.clicked.connect(self.delete_employee)

    def on_row_selected(self):
        """Обработчик выделения строки в таблице"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.input_name.setText(self.table.item(row, 0).text())
            self.input_position.setText(self.table.item(row, 1).text())
            self.selected_employee_id = self.table.item(row, 2).text()

    def get_all_employees(self):
        try:
            response = requests.get('http://127.0.0.1:5000/employees')
            if response.status_code == 200:
                employees = response.json()
                self.table.setRowCount(0)

                for row, employee in enumerate(employees):
                    self.table.insertRow(row)

                    # Создаем элементы таблицы с запретом редактирования
                    name_item = QTableWidgetItem(employee['name'])
                    name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                    position_item = QTableWidgetItem(employee['position'])
                    position_item.setFlags(position_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                    id_item = QTableWidgetItem(str(employee['id']))
                    id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                    self.table.setItem(row, 0, name_item)
                    self.table.setItem(row, 1, position_item)
                    self.table.setItem(row, 2, id_item)

                if employees:
                    QMessageBox.information(self, "Успех", f"Загружено {len(employees)} сотрудников")
                else:
                    QMessageBox.information(self, "Информация", "Список сотрудников пуст")
            else:
                QMessageBox.warning(self, "Ошибка", f"Ошибка сервера: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к серверу:\n{str(e)}")

    def get_employee_by_id(self):
        employee_id = self.input_name.text().strip()
        if not employee_id:
            QMessageBox.warning(self, "Ошибка", "Введите ID сотрудника")
            return

        try:
            response = requests.get(f'http://127.0.0.1:5000/employees/{employee_id}')
            if response.status_code == 200:
                employee = response.json()
                self.table.setRowCount(0)
                self.table.insertRow(0)

                name_item = QTableWidgetItem(employee['name'])
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                position_item = QTableWidgetItem(employee['position'])
                position_item.setFlags(position_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                id_item = QTableWidgetItem(str(employee['id']))
                id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                self.table.setItem(0, 0, name_item)
                self.table.setItem(0, 1, position_item)
                self.table.setItem(0, 2, id_item)

                self.input_name.setText(employee['name'])
                self.input_position.setText(employee['position'])
                self.selected_employee_id = str(employee['id'])
            else:
                QMessageBox.warning(self, "Ошибка", response.json().get('error', 'Сотрудник не найден'))
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {str(e)}")

    def create_employee(self):
        name = self.input_name.text().strip()
        position = self.input_position.text().strip()

        if not name or not position:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            response = requests.post(
                'http://127.0.0.1:5000/employees',
                json={'name': name, 'position': position},
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 201:
                QMessageBox.information(self, "Успех", "Сотрудник добавлен")
                self.input_name.clear()
                self.input_position.clear()
                self.get_all_employees()
            else:
                QMessageBox.warning(self, "Ошибка", response.text)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {str(e)}")

    def update_employee(self):
        if not self.selected_employee_id:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника из таблицы")
            return

        name = self.input_name.text().strip()
        position = self.input_position.text().strip()

        if not name or not position:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            response = requests.put(
                f'http://127.0.0.1:5000/employees/{self.selected_employee_id}',
                json={'name': name, 'position': position},
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                QMessageBox.information(self, "Успех", "Данные обновлены")
                self.get_all_employees()
            else:
                QMessageBox.warning(self, "Ошибка", response.text)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {str(e)}")

    def delete_employee(self):
        if not self.selected_employee_id:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника из таблицы")
            return

        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить этого сотрудника?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                response = requests.delete(
                    f'http://127.0.0.1:5000/employees/{self.selected_employee_id}'
                )

                if response.status_code == 200:
                    QMessageBox.information(self, "Успех", "Сотрудник удален")
                    self.get_all_employees()
                    self.input_name.clear()
                    self.input_position.clear()
                    self.selected_employee_id = None
                else:
                    QMessageBox.warning(self, "Ошибка", response.text)
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QLabel {
            font-size: 14px;
            font-weight: bold;
        }
        QLineEdit {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            font-size: 14px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())