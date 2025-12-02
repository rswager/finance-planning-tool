
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableView, QHeaderView

STD_SCROLL_STEPS = 1

class ModelTables:
    def __init__(self, table_reference, header_in):
        super().__init__()
        self.table = table_reference
        self.table.doubleClicked.connect(self.on_table_double_click)
        self.table_item_model = QStandardItemModel()

        self.table_item_model.setColumnCount(len(header_in))
        self.table_item_model.setHorizontalHeaderLabels(header_in)

        self.table.setModel(self.table_item_model)
        self.selection_model = self.table.selectionModel()

        self.format_table()

    def on_table_double_click(self, index: QModelIndex):
        first_col_value = self.table_item_model.data(self.table_item_model.index(index.row(), 0))

        print(self.finance_model[first_col_value].account_name)

    def format_table(self) -> None:
        header = self.table.horizontalHeader()
        column_count = self.table_item_model.columnCount()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)

        for col in range(column_count):
            if col == 0:
                header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(col, QHeaderView.Stretch)

        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #87ceeb    ;
                color: black;
                padding: 4px;
                border: none;
            }

            QTableView {
                gridline-color: #bfbfbf;
                background-color: #f9f9f9;
                alternate-background-color: #D3D3D3;  
                selection-background-color: #4a90e2;
            }
        """)

        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.horizontalHeader().setStretchLastSection(True)

    def add_item_to_model(self, data_in) -> None:
        for row in data_in:
            row_items=[]
            for col in row:
                item=QStandardItem(col)
                item.setTextAlignment(Qt.AlignCenter)
                row_items.append(item)
            self.table_item_model.appendRow(row_items)

    def set_scroll_speed(self) -> None:
        v_scroll = self.table.verticalScrollBar()
        h_scroll = self.table.horizontalScrollBar()

        v_scroll.setSingleStep(STD_SCROLL_STEPS)
        h_scroll.setSingleStep(STD_SCROLL_STEPS)
