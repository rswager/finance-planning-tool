from datetime import date
from resources.model_tables import ModelTables
from resources.modelManager import ModelManager

from models.enumType import AccountType, FrequencyType
from models.utils import dollars_to_cents, money_dollars
from models.bankAccount import BankAccount
from models.financed_bill import FinancedBill
from models.income import Income
from models.recurring_bill import RecurringBill
from models.revolving_credit_bill import RevolvingCreditBill
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from sys import argv


class MainApp: # pyrefly: ignore[missing-attribute]
    def __init__(self):
        super().__init__()
        self.debug=True
        self.round_up_down=False

        # Load the UI file
        self.ui = uic.loadUi("main_app.ui")
        # Set to max screen
        self.ui.showMaximized()
        self.hide_relations ={
            self.ui.pushButton_show_hide_bank_accounts:[self.ui.tableView_bank_accounts,self.ui.pushButton_add_bank_account],
            self.ui.pushButton_show_hide_income:[self.ui.tableView_income,self.ui.pushButton_add_income],
            self.ui.pushButton_show_hide_revolving_credit:[self.ui.tableView_revolving_credit,self.ui.pushButton_add_revolving_credit],
            self.ui.pushButton_show_hide_financed_bills:[self.ui.tableView_financed_bills,self.ui.pushButton_add_financed_bills],
            self.ui.pushButton_show_hide_bills:[self.ui.tableView_bills, self.ui.pushButton_add_bills]
        }
        ################################################################################################################
        self.ui.pushButton_show_hide_bank_accounts.clicked.connect(
            lambda : self.show_hide_area(self.ui.pushButton_show_hide_bank_accounts))

        self.bank_account_model = ModelManager(
            table_reference=self.ui.tableView_bank_accounts,
            model_type_in=BankAccount,
            model_data_in=None if not self.debug else
                {
                    "primary_checking":
                        BankAccount(
                            name_in="primary_checking",
                            balance_in=dollars_to_cents(money_dollars(1_000.00)),
                            account_type_in=AccountType.CHECKING
                        ),
                    "primary_savings":
                        BankAccount(
                            name_in="primary_savings",
                            balance_in=dollars_to_cents(money_dollars(2_000.00)),
                            account_type_in=AccountType.SAVINGS
                        )
                }
        )

        ################################################################################################################
        self.ui.pushButton_show_hide_income.clicked.connect(
            lambda: self.show_hide_area(self.ui.pushButton_show_hide_income))

        self.income_model = ModelManager(
            table_reference=self.ui.tableView_income,
            model_type_in=Income
        )

        ################################################################################################################
        self.ui.pushButton_show_hide_revolving_credit.clicked.connect(
            lambda: self.show_hide_area(self.ui.pushButton_show_hide_revolving_credit))
        self.revolving_credit_model = ModelManager(
            table_reference=self.ui.tableView_revolving_credit,
            model_type_in=RevolvingCreditBill
        )

        ################################################################################################################
        self.ui.pushButton_show_hide_financed_bills.clicked.connect(
            lambda: self.show_hide_area(self.ui.pushButton_show_hide_financed_bills))
        self.financed_bills_model = ModelManager(
            table_reference=self.ui.tableView_financed_bills,
            model_type_in=FinancedBill

        )

        ################################################################################################################
        self.ui.pushButton_show_hide_bills.clicked.connect(
            lambda: self.show_hide_area(self.ui.pushButton_show_hide_bills))
        self.bills_model = ModelManager(
            table_reference=self.ui.tableView_bills,
            model_type_in=RecurringBill

        )

    def show_hide_area(self, button):
        if button.text() == "↓":
            button.setText("→")
            # raised everything up
            for items in self.hide_relations[button]:
                items.setVisible(False)
        else:
            button.setText("↓")
            # drop everything down
            for items in self.hide_relations[button]:
                items.setVisible(True)


if __name__ == "__main__":
    app = QApplication(argv)
    window = MainApp()
    window.ui.show()
    app.exec_()