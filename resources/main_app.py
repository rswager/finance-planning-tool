from datetime import date
from model_tables import ModelTables
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

        self.bank_account_model = ModelTables(
            table_reference=self.ui.tableView_bank_accounts,
            models_in=None if not self.debug else
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

        self.income_model = ModelTables(
            table_reference=self.ui.tableView_income,
            models_in=None if not self.debug else
                {
                    'primary_income':
                        Income(
                            name_in='primary_income',
                            income_in=dollars_to_cents(money_dollars(2_557.31)),
                            initial_pay_date_in=date(2025, 11, 6),
                            account_contributions_in=
                            [
                                (self.bank_account_model.finance_model['primary_checking'], .9),  # 90% to primary checking
                                (self.bank_account_model.finance_model['primary_savings'], .1)  # 10% to primary savings
                            ],
                            frequency_type_in=FrequencyType.BI_WEEKLY, round_down=self.round_up_down
                        )
                }
        )

        ################################################################################################################
        self.ui.pushButton_show_hide_revolving_credit.clicked.connect(
            lambda: self.show_hide_area(self.ui.pushButton_show_hide_revolving_credit))
        self.revolving_credit_model = ModelTables(
            table_reference=self.ui.tableView_revolving_credit,
            models_in=None if not self.debug else
                {
                    'discover_card':
                        RevolvingCreditBill(
                            name_in='discover_card', balance_in=dollars_to_cents(money_dollars(693.65)),
                            account_type_in=AccountType.REVOLVING,
                            initial_pay_date_in=date(2025,11,28),
                            frequency_type_in=FrequencyType.MONTHLY,
                            minimum_payment_in=dollars_to_cents(money_dollars(400.00)),
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            apr_rate_in=.15,
                            credit_limit_in=dollars_to_cents(money_dollars(30_000.00)),
                            round_up=self.round_up_down
                            )
                }
        )

        ################################################################################################################
        self.ui.pushButton_show_hide_financed_bills.clicked.connect(
            lambda: self.show_hide_area(self.ui.pushButton_show_hide_financed_bills))
        self.financed_bills_model = ModelTables(
            table_reference=self.ui.tableView_financed_bills,
            models_in=None if not self.debug else
                {
                    'mortgage':
                        FinancedBill(
                            name_in='mortgage',
                            balance_in=dollars_to_cents(money_dollars(132_367.00)),
                            account_type_in=AccountType.LOAN,
                            initial_pay_date_in=date(2025, 11, 1),
                            frequency_type_in=FrequencyType.BI_WEEKLY,
                            minimum_payment_in=dollars_to_cents(money_dollars(924.35 / 2)),
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            apr_rate_in=.0725,
                            round_up=self.round_up_down),
                    'car_payment_ford':
                        FinancedBill(
                            name_in='car_payment_ford',
                            balance_in=dollars_to_cents(money_dollars(28_000.00)),
                            account_type_in=AccountType.LOAN,
                            initial_pay_date_in=date(2025, 11, 15),
                            frequency_type_in=FrequencyType.BI_WEEKLY,
                            minimum_payment_in=dollars_to_cents(money_dollars(250.00)),
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            apr_rate_in=.06,
                            round_up=self.round_up_down
                        ),
                    'student_loans':
                        FinancedBill(
                            name_in='student_loans',
                            balance_in=dollars_to_cents(money_dollars(35_000.00)),
                            account_type_in=AccountType.LOAN,
                            initial_pay_date_in=date(2025, 11, 18),
                            frequency_type_in=FrequencyType.MONTHLY,
                            minimum_payment_in=dollars_to_cents(money_dollars(461.00)),
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            apr_rate_in=.03,
                            round_up=self.round_up_down),
                }
        )

        ################################################################################################################
        self.ui.pushButton_show_hide_bills.clicked.connect(
            lambda: self.show_hide_area(self.ui.pushButton_show_hide_bills))
        self.bills_model = ModelTables(
            table_reference=self.ui.tableView_bills,
            models_in=None if not self.debug else
                {
                    'mortgage_escrow':
                        RecurringBill(
                            name_in='mortgage_escrow',
                            minimum_payment_in=dollars_to_cents(money_dollars(924.35)),
                            account_type_in=AccountType.REOCCURRING,
                            initial_pay_date_in=date(2025, 11, 1),
                            frequency_type_in=FrequencyType.MONTHLY,
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            round_up=self.round_up_down
                        ),
                    'netflix':
                        RecurringBill(
                            name_in='netflix',
                            minimum_payment_in=dollars_to_cents(money_dollars(12.99)),
                            account_type_in=AccountType.SUBSCRIPTION,
                            initial_pay_date_in=date(2025, 11, 9),
                            frequency_type_in=FrequencyType.MONTHLY,
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            round_up=self.round_up_down
                        ),
                    'car_insurance':
                        RecurringBill(
                            name_in='car_insurance',
                            minimum_payment_in=dollars_to_cents(money_dollars(300.00)),
                            account_type_in=AccountType.REOCCURRING,
                            initial_pay_date_in=date(2025, 11, 16),
                            frequency_type_in=FrequencyType.MONTHLY,
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            round_up=self.round_up_down
                        ),
                    'crunchyroll':
                        RecurringBill(
                            name_in='crunchyroll',
                            minimum_payment_in=dollars_to_cents(money_dollars(11.99)),
                            account_type_in=AccountType.SUBSCRIPTION,
                            initial_pay_date_in=date(2025, 11, 13),
                            frequency_type_in=FrequencyType.MONTHLY,
                            payment_method_in=self.revolving_credit_model.finance_model['discover_card'],
                            round_up=self.round_up_down
                        ),
                    'spotify':
                        RecurringBill(
                            name_in='spotify',
                            minimum_payment_in=dollars_to_cents(money_dollars(11.99)),
                            account_type_in=AccountType.SUBSCRIPTION,
                            initial_pay_date_in=date(2025, 11, 13),
                            frequency_type_in=FrequencyType.MONTHLY,
                            payment_method_in=self.revolving_credit_model.finance_model['discover_card'],
                            round_up=self.round_up_down
                        ),
                    'internet':
                        RecurringBill(
                            name_in='internet',
                            minimum_payment_in=dollars_to_cents(money_dollars(59.99)),
                            account_type_in=AccountType.REOCCURRING,
                            initial_pay_date_in=date(2025, 11, 3),
                            frequency_type_in=FrequencyType.MONTHLY,
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            round_up=self.round_up_down),
                    'utilities':
                        RecurringBill(
                            name_in='utilities',
                            minimum_payment_in=dollars_to_cents(money_dollars(150.00)),
                            account_type_in=AccountType.REOCCURRING,
                            initial_pay_date_in=date(2025, 11, 1),
                            frequency_type_in=FrequencyType.MONTHLY,
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            round_up=self.round_up_down
                        ),
                    'adt':
                        RecurringBill(
                            name_in='adt',
                            minimum_payment_in=dollars_to_cents(money_dollars(50.00)),
                            account_type_in=AccountType.REOCCURRING,
                            initial_pay_date_in=date(2025, 11, 15),
                            frequency_type_in=FrequencyType.MONTHLY,
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            round_up=self.round_up_down),

                    'food':
                        RecurringBill(
                            name_in='food',
                            minimum_payment_in=dollars_to_cents(money_dollars(75.00)),
                            account_type_in=AccountType.REOCCURRING,
                            initial_pay_date_in=date(2025, 11, 1),
                            frequency_type_in=FrequencyType.WEEKLY,
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            round_up=self.round_up_down
                        ),
                    'fun':
                        RecurringBill(
                            name_in='fun',
                            minimum_payment_in=dollars_to_cents(money_dollars(25.00)),
                            account_type_in=AccountType.REOCCURRING,
                            initial_pay_date_in=date(2025, 11, 1),
                            frequency_type_in=FrequencyType.WEEKLY,
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            round_up=self.round_up_down
                        ),
                    'gas':
                        RecurringBill(
                            name_in='gas',
                            minimum_payment_in=dollars_to_cents(money_dollars(10.00)),
                            account_type_in=AccountType.REOCCURRING,
                            initial_pay_date_in=date(2025, 11, 1),
                            frequency_type_in=FrequencyType.WEEKLY,
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            round_up=self.round_up_down
                        ),
                    'therapy':
                        RecurringBill(
                            name_in='therapy',
                            minimum_payment_in=dollars_to_cents(money_dollars(30.00)),
                            account_type_in=AccountType.REOCCURRING,
                            initial_pay_date_in=date(2025, 11, 8),
                            frequency_type_in=FrequencyType.BI_WEEKLY,
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            round_up=self.round_up_down
                        ),
                    'cat_bill':
                        RecurringBill(
                            name_in='cat_bill',
                            minimum_payment_in=dollars_to_cents(money_dollars(60.00)),
                            account_type_in=AccountType.REOCCURRING,
                            initial_pay_date_in=date(2025, 11, 28),
                            frequency_type_in=FrequencyType.BI_WEEKLY,
                            payment_method_in=self.bank_account_model.finance_model['primary_checking'],
                            round_up=self.round_up_down
                        )
                }
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