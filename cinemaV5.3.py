import sys
from PyQt5.QtWidgets import (QDialog, QApplication, QWidget, QLabel, QFrame,
 QLineEdit, QPushButton, QVBoxLayout, QCheckBox, QMessageBox, QListWidget, QHBoxLayout,QComboBox,QTextEdit,QGridLayout, QListWidgetItem)
from PyQt5.QtCore import Qt
import requests
from datetime import date
from PyQt5.QtGui import QTextCursor, QTextBlockFormat

class UsersWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Users")
        self.setFixedSize(500, 700)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Filter input
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Search users by name")
        self.filter_edit.setFixedHeight(40)
        self.filter_edit.setStyleSheet(
            "font-size: 18px; padding: 5px; border: 1px solid #bdc3c7; border-radius: 5px;"
        )
        self.filter_edit.textChanged.connect(self.filter_users)
        layout.addWidget(self.filter_edit)

        # Title label
        title = QLabel("Users")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;"
        )
        layout.addWidget(title)

        # Subtitle label
        subtitle = QLabel("Name - Password")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 18px; color: #7f8c8d;")
        layout.addWidget(subtitle)

        # User list
        self.user_list = QListWidget()
        self.user_list.setStyleSheet(
            """
            QListWidget {
                font-size: 20px; 
                border: 1px solid #bdc3c7; 
                border-radius: 8px; 
                background-color: #ecf0f1;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                outline: none;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
                outline: none;
            }
            """
        )
        self.user_list.addItems(
            requests.get('https://dair.pythonanywhere.com/getAllUsers').json()
        )
        self.user_list.itemClicked.connect(self.user_selected)
        layout.addWidget(self.user_list)

        self.setLayout(layout)

    def filter_users(self):
        """Filters the user list based on the input text."""
        filter_text = self.filter_edit.text().lower()
        for row in range(self.user_list.count()):
            item = self.user_list.item(row)
            item.setHidden(filter_text not in item.text().lower().split(' - ')[0])

    def user_selected(self, item):
        user_name = item.text().split(' - ')[0]
        self.hist = HistoryWindow(user_name)
        self.hist.show()

class MovieInformWindow(QDialog):
    def __init__(self, title, hall, session):
        self.title = title
        self.hall = hall
        self.session = session
        super().__init__()
        self.setWindowTitle("Movie Information")
        self.setFixedSize(650, 700)
        self.init_ui()

    def init_ui(self):
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(20, 20, 20, 20)

        # Film information label
        label_film_info = QLabel("Information about the Film")
        label_film_info.setAlignment(Qt.AlignCenter)
        label_film_info.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(label_film_info)

        # Film information text box
        text_edit_film_info = QTextEdit()
        text_edit_film_info.setStyleSheet(
            "font-size: 20px; background-color: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 8px; padding: 10px;"
        )
        text_edit_film_info.setReadOnly(True)
        pro = self.get_profit(self.title, self.hall, self.session)
        prof, sessions, hall = pro.get('profit', '')
        text_edit_film_info.setText(
            f"Title:     {self.title}\n"
            f"Profit:    {prof}\n"
            f"Quantity of halls:      {hall}\n"
            f"Quantity of sessions:   {sessions}"
        )
        text_edit_film_info.setFixedHeight(200)
        layout.addWidget(text_edit_film_info)

        # People information label
        label_people = QLabel("People Information\n(Name - Seat - Date - Time - Hall)")
        label_people.setAlignment(Qt.AlignCenter)
        label_people.setStyleSheet("font-size: 28px; font-weight: bold; color: #34495e;")
        layout.addWidget(label_people)

        # People information text box
        text_edit_people = QTextEdit()
        text_edit_people.setStyleSheet(
            "font-size: 20px; background-color: #fdfefe; border: 1px solid #bdc3c7; border-radius: 8px; padding: 10px;"
        )
        text_edit_people.setReadOnly(True)
        text_edit_people.setText(''.join(pro.get('users', '')))
        text_edit_people.setFixedHeight(300)
        self.center_text_in_text_edit(text_edit_people)
        layout.addWidget(text_edit_people)

        self.setLayout(layout)

    def center_text_in_text_edit(self, text_edit):
        cursor = text_edit.textCursor()
        block_format = QTextBlockFormat()
        block_format.setAlignment(Qt.AlignCenter)
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(block_format)
        cursor.clearSelection()
        text_edit.setTextCursor(cursor)

    def get_profit(self, title, hall, session):
        try:
            response = requests.get(
                'https://dair.pythonanywhere.com/getProfyt',
                params={'title': title, 'hall': hall, 'session': session}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch profit data: {e}")
            return {}
               
class HistoryWindow(QDialog):
    def __init__(self, user):
        self.user = user
        super().__init__()
        self.setWindowTitle("User History")
        self.setFixedSize(600, 700)
        self.init_ui()
        self.populate_data()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # Title label
        title_label = QLabel("History")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #34495e;")

        # Filters layout
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(15)

        # Filter inputs
        self.date_filter = QLineEdit()
        self.date_filter.setPlaceholderText("Filter by date")
        self.date_filter.setFixedHeight(40)
        self.date_filter.setStyleSheet(
            "font-size: 18px; border: 1px solid #bdc3c7; border-radius: 8px; padding-left: 10px;"
        )

        self.title_filter = QLineEdit()
        self.title_filter.setPlaceholderText("Filter by title")
        self.title_filter.setFixedHeight(40)
        self.title_filter.setStyleSheet(
            "font-size: 18px; border: 1px solid #bdc3c7; border-radius: 8px; padding-left: 10px;"
        )

        # Clear Filters button
        self.clear_button = QPushButton("Clear Filters")
        self.clear_button.setFixedHeight(40)
        self.clear_button.setStyleSheet(
            "background-color: #e74c3c; color: white; font-size: 18px; border-radius: 8px;"
            "padding: 10px;"
        )
        self.clear_button.clicked.connect(self.clear_filters)

        filters_layout.addWidget(self.date_filter)
        filters_layout.addWidget(self.title_filter)
        filters_layout.addWidget(self.clear_button)

        # Header label
        header_label = QLabel("Date - Time - Place - Movie - Hall")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")

        # History list widget
        self.history_list = QListWidget()
        self.history_list.setFrameShape(QFrame.Box)
        self.history_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #bdc3c7;
                font-size: 18px;
                background-color: #ecf0f1;
                border-radius: 8px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                outline: none;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
                outline: none;
            }
            """
        )

        # Connect filters to update function
        self.date_filter.textChanged.connect(self.filter_list)
        self.title_filter.textChanged.connect(self.filter_list)

        # Add widgets to the main layout
        main_layout.addWidget(title_label)
        main_layout.addLayout(filters_layout)
        main_layout.addWidget(header_label)
        main_layout.addWidget(self.history_list)

    def populate_data(self):
        """Populates the list with data from the server."""
        try:
            data = requests.get(
                "https://dair.pythonanywhere.com/getUserHistory",
                params={"user": self.user},
            ).json()
            for item in data:
                self.history_list.addItem(QListWidgetItem(item))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load history: {e}")

    def clear_filters(self):
        """Clears the filters."""
        self.date_filter.clear()
        self.title_filter.clear()

    def filter_list(self):
        """Filters the list based on the date and title filters."""
        date_text = self.date_filter.text().lower()
        title_text = self.title_filter.text().lower()

        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            item_text = item.text().lower()
            item.setHidden(
                (date_text not in item_text.split(" - ")[0])
                or (title_text not in item_text.split(" - ")[3]))
            
class SiteWindow(QDialog):
    def __init__(self, title, session, hall, user):
        super().__init__()
        self.title = title
        self.session = session
        self.hall = hall
        self.user = user
        self.setWindowTitle(title)

        self.setFixedSize(600, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f4;
                font-family: Arial, sans-serif;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 12px;
                font-size: 18px;
                padding: 10px 20px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1c7430;
            }
            QLabel {
                font-size: 16px;
            }
            QFrame {
                background-color: transparent;
            }
        """)
        #Unknown property transition

        self.selected_seats = []

        main_layout = QVBoxLayout()

        # Legend Layout
        legend_layout = QHBoxLayout()
        legend_layout.addLayout(self.create_legend_item("Free", "#ffffff"))
        legend_layout.addLayout(self.create_legend_item("Occupied", "#ff4d4d"))
        legend_layout.addLayout(self.create_legend_item("Your Seats", "#28a745"))
        legend_layout.setAlignment(Qt.AlignCenter)
        legend_layout.setSpacing(35)
        main_layout.addLayout(legend_layout)

        # Seat Grid Layout
        self.grid_layout = QGridLayout()
        self.seats = {}
        self.create_seat_grid()
        main_layout.addLayout(self.grid_layout)

        self.load_site()

        # Buttons Layout
        buttons_layout = QHBoxLayout()

        buy_button = QPushButton("Buy")
        buy_button.setFixedSize(150, 50)
        buy_button.setCursor(Qt.PointingHandCursor)
        buy_button.clicked.connect(self.buy_seats)
        buttons_layout.addWidget(buy_button, alignment=Qt.AlignCenter)

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(150, 50)
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4d; 
                color: white; 
                border-radius: 12px; 
                font-size: 18px; 
                padding: 10px 20px; 
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        cancel_button.clicked.connect(self.cancel_seats)
        buttons_layout.addWidget(cancel_button, alignment=Qt.AlignCenter)
        
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def create_legend_item(self, text, color):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Уменьшение отступов до минимума
        layout.setSpacing(1)
        square = QFrame()
        square.setFixedSize(20, 20)
        square.setStyleSheet(f"background-color: {color}; border: 1px solid #000;")
        label = QLabel(text)
        label.setStyleSheet("font-size: 16px; margin-left: 10px;")
        layout.addWidget(square)
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignLeft)
        return layout

    def create_seat_grid(self):
        for col in range(9):
            col_label = QLabel(str(col + 1))
            col_label.setAlignment(Qt.AlignCenter)
            col_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
            self.grid_layout.addWidget(col_label, 0, col + 1)

        for row in range(9):
            row_label = QLabel(chr(65 + row))
            row_label.setAlignment(Qt.AlignCenter)
            row_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
            self.grid_layout.addWidget(row_label, row + 1, 0)

        for row in range(9):
            for col in range(9):
                seat_button = QPushButton()
                seat_button.setFixedSize(50, 50)
                seat_button.setStyleSheet("background-color: #ffffff; border: 2px solid #ddd; border-radius: 8px;")
                seat_button.clicked.connect(lambda _, r=row, c=col: self.select_seat(r, c))
                self.grid_layout.addWidget(seat_button, row + 1, col + 1)
                self.seats[(row, col)] = seat_button

    def select_seat(self, row, col):
        seat_button = self.seats[(row, col)]
        current_color = seat_button.palette().button().color().name()

        if current_color == "#ffffff":
            seat_button.setStyleSheet("background-color: #28a745; border: 2px solid #28a745;")
            self.selected_seats.append((row, col))
        elif current_color == "#28a745":
            seat_button.setStyleSheet("background-color: #ffffff; border: 2px solid #ddd;")
            self.selected_seats.remove((row, col))

    def buy_seats(self):
        site = ','.join([f'{i}{v}' for i, v in self.selected_seats])
        requests.get('https://dair.pythonanywhere.com/saveSite', params={'user': self.user, 'title': self.title, 'hall': self.hall, 'session': self.session, 'site': site,'date': str(date.today()).replace('-', '.')})
        QMessageBox.information(self, "Site", "Your place(s) have been saved successfully!")

    def cancel_seats(self):
        for seat in self.selected_seats:
            row, col = seat
            self.seats[(row, col)].setStyleSheet("background-color: #ffffff; border: 2px solid #ddd;")
        self.selected_seats.clear()
        requests.get('https://dair.pythonanywhere.com/cancelSite', params={'user': self.user, 'title': self.title, 'hall': self.hall, 'session': self.session})
        QMessageBox.information(self, "Site", "Your reservations have been canceled!")
        self.load_site()

    def load_site(self):
        site = requests.get('https://dair.pythonanywhere.com/getSite', params={'title': self.title, 'hall': self.hall, 'session': self.session}).json()
        for row in range(9):
            for col in range(9):
                seat_button = self.seats[(row, col)]
                seat_name = site[row][col]
                if seat_name == self.user:
                    seat_button.setStyleSheet("background-color: #28a745; border: 2px solid #28a745;")
                    seat_button.setEnabled(False)
                elif seat_name:
                    seat_button.setStyleSheet("background-color: #ff4d4d; border: 2px solid #ff4d4d;")
                    seat_button.setEnabled(False)
                else:
                    seat_button.setStyleSheet("background-color: #ffffff; border: 2px solid #ddd;")
                    seat_button.setEnabled(True)

class AddMovieWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Movie")
        self.resize(600, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                background-color: #fff;
            }
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 8px 30px 8px 12px;
                font-size: 16px;
                background-color: #fff;
                color: #333;
                min-width: 200px;
                position: relative;
            }

            QComboBox::drop-down {
                border: none;
            }

            QComboBox QAbstractItemView {
                border-radius: 10px;
                background-color: #fff;
                border: 1px solid #ccc;
                selection-background-color: #28a745;
                selection-color: #fff;
                padding: 5px;
                margin: 2px;
            }

            QComboBox QAbstractItemView::item {
                padding: 10px;
                font-size: 16px;
                border-radius: 8px;
            }

            QComboBox QAbstractItemView::item:hover {
                background-color: #f0f0f0;
                color: #333;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 16px;
                padding: 10px;
                background-color: #fff;
                min-height: 100px;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 12px;
                font-size: 18px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #ddd;
                color: #888;
            }
        """)

        layout = QVBoxLayout()

        # Заголовок и поля для ввода данных
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Movie Title")
        layout.addWidget(self.title_input)

        self.hall_combobox = QComboBox()
        self.hall_combobox.addItems([f"Hall №{i}" for i in range(1, 4)])
        layout.addWidget(self.hall_combobox)

        self.session_label = QLabel("Sessions:")
        self.session_input = QTextEdit()
        self.session_input.setPlaceholderText("Enter session times, each on a new line")
        layout.addWidget(self.session_label)
        layout.addWidget(self.session_input)

        # Кнопка добавления фильма
        self.add_button = QPushButton("Add Movie")
        layout.addWidget(self.add_button)

        self.setLayout(layout)

        # Связывание кнопки с методом
        self.add_button.clicked.connect(self.add_movie)
        self.hall_combobox.currentIndexChanged.connect(self.clear_session_input)

    def clear_session_input(self):
        self.session_input.clear()
    def add_movie(self):
        title = self.title_input.text()
        hall = self.hall_combobox.currentText()
        session = self.session_input.toPlainText().strip().split('\n')
        session = sorted([i for i in session if i != ''])

        if title and session:
            # Отправка запроса на сервер
            requests.get('https://dair.pythonanywhere.com/saveMovie', params={'title': title, 'hall': hall, 'session': session})

            # Вывод сообщения об успехе
            QMessageBox.information(self, "Success", f"Movie '{title}' added to {hall} with sessions:\n{', '.join(session)}")
        else:
            QMessageBox.warning(self, "Error", "Please fill in all fields!")

class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin")
        self.setGeometry(100, 100, 1000, 800)  # Увеличиваем размер окна
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f4;
                border-radius: 10px;
            }
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #333;
            }
            QListWidget {
                border: 2px solid #ccc;
                border-radius: 8px;
                font-size: 18px;
                padding: 10px;
                background-color: #ffffff;
                margin-top: 10px;
                outline: none; /* Убирает фокус со всего QListWidget */
            }
            QListWidget::item {
                padding: 10px;
                font-size: 18px;
                border-radius: 6px;
                background-color: #f9f9f9;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
                outline: none; /* Убирает обводку выбранного элемента */
            }
            QListWidget::item:selected:focus {
                outline: none;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #c6c6c6;
                color: #888888;
            }
            #logout_button {
                background-color: #f44336;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                width: 100px;
            }
            #logout_button:hover {
                background-color: #d32f2f;
            }
            QHBoxLayout, QVBoxLayout {
                spacing: 15px;
            }
            QGroupBox {
                border: 1px solid #ddd;
                padding: 10px;
                margin-top: 20px;
                border-radius: 8px;
            }
            QGroupBox:title {
                color: #4CAF50;
                font-size: 22px;
                font-weight: bold;
            }
        """)

        main_layout = QVBoxLayout()

        # Верхняя панель с кнопкой Logout
        logout_button = QPushButton("Logout")
        logout_button.setObjectName("logout_button")
        logout_button.setFixedSize(100, 65)
        logout_button.clicked.connect(self.logout)

        top_layout = QHBoxLayout()
        top_layout.addStretch()  # Растягиваем пространство слева
        top_layout.addWidget(logout_button)  # Добавляем кнопку в правый угол

        # Основная часть с фильмами, залами и сессиями
        self.movie_list = QListWidget()
        self.hall_list = QListWidget()
        self.session_list = QListWidget()
        self.update_movie_list()

        self.movie_label = QLabel("Movie")
        self.hall_label = QLabel("Hall")
        self.session_label = QLabel("Session")

        lists_layout = QHBoxLayout()
        lists_layout.addWidget(self.create_list_with_label(self.movie_label, self.movie_list))
        lists_layout.addWidget(self.create_list_with_label(self.hall_label, self.hall_list))
        lists_layout.addWidget(self.create_list_with_label(self.session_label, self.session_list))

        # Кнопки администратора
        self.add_movie_button = QPushButton("Add Movie")
        self.remove_button = QPushButton("Remove")
        self.movie_info_button = QPushButton("Movie Information")
        self.user_info_button = QPushButton("User Info")

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.add_movie_button)
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addWidget(self.movie_info_button)
        buttons_layout.addWidget(self.user_info_button)

        main_layout.addLayout(top_layout)  # Верхняя панель с кнопкой Logout
        main_layout.addLayout(lists_layout)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        # Привязка событий
        self.add_movie_button.clicked.connect(self.open_add_movie_window)
        self.movie_list.itemClicked.connect(self.load_halls)
        self.hall_list.itemClicked.connect(self.load_sessions)
        self.remove_button.clicked.connect(self.remove_item)
        self.movie_info_button.clicked.connect(self.open_movie_inform)
        self.user_info_button.clicked.connect(self.open_users)

    def create_list_with_label(self, label, list_widget):
        layout = QVBoxLayout()
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(list_widget)
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def logout(self):
        self.close()
        self.log = Login()
        self.log.show()

    def open_add_movie_window(self):
        self.add_movie_window = AddMovieWindow()
        self.add_movie_window.finished.connect(self.update_movie_list)
        self.add_movie_window.exec_()

    def update_movie_list(self):
        self.inforn=requests.get('https://dair.pythonanywhere.com/getAllInform').json().get('inform',{})
        movies = list(self.inforn.keys())
        self.movie_list.clear()
        self.hall_list.clear()
        self.session_list.clear()
        self.movie_list.addItems(movies)
        self.movie_list.setCurrentRow(-1)  # Очистка выбора

    def load_halls(self, item):
        if item is None: return
        title = item.text()
        response = self.inforn[title].keys()
        halls = sorted(response)
        self.hall_list.clear()
        self.hall_list.addItems(halls)
        self.session_list.clear()

    def load_sessions(self, item):
        if self.movie_list.currentItem() is None or item is None: return
        title = self.movie_list.currentItem().text()
        hall = item.text()
        response = self.inforn[title][hall]
        sessions = response
        self.session_list.clear()
        self.session_list.addItems(sessions)

    def remove_item(self):
        if self.session_list.currentItem():
            title = self.movie_list.currentItem().text()
            hall = self.hall_list.currentItem().text()
            session = self.session_list.currentItem().text()
            self.inforn=requests.get('https://dair.pythonanywhere.com/removeSession', params={'title': title, 'hall': hall, 'session': session}).json().get('inform',{})
            QMessageBox.information(self, "Success", f"Session '{session}' removed from {hall}.")
            if not title in self.inforn:
                    self.update_movie_list()
                    return
            if not hall in self.inforn[title]:
                self.load_halls(self.movie_list.currentItem())
            else:
                self.load_sessions(self.hall_list.currentItem())

        elif self.hall_list.currentItem():
            title = self.movie_list.currentItem().text()
            hall = self.hall_list.currentItem().text()
            self.inforn=requests.get('https://dair.pythonanywhere.com/removeHall', params={'title': title, 'hall': hall}).json().get('inform',{})
            QMessageBox.information(self, "Success", f"All sessions in '{hall}' removed.")
            if not title in self.inforn:
                self.update_movie_list()
            else:
                self.load_halls(self.movie_list.currentItem())

        elif self.movie_list.currentItem():
            title = self.movie_list.currentItem().text()
            requests.get('https://dair.pythonanywhere.com/removeMovie', params={'title': title})
            QMessageBox.information(self, "Success", f"All sessions for movie '{title}' removed.")
            self.movie_list.takeItem(self.movie_list.currentRow())
            self.hall_list.clear()
            self.session_list.clear()
        else:
            QMessageBox.warning(self, "Error", "Please select a session, hall, or movie to remove.")

    def open_movie_inform(self):
        if self.movie_list.currentItem():
            hall = self.hall_list.currentItem().text() if self.hall_list.currentItem() else ''
            session = self.session_list.currentItem().text() if self.session_list.currentItem() else ''
            self.movie_infor = MovieInformWindow(self.movie_list.currentItem().text(), hall, session)
            self.movie_infor.show()
        else:
            QMessageBox.warning(self, "Error", "Select movie")

    def open_users(self):
        self.update_movie_list()
        self.users = UsersWindow()
        self.users.show()

class MovieWindow(QWidget):
    def __init__(self, user):
        self.user = user

        super().__init__()

        self.setWindowTitle("Movie")
        self.setGeometry(100, 100, 1000, 800)  # Adjust window size to match AdminWindow size
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f4;
                border-radius: 10px;
            }
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #333;
            }
            QListWidget {
                border: 2px solid #ccc;
                border-radius: 8px;
                font-size: 18px;
                padding: 10px;
                background-color: #ffffff;
                margin-top: 10px;
                outline: none; /* Убирает фокус со всего QListWidget */
            }
            QListWidget::item {
                padding: 10px;
                font-size: 18px;
                border-radius: 6px;
                background-color: #f9f9f9;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
                outline: none; /* Убирает обводку выбранного элемента */
            }
            QListWidget::item:selected:focus {
                outline: none;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #c6c6c6;
                color: #888888;
            }
            #logout_button {
                background-color: #f44336;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                width: 100px;
            }
            #logout_button:hover {
                background-color: #d32f2f;
            }
            QHBoxLayout, QVBoxLayout {
                spacing: 15px;
            }
            QGroupBox {
                border: 1px solid #ddd;
                padding: 10px;
                margin-top: 20px;
                border-radius: 8px;
            }
            QGroupBox:title {
                color: #4CAF50;
                font-size: 22px;
                font-weight: bold;
            }
        """)

        main_layout = QVBoxLayout()

        # Top bar with logout button
        logout_button = QPushButton("Logout")
        logout_button.setObjectName("logout_button")
        logout_button.setFixedSize(100, 65)
        logout_button.clicked.connect(self.logout)

        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(logout_button)

        # Movie, session, and hall sections
        self.movie_list = QListWidget()
        self.session_list = QListWidget()
        self.hall_list = QListWidget()
        self.update_movie_list()

        self.movie_label = QLabel("Movie")
        self.session_label = QLabel("Session")
        self.hall_label = QLabel("Hall")

        lists_layout = QHBoxLayout()
        lists_layout.addWidget(self.create_list_with_label(self.movie_label, self.movie_list))
        lists_layout.addWidget(self.create_list_with_label(self.session_label, self.session_list))
        lists_layout.addWidget(self.create_list_with_label(self.hall_label, self.hall_list))

        # Buttons
        self.buy_button = QPushButton("Buy")
        self.history_button = QPushButton("History")

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.buy_button)
        button_layout.addWidget(self.history_button)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(lists_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Button connections
        self.buy_button.clicked.connect(self.open_site)
        self.history_button.clicked.connect(self.open_hist)
        self.movie_list.itemClicked.connect(self.load_sessions)
        self.session_list.itemClicked.connect(self.load_halls)

    def create_list_with_label(self, label, list_widget):
        layout = QVBoxLayout()
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(list_widget)
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def load_sessions(self):
        title = self.movie_list.currentItem().text()
        response = []
        for i,v in self.inforn[title].items():response+=v
        sessions = sorted(list(set(response)))
        self.session_list.clear()
        self.hall_list.clear()
        self.session_list.addItems(sessions)

    def load_halls(self, item):
        title = self.movie_list.currentItem().text()
        session = item.text()
        response = [i for i,v in self.inforn[title].items() if session in v]
        halls = sorted(response)
        self.hall_list.clear()
        self.hall_list.addItems(halls)

    def open_site(self):
        if self.movie_list.currentItem() and self.session_list.currentItem() and self.hall_list.currentItem():
            title = self.movie_list.currentItem().text()
            session = self.session_list.currentItem().text()
            hall = self.hall_list.currentItem().text()
            self.site = SiteWindow(title, session, hall, self.user)
            self.site.show()
        else:
            QMessageBox.warning(self, "Error", "Please select a movie, session, and hall before proceeding!")
        self.update_movie_list()

    def open_hist(self):
        self.update_movie_list()
        self.hist = HistoryWindow(self.user)
        self.hist.show()
        

    def update_movie_list(self):
        self.inforn=requests.get('https://dair.pythonanywhere.com/getAllInform').json().get('inform','')
        movies = list(self.inforn.keys())
        self.movie_list.clear()
        self.hall_list.clear()
        self.session_list.clear()
        self.movie_list.addItems(movies)

    def logout(self):
        self.close()
        self.log = Login()
        self.log.show()

class Registration(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Registration')
        self.setGeometry(200, 200, 600, 450)
        self.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 18px;
                font-family: Arial, sans-serif;
            }
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 8px;
                padding: 12px;
                font-size: 18px;
                font-family: Arial, sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-family: Arial, sans-serif;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #c6c6c6;
                color: #888888;
            }
            QVBoxLayout {
                margin: 0;
                padding: 20px;
            }
            QFrame {
                background-color: #f4f4f4;
                padding: 20px;
                border-radius: 12px;
            }
        """)

        # Create form widgets
        self.label1 = QLabel("Username:")
        self.username = QLineEdit()
        self.label2 = QLabel("Password:")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.label3 = QLabel("Confirm Password:")
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_button = QPushButton("Register")

        # Set initial states
        self.register_button.setEnabled(False)

        # Layout for the registration form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        form_layout.addWidget(self.label1)
        form_layout.addWidget(self.username)
        form_layout.addWidget(self.label2)
        form_layout.addWidget(self.password)
        form_layout.addWidget(self.label3)
        form_layout.addWidget(self.confirm_password)
        form_layout.addWidget(self.register_button)

        # Setting layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)

        self.setLayout(main_layout)

        # Connect signal to register user
        self.username.textChanged.connect(self.enable_register_button)
        self.password.textChanged.connect(self.enable_register_button)
        self.confirm_password.textChanged.connect(self.enable_register_button)
        self.register_button.clicked.connect(self.register_user)

    def enable_register_button(self):
        # Enable register button only if username, password, and confirm password are valid
        name = self.username.text().strip()
        password = self.password.text().strip()
        confirm_password = self.confirm_password.text().strip()
        if name and password and confirm_password and password == confirm_password:
            self.register_button.setEnabled(True)
        else:
            self.register_button.setEnabled(False)

    def register_user(self):
        name = self.username.text().strip()
        password = self.password.text().strip()
        confirm_password = self.confirm_password.text().strip()

        if ' ' in name or ' ' in password:
            QMessageBox.warning(self, "Error", "Username and password cannot contain spaces.")
            return
        
        test = requests.get('https://dair.pythonanywhere.com/isNewUser', params={'name': name}).json().get('test', '')
        if test:
            QMessageBox.warning(self, "Error", "This username is already taken.")
            return

        if name and password == confirm_password and password:
            requests.get('https://dair.pythonanywhere.com/saveUser', params={'name': name, 'password': password})
            self.close()
            self.movie_window = MovieWindow(name)
            self.movie_window.show()
        else:
            QMessageBox.warning(self, "Error", "You need to enter a valid username and password.")

class Login(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Login')
        self.setGeometry(200, 200, 600, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;
                border-radius: 10px;
            }
            QLabel {
                color: #333;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 12px;
                font-size: 18px;
                margin-bottom: 20px;
            }
            QLineEdit:focus {
                border-color: #28a745;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 10px;
                padding: 15px;
                font-size: 18px;
                margin-bottom: 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: white;
            }
            QCheckBox {
                font-size: 18px;
                color: #555;
                margin-bottom: 20px;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
            }
            QVBoxLayout {
                margin: 20px;
            }
            QHBoxLayout {
                justify-content: center;
            }
        """)

        # Widgets
        self.label = QLabel("Username:")
        self.username = QLineEdit()
        self.label2 = QLabel("Password:")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.captcha_checkbox = QCheckBox("I'm not a robot")
        self.login_button = QPushButton("Login")
        self.new_user_button = QPushButton("New user")
        self.login_for_admin_button = QPushButton("Login as admin")

        # Initial state
        self.captcha_checkbox.setEnabled(False)
        self.login_button.setEnabled(False)
        self.new_user_button.setEnabled(False)

        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(self.label)
        layout.addWidget(self.username)
        layout.addWidget(self.label2)
        layout.addWidget(self.password)
        layout.addWidget(self.captcha_checkbox)
        layout.addWidget(self.login_button)
        layout.addWidget(self.new_user_button)
        layout.addWidget(self.login_for_admin_button)

        self.setLayout(layout)

        # Event connections
        self.captcha_checkbox.stateChanged.connect(self.update_login_button)
        self.new_user_button.clicked.connect(self.open_registration_dialog)
        self.login_button.clicked.connect(self.login)
        self.login_for_admin_button.clicked.connect(self.open_as_admin)

        self.mouse_moved = False
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        if not self.mouse_moved:
            self.mouse_moved = True
            self.captcha_checkbox.setEnabled(True)

    def update_login_button(self):
        self.login_button.setEnabled(self.captcha_checkbox.isChecked())
        self.new_user_button.setEnabled(self.captcha_checkbox.isChecked())

    def open_registration_dialog(self):
        self.close()
        self.registration_dialog = Registration()
        self.registration_dialog.exec_()

    def login(self):
        name = self.username.text()
        password = self.password.text()
        rightPassword = requests.get('https://dair.pythonanywhere.com/getPassword', params={'name': name}).json().get('password')
        if password == rightPassword:
            self.close()
            self.movie_window = MovieWindow(name)
            self.movie_window.show()
        else:
            QMessageBox.warning(self, "Error", "Login failed!")

    def open_as_admin(self):
        self.close()
        self.movie_window = AdminWindow()
        self.movie_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    sys.exit(app.exec_())