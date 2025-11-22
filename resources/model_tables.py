from models.bankAccount import BankAccount
from models.financed_bill import FinancedBill
from models.income import Income
from models.recurring_bill import RecurringBill
from models.revolving_credit_bill import RevolvingCreditBill
from models.enumType import AccountType

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableView, QHeaderView

STD_SCROLL_STEPS = 1

headers = {
    BankAccount: ["Name", "Type", "Balance"],
    Income: ["Name", "Amt", "Frequency"],
    RevolvingCreditBill: ["Name", "Limit", "Min Payment", "Frequency"],
    FinancedBill: ["Name", "Financed Amt", "Min Payment", "Frequency"],
    RecurringBill: ["Name", "Payment Amt", "Frequency"]
}

class ModelTables:
    def __init__(self, table_reference, models_in=None):
        super().__init__()
        self.table = table_reference
        self.table.doubleClicked.connect(self.on_table_double_click)
        self.table_item_model = QStandardItemModel()
        self.model_type = type(models_in[next(iter(models_in))])
        header_in = headers[self.model_type]

        self.table_item_model.setColumnCount(len(header_in))
        self.table_item_model.setHorizontalHeaderLabels(header_in)

        self.table.setModel(self.table_item_model)
        self.selection_model = self.table.selectionModel()

        if models_in is not None:
            self.finance_model = models_in
            self.add_item_to_model(models_in)
        else:
            self.finance_model = {}

        self.format_table()


    def on_table_double_click(self, index: QModelIndex):
        # Optional: print entire row
        # Always get the value from the first column of the clicked row
        first_col_value = self.table_item_model.data(self.table_item_model.index(index.row(), 0))

        print("Value in first column:", first_col_value)

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

    def add_item_to_model(self, model_data_in) -> None:
        # BankAccount: ["Name", "Type", "Balance"],
        # Income: ["Name", "Amt", "Frequency"],
        # RevolvingCreditBill: ["Name", "Limit", "Min Payment", "Frequency"],
        # FinancedBill: ["Name", "Financed Amt", "Min Payment", "Frequency"],
        # RecurringBill: ["Name", "Payment Amt", "Frequency"]

        for model in model_data_in:
            finance_model = model_data_in[model]
            each = []
            if type(finance_model) == BankAccount :
                each = [finance_model.account_name, finance_model.account_type.name, f'${finance_model.balance_dollars:,.2f}']
            elif type(finance_model) == Income:
                each = [finance_model.account_name, f'${finance_model.income_amount_dollars:,.2f}',finance_model.frequency.name]
            elif type(finance_model) == RevolvingCreditBill:
                each = [finance_model.account_name, f'${finance_model.credit_limit_dollars:,.2f}',
                        f'${finance_model.min_payment_dollars:,.2f}', finance_model.frequency.name]
            elif type(finance_model) == FinancedBill:
                each = [finance_model.account_name,f"${finance_model.loan_balance_dollars:,.2f}",
                        f"${finance_model.min_payment_dollars:,.2f}",finance_model.frequency.name]
            elif type(finance_model) == RecurringBill:
                each = [finance_model.account_name,f"${finance_model.min_payment_dollars:,.2f}",
                        finance_model.frequency.name]
            else:
                 return
            row_items = []
            for col in each:
                item=QStandardItem(col)
                item.setTextAlignment(Qt.AlignCenter)
                row_items.append(item)
            self.table_item_model.appendRow(row_items)


    def set_scroll_speed(self):
        v_scroll = self.table.verticalScrollBar()
        h_scroll = self.table.horizontalScrollBar()

        v_scroll.setSingleStep(STD_SCROLL_STEPS)
        h_scroll.setSingleStep(STD_SCROLL_STEPS)
