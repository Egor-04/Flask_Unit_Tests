from werkzeug.utils import get_content_type

from main import *
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton, QInputDialog, QTextEdit, QLineEdit,
)

import sys

import main


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Employee Table")
        self.setFixedSize(QSize(600, 400))

        # Таблица для сотрудников
        self.table = QTableWidget(self)
        self.table.setRowCount(0)  # Строки
        self.table.setColumnCount(2)  # Столбцы
        self.table.setHorizontalHeaderLabels(["Name", "Position"])

        # Кнопки
        self.btn_get_all = QPushButton("Get All Employees")
        self.btn_get_one = QPushButton("Get Employee by ID")
        self.btn_update = QPushButton("Update Employee")
        self.btn_delete = QPushButton("Delete Employee")

        # Подключаем кнопки к методам
        self.btn_get_all.clicked.connect(self.get_all_employees)
        self.btn_get_one.clicked.connect(self.get_employee_by_id)
        self.btn_update.clicked.connect(self.update_employee)
        self.btn_delete.clicked.connect(self.delete_employee)

        # Форма ввода для ID
        self.input_field_id = QLineEdit(self)
        self.input_field_id.setFixedSize(QSize(150, 20))

        # Контейнер для строки ввода ID
        input_field_container = QWidget()
        input_field_layout = QVBoxLayout()
        input_field_layout.addWidget(self.input_field_id)
        input_field_container.setLayout(input_field_layout)

        # Создаем контейнер для кнопок
        button_container = QWidget()
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.btn_get_all)
        button_layout.addWidget(self.btn_get_one)
        button_layout.addWidget(self.btn_update)
        button_layout.addWidget(self.btn_delete)
        button_container.setLayout(button_layout)

        # Создаем основной контейнер для таблицы и кнопок
        main_container = QWidget()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.table)
        main_layout.addWidget(button_container)
        main_layout.addWidget(input_field_container)
        main_container.setLayout(main_layout)

        self.setCentralWidget(main_container)

    def get_all_employees(self):
        try:
            with main.app.app_context():
                response_tuple = main.get_employees_list()
                response = response_tuple[0]
                employees_list = response.get_json()  # Получаем список сотрудников

                # Очищаем таблицу перед добавлением новых данных
                self.table.setRowCount(0)

                # Добавляем всех сотрудников из списка
                for row, employee_data in enumerate(employees_list):
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(employee_data['name']))
                    self.table.setItem(row, 1, QTableWidgetItem(employee_data['position']))
                print('Список успешно обновлен!')
        except Exception as ex:
            print(f"Error: {ex}")


    def get_employee_by_id(self):
        try:
            with main.app.app_context():
                employee_id = int(self.input_field_id.text())
                response_tuple = main.get_employee(employee_id)
                response = response_tuple[0]
                data = response.get_json()

                # Проверяем, существует ли уже такой сотрудник в таблице
                employee_exists = False
                for row in range(self.table.rowCount()):
                    # Если нет, можно сравнивать по имени и должности
                    if (self.table.item(row, 0).text() == data['name'] and
                            self.table.item(row, 1).text() == data['position']):
                        employee_exists = True
                        break

                if not employee_exists:
                    # Добавляем новую строку
                    current_row = self.table.rowCount()
                    self.table.insertRow(current_row)

                    # Заполняем данные
                    self.table.setItem(current_row, 0, QTableWidgetItem(data['name']))
                    self.table.setItem(current_row, 1, QTableWidgetItem(data['position']))

                    # Можно добавить ID в скрытую колонку, если нужно
                    # self.table.setItem(current_row, 2, QTableWidgetItem(str(employee_id)))
                else:
                    print(f"Сотрудник {data['name']} уже есть в таблице")

        except Exception as ex:
            print(f"Error: {ex}")


    def update_employee(self):
        pass

    def delete_employee(self):
        pass


app = QApplication(sys.argv)

# Создаём виджет Qt — окно.
window = MainWindow()
window.show()  # Важно: окно по умолчанию скрыто.

# Запускаем цикл событий.
app.exec()
