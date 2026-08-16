import json
import re

from ..customize import widgets

from PyQt5.Qt import QRect
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from qfluentwidgets import TableWidget, PushButton


class Character(QWidget):
    def __init__(self, languages, configure, api_config, intelligence_model, runtime_model):
        super().__init__()
        self.intelligence = intelligence_model
        self.runtime = runtime_model
        self.languages = languages
        self.configure = configure
        self.api_config = api_config
        self.setObjectName("Character")

        self.histories = []

        self.table_character = TableWidget(self)
        self.table_character.setBorderVisible(True)
        self.table_character.setBorderRadius(8)
        self.table_character.setWordWrap(False)
        self.table_character.setColumnCount(2)

        self.table_character.setColumnWidth(0, 100)
        self.table_character.setColumnWidth(1, 500)

        with open(f"./intelligence/prompts/{self.configure['default']}.json", "r", encoding="utf-8") as f:
            prompts = json.load(f)
            f.close()
        dialog = []
        for key, value in prompts.items():
            dialog.append([key, value])

        self.table_character.setRowCount(len(dialog))
        for i, dialogInfo in enumerate(dialog):
            for j in range(2):
                self.table_character.setItem(i, j, QTableWidgetItem(dialogInfo[j]))

        self.table_character.setHorizontalHeaderLabels(['权限集', '人设词'])
        self.table_character.verticalHeader().hide()
        self.table_character.setGeometry(QRect(10, 42, 620, 400))

        self.click_add_system = PushButton(self.languages[168], self)
        self.click_add_system.setGeometry(QRect(10, 440, 200, 30))
        self.click_add_system.clicked.connect(lambda: self.add_one("system"))
        self.click_add_user = PushButton(self.languages[169], self)
        self.click_add_user.setGeometry(QRect(10, 470, 200, 30))
        self.click_add_user.clicked.connect(lambda: self.add_one("user"))
        self.click_add_assistant = PushButton(self.languages[170], self)
        self.click_add_assistant.setGeometry(QRect(10, 500, 200, 30))
        self.click_add_assistant.clicked.connect(lambda: self.add_one("assistant"))

        self.click_remove_one = PushButton(self.languages[171], self)
        self.click_remove_one.setGeometry(QRect(220, 440, 200, 30))
        self.click_remove_one.clicked.connect(self.remove_one)
        self.click_get_assistant = PushButton(self.languages[172], self)
        self.click_get_assistant.setGeometry(QRect(220, 470, 200, 30))
        self.click_get_assistant.clicked.connect(self.auto_fill_assistant)
        self.click_save_all = PushButton(self.languages[173], self)
        self.click_save_all.setGeometry(QRect(220, 500, 200, 30))
        self.click_save_all.clicked.connect(self.save_all)

        self.click_undo = PushButton(self.languages[174], self)
        self.click_undo.setGeometry(QRect(430, 440, 100, 30))
        self.click_undo.clicked.connect(self.undo)

    def undo(self):
        if not self.histories:
            return
        item = self.histories[-1][1]
        match self.histories[-1][0]:
            case 'add':
                self.remove_one(item)
            case 'remove':
                self.add_one(re.sub(r'\d+', '', item[1]), item[2], item[0], True)
            case 'auto-fill':
                self.remove_one(item)
        self.histories.pop()

    def get_all_elements(self):
        all_elements = []
        row_count = self.table_character.rowCount()
        column_count = self.table_character.columnCount()

        for row in range(row_count):
            row_data = []
            for column in range(column_count):
                item = self.table_character.item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            all_elements.append(row_data)

        return all_elements

    def auto_fill_assistant(self):
        def filler(text: list):
            if text[1]:
                self.table_character.setItem(generate_id, 1, QTableWidgetItem(text[0]))
                self.histories.append(("auto-fill", generate_id))
            else:
                self.table_character.setItem(generate_id, 1, QTableWidgetItem(text[0]))

        selected_row = self.table_character.currentRow()
        if selected_row != -1:
            if "user" not in self.table_character.item(selected_row, 0).text():
                widgets.pop_error(self, self.languages[76], self.languages[167])
                return
            generate_id = self.add_one("assistant", "Waiting for Answering")
            text_generator = self.runtime.thread.TextGenerateThread(
                self, self.configure, self.api_config,
                self.table_character.item(selected_row, 1).text())
            text_generator.result.connect(filler)
            text_generator.start()

    def save_all(self):
        all_elements = self.get_all_elements()
        with open(f"./intelligence/prompts/{self.configure['default']}.json", "w", encoding="utf-8") as sf:
            json.dump({row[0]: row[1] for row in all_elements}, sf, indent=3, ensure_ascii=False)
            sf.close()
        self.intelligence.text.reload_memories(self.configure['default'])
        widgets.pop_success(self, self.languages[76], self.languages[165])

    def remove_one(self, id_: int | None = None):
        if not isinstance(id_, int):
            current_row = id_
        else:
            current_row = self.table_character.currentRow()
        if current_row != -1:
            self.histories.append(("remove", [current_row,
                                              self.table_character.item(current_row, 0).text(),
                                              self.table_character.item(current_row, 1).text()
                                              ]))
            self.table_character.removeRow(current_row)
            self.table_character.resizeRowsToContents()
            self.table_character.resizeColumnToContents(0)

    def add_one(self, type_: str, text: str = "", index: int = -1, is_insert: bool = False):
        filtered_rows = list(filter(lambda row: type_ in row[0], self.get_all_elements()))
        if filtered_rows:
            if type_ == "system":
                widgets.pop_error(self, self.languages[76], self.languages[166])
                return
            last_number = int(re.search(r'\d+', filtered_rows[-1][0]).group())
            new_number = last_number + 1
        else:
            if type_ == "system":
                new_number = ""
            else:
                new_number = 1
        insert_index = index
        if is_insert is False:
            self.table_character.insertRow(self.table_character.rowCount())
            insert_index = self.table_character.rowCount() - 1
            self.table_character.setItem(insert_index, 0,
                                         QTableWidgetItem(f"{type_}{new_number}"))
            self.table_character.setItem(insert_index, 1, QTableWidgetItem(text))
            self.table_character.resizeRowsToContents()
            self.table_character.resizeColumnToContents(0)
            self.histories.append(("add", insert_index))
        else:
            elements = self.get_all_elements()
            elements.insert(insert_index, [f"{type_}{new_number}", text])
            self.table_character.setRowCount(len(elements))
            for row_index, row_data in enumerate(elements):
                for column_index, item_data in enumerate(row_data):
                    self.table_character.setItem(row_index, column_index, QTableWidgetItem(item_data))
        return insert_index
