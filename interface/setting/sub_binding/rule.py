from PyQt5.Qt import QRect, QTableWidgetItem
from PyQt5.QtWidgets import QWidget

from qfluentwidgets import TableWidget, BodyLabel, LineEdit, ComboBox, PushButton


class RuleBinding(QWidget):
    def __init__(self, languages, configure, rules, model_path, addon, runtime_module):
        super().__init__()
        self.languages = languages
        self.configure = configure
        self.runtime = runtime_module
        self.setObjectName("RuleBinding")

        self.rules_table = TableWidget(self)
        self.rules_table.setColumnCount(2)
        self.rules_table.setHorizontalHeaderLabels([self.languages[175], self.languages[176]])
        self.rules_table.setColumnWidth(0, 450)
        self.rules_table.setColumnWidth(1, 200)
        self.rules_table.setGeometry(QRect(0, 42, 650, 350))
        self.rules_table.setBorderVisible(True)
        self.rules_table.setBorderRadius(8)
        self.rules_table.setWordWrap(False)
        self.rules_table.verticalHeader().setHidden(True)
        for trigger, expr in rules.items():
            self.rules_table.insertRow(self.rules_table.rowCount())
            self.rules_table.setItem(self.rules_table.rowCount() - 1, 0, QTableWidgetItem(trigger))
            self.rules_table.setItem(self.rules_table.rowCount() - 1, 1, QTableWidgetItem(expr))

        BodyLabel(self.languages[175], self).setGeometry(QRect(0, 400, 150, 30))
        self.trigger_words = LineEdit(self)
        self.trigger_words.setGeometry(QRect(100, 400, 550, 30))
        BodyLabel(self.languages[176], self).setGeometry(QRect(0, 450, 150, 30))
        self.execute_expr = ComboBox(self)
        self.execute_expr.addItems(addon.Live2DParameters(model_path).get_expressions)
        self.execute_expr.setGeometry(QRect(100, 450, 550, 30))
        self.click_add = PushButton(self.languages[177], self)
        self.click_add.clicked.connect(self.add)
        self.click_add.setGeometry(QRect(0, 490, 200, 30))
        self.click_remove = PushButton(self.languages[178], self)
        self.click_remove.clicked.connect(self.remove)
        self.click_remove.setGeometry(QRect(250, 490, 200, 30))
        self.click_save = PushButton(self.languages[44], self)
        self.click_save.clicked.connect(self.save)
        self.click_save.setGeometry(QRect(500, 490, 150, 30))

    def add(self):
        self.rules_table.insertRow(self.rules_table.rowCount())
        self.rules_table.setItem(self.rules_table.rowCount() - 1, 0, QTableWidgetItem(self.trigger_words.text()))
        self.rules_table.setItem(self.rules_table.rowCount() - 1, 1, QTableWidgetItem(self.execute_expr.text()))

    def remove(self):
        for index in self.rules_table.selectedIndexes():
            self.rules_table.removeRow(index.row())

    def save(self):
        rules = {}
        for row in range(self.rules_table.rowCount()):
            rules.update({self.rules_table.item(row, 0).text(): self.rules_table.item(row, 1).text()})
        self.runtime.file.save_rules(rules, self.configure['default'])
