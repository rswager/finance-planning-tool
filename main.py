from __future__ import annotations

import os
from collections.abc import Sequence
from datetime import date, timedelta

from xlsxwriter.utility import xl_col_to_name
from xlsxwriter.workbook import Workbook
from xlsxwriter.worksheet import Worksheet

from _dirs import LOCAL_APP_DATA, SAVED_OBJECT_DATA
from models.accounts.bank_account import BankAccount
from models.bills.bill_financed import FinancedBill
from models.bills.bill_recurring import RecurringBill
from models.bills.bill_revolving_credit import RevolvingCreditBill
from models.core.enum_type import AccountType, FrequencyType
from models.core.ledger import StandardLedgerRow
from models.core.utils import MinorUnit
from models.income.income import Income
from models.persistence.json_reader_writer import write_object_to_file
from models.persistence.serializer import convert_objects_to_persistence_dict

# Make sure our Directories are set up.
os.makedirs(LOCAL_APP_DATA, exist_ok=True)
os.makedirs(SAVED_OBJECT_DATA, exist_ok=True)


def add_table(
    worksheet_in: Worksheet, table_name_in: str, header_in: list[str], data_in: Sequence[StandardLedgerRow]
) -> None:
    data = [list(row) for row in data_in]
    if not data:
        return
    header = []
    for index, column_data in enumerate(data[0]):
        if isinstance(column_data, float | int) and index != 0:
            column_def = {"header": header_in[index], "format": accounting_format}
        elif isinstance(column_data, date):
            column_def = {"header": header_in[index], "format": date_format}
        else:
            column_def = {"header": header_in[index]}
        header.append(column_def)

    worksheet_in.add_table(
        first_row=0,
        first_col=0,
        last_row=len(data),
        last_col=len(header) - 1,
        options={
            "header_row": True,
            "data": data,
            "total_row": False,
            "autofilter": True,
            "columns": header,
            "style": "Table Style Medium 9",
            "name": f"{str(table_name_in)}_Table",
        },
    )


def add_chart(workbook_in: Workbook, worksheet_in: Worksheet, table_name_in: str, col_in: str) -> None:
    chart = workbook_in.add_chart({"type": "line"})
    assert chart is not None
    chart.add_series(
        {
            "categories": f"{table_name_in}_Table[Date]",
            "values": f"{table_name_in}_Table[Balance]",
            "name": "Projected Balance",
        }
    )

    worksheet_in.insert_chart(f"{col_in}1", chart, {"x_scale": 2.5, "y_scale": 2.5})


round_up_expenses_round_down_income = False
accounts = {
    "primary_checking": BankAccount(
        name_in="primary_checking",
        account_type_in=AccountType.CHECKING,
        balance_in=MinorUnit.from_major(571.75),
    ),
    "primary_savings": BankAccount(
        name_in="primary_savings",
        account_type_in=AccountType.SAVINGS,
        balance_in=MinorUnit.from_major(15_380.29),
    ),
}

revolving_credit = {
    "discover_card": RevolvingCreditBill(
        name_in="discover_card",
        balance_in=MinorUnit.from_major(10_923.60),
        account_type_in=AccountType.REVOLVING,
        initial_pay_date_in=date(2025, 11, 28),
        frequency_type_in=FrequencyType.MONTHLY,
        minimum_payment_in=MinorUnit.from_major(400.00),
        payment_method_in=accounts["primary_checking"],
        apr_rate_in=0.15,
        credit_limit_in=MinorUnit.from_major(30_000.00),
        round_up=round_up_expenses_round_down_income,
    )
}

incomes = {
    "primary_Income": Income(
        name_in="primary_Income",
        income_in=MinorUnit.from_major(2_604.9),
        initial_pay_date_in=date(2025, 11, 6),
        account_contributions_in=[
            (accounts["primary_checking"], 0.9),  # 90% to primary checking
            (accounts["primary_savings"], 0.1),  # 10% to primary savings
        ],
        frequency_type_in=FrequencyType.BI_WEEKLY,
        round_down=round_up_expenses_round_down_income,
    )
}

bills = {
    "Mortgage": FinancedBill(
        name_in="Mortgage",
        balance_in=MinorUnit.from_major(131_315.21),
        account_type_in=AccountType.LOAN,
        initial_pay_date_in=date(2025, 11, 1),
        frequency_type_in=FrequencyType.MONTHLY,
        minimum_payment_in=MinorUnit.from_major(924.35),
        payment_method_in=accounts["primary_checking"],
        apr_rate_in=0.0725,
        round_up=round_up_expenses_round_down_income,
    ),
    "Mortgage_Escrow": RecurringBill(
        name_in="Mortgage_Escrow",
        minimum_payment_in=MinorUnit.from_major(924.35),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 1),
        frequency_type_in=FrequencyType.MONTHLY,
        payment_method_in=accounts["primary_checking"],
        round_up=round_up_expenses_round_down_income,
    ),
    "Car_Payment_Ford": FinancedBill(
        name_in="Car Payment - Ford",
        balance_in=MinorUnit.from_major(25_578.05),
        account_type_in=AccountType.LOAN,
        initial_pay_date_in=date(2025, 11, 18),
        frequency_type_in=FrequencyType.MONTHLY,
        minimum_payment_in=MinorUnit.from_major(650.00),
        payment_method_in=accounts["primary_checking"],
        apr_rate_in=0.06,
        round_up=round_up_expenses_round_down_income,
    ),
    "Student_Loans": FinancedBill(
        name_in="Student Loans",
        balance_in=MinorUnit.from_major(35_000.00),
        account_type_in=AccountType.LOAN,
        initial_pay_date_in=date(2025, 11, 18),
        frequency_type_in=FrequencyType.MONTHLY,
        minimum_payment_in=MinorUnit.from_major(461.00),
        payment_method_in=accounts["primary_checking"],
        apr_rate_in=0.03,
        round_up=round_up_expenses_round_down_income,
    ),
    "Netflix": RecurringBill(
        name_in="Netflix",
        minimum_payment_in=MinorUnit.from_major(12.99),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 9),
        frequency_type_in=FrequencyType.MONTHLY,
        payment_method_in=accounts["primary_checking"],
        round_up=round_up_expenses_round_down_income,
    ),
    "Car_Insurance": RecurringBill(
        name_in="Car Insurance",
        minimum_payment_in=MinorUnit.from_major(300.00),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 16),
        frequency_type_in=FrequencyType.MONTHLY,
        payment_method_in=accounts["primary_checking"],
        round_up=round_up_expenses_round_down_income,
    ),
    "CrunchyRoll": RecurringBill(
        name_in="CrunchyRoll",
        minimum_payment_in=MinorUnit.from_major(11.99),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 13),
        frequency_type_in=FrequencyType.MONTHLY,
        payment_method_in=revolving_credit["discover_card"],
        round_up=round_up_expenses_round_down_income,
    ),
    "Spotify": RecurringBill(
        name_in="Spotify",
        minimum_payment_in=MinorUnit.from_major(11.99),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 13),
        frequency_type_in=FrequencyType.MONTHLY,
        payment_method_in=revolving_credit["discover_card"],
        round_up=round_up_expenses_round_down_income,
    ),
    "Internet": RecurringBill(
        name_in="Internet",
        minimum_payment_in=MinorUnit.from_major(69.99),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 3),
        frequency_type_in=FrequencyType.MONTHLY,
        payment_method_in=accounts["primary_checking"],
        round_up=round_up_expenses_round_down_income,
    ),
    "Utilities": RecurringBill(
        name_in="Utilities",
        minimum_payment_in=MinorUnit.from_major(200.00),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 1),
        frequency_type_in=FrequencyType.MONTHLY,
        payment_method_in=accounts["primary_checking"],
        round_up=round_up_expenses_round_down_income,
    ),
    "ADT": RecurringBill(
        name_in="ADT",
        minimum_payment_in=MinorUnit.from_major(50.00),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 15),
        frequency_type_in=FrequencyType.MONTHLY,
        payment_method_in=accounts["primary_checking"],
        round_up=round_up_expenses_round_down_income,
    ),
    "Food": RecurringBill(
        name_in="Food",
        minimum_payment_in=MinorUnit.from_major(75.00),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 1),
        frequency_type_in=FrequencyType.WEEKLY,
        payment_method_in=accounts["primary_checking"],
        round_up=round_up_expenses_round_down_income,
    ),
    "Gas": RecurringBill(
        name_in="Gas",
        minimum_payment_in=MinorUnit.from_major(10.00),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 1),
        frequency_type_in=FrequencyType.WEEKLY,
        payment_method_in=accounts["primary_checking"],
        round_up=round_up_expenses_round_down_income,
    ),
    "Cat_Bill": RecurringBill(
        name_in="Cat_Bill",
        minimum_payment_in=MinorUnit.from_major(60.00),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 28),
        frequency_type_in=FrequencyType.BI_WEEKLY,
        payment_method_in=accounts["primary_checking"],
        round_up=round_up_expenses_round_down_income,
    ),
}


write_object_to_file(
    file_path=SAVED_OBJECT_DATA / "temp.json",
    output_data=convert_objects_to_persistence_dict(bills | incomes | revolving_credit | accounts),
)

quit()
today = date(2025, 11, 1)
end_date = date(today.year + 10, today.month, today.day)

# let's update the initial dates to the simulated date
for collection in (bills, incomes, revolving_credit):
    for bill in collection:
        collection[bill].initialize_simulation_date(today)

# Walk Through Each day until we reach last day
while today < end_date:
    if today.day == 1:
        print(today)
    # process income
    for income in incomes:
        incomes[income].process_day(today)

    # Process Revolving Credit
    for credit in revolving_credit:
        revolving_credit[credit].process_day(today)

    # Process Bills
    for bill in bills:
        bills[bill].process_day(today)

    today += timedelta(days=1)


downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
output_path = os.path.join(downloads_folder, "Output_Analysis.xlsx")
workbook = Workbook(output_path)
accounting_format = workbook.add_format({"num_format": 44})
date_format = workbook.add_format({"num_format": 14})
for each in accounts:
    worksheet = workbook.add_worksheet(f"{each}_Table")
    add_table(
        worksheet_in=worksheet,
        table_name_in=each,
        header_in=accounts[each].ledger_header,
        data_in=accounts[each].raw_copy_ledger,
    )
    add_chart(
        workbook_in=workbook,
        worksheet_in=worksheet,
        table_name_in=each,
        col_in=xl_col_to_name(accounts[each].ledger_col_count + 1),
    )


for each in revolving_credit:
    worksheet = workbook.add_worksheet(f"{each}_Table")
    add_table(
        worksheet_in=worksheet,
        table_name_in=each,
        header_in=revolving_credit[each].ledger_header,
        data_in=revolving_credit[each].raw_copy_ledger,
    )
    add_chart(
        workbook_in=workbook,
        worksheet_in=worksheet,
        table_name_in=each,
        col_in=xl_col_to_name(revolving_credit[each].ledger_col_count + 1),
    )

for each in bills:
    worksheet = workbook.add_worksheet(f"{each}_Table")
    add_table(
        worksheet_in=worksheet,
        table_name_in=each,
        header_in=bills[each].ledger_header,
        data_in=bills[each].raw_copy_ledger,
    )
    if isinstance(bills[each], FinancedBill):
        add_chart(
            workbook_in=workbook,
            worksheet_in=worksheet,
            table_name_in=each,
            col_in=xl_col_to_name(bills[each].ledger_col_count + 1),
        )

workbook.close()


if __name__ == "__main__":
    pass
