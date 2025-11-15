from datetime import date, timedelta
from models.bankAccount import BankAccount
from models.enumType import AccountType, FrequencyType
from models.financed_bill import FinancedBill
from models.income import Income
from models.recurring_bill import RecurringBill
from models.revolving_credit_bill import RevolvingCreditBill
import os
import xlsxwriter


def get_col(col_num_in):
    col = ['A', 'B', 'C', 'D', 'E', 'F',
           'G', 'H', 'I', 'J', 'K', 'L',
           'M', 'N', 'O', 'P', 'Q', 'R',
           'S', 'T', 'U', 'V', 'W', 'X',
           'Y', 'Z']

    if col_num_in < 26:
        return col[col_num_in]
    elif col_num_in > 701:
        return False
    else:
        factor = int(col_num_in / 26) - 1
        remain = (col_num_in % 26)
        return str(col[factor]) + str(col[remain])


def add_table(worksheet_in, table_name_in, data_in):
    data = data_in
    header_in = data.pop(0)
    header = []
    # first row of data
    for index, column_data in enumerate(data[0]):
        if type(column_data) in(float,int) and index != 0:
            column_def = {'header': header_in[index], 'format': accounting_format}
        elif type(column_data) == date:
            column_def = {'header': header_in[index], 'format': date_format}
        else:
            column_def = {'header': header_in[index]}
        header.append(column_def)

    worksheet_in.add_table(f'A1:{get_col(len(header)-1)}{len(data)+1}', {
        'header_row': True,
        'data': data,
        'total_row': False, 'autofilter': True,
        'columns': header, 'style': "Table Style Medium 9",
        'name': f'{str(table_name_in)}_Table'
    })


def add_chart(workbook_in, worksheet_in, table_name_in, col_in):
    chart = workbook_in.add_chart({'type': 'line'})
    chart.add_series({
        'categories': f'{table_name_in}_Table[Date]',
        'values': f'{table_name_in}_Table[Balance]',
        'name': 'Projected Balance'
    })

    worksheet_in.insert_chart(f'{col_in}1', chart, {'x_scale': 2.5, 'y_scale': 2.5})

round_up_down= False
accounts = {
        'primary_checking': BankAccount(name_in='Primary Checking', account_type_in= AccountType.CHECKING,
                                        balance_in=2_261.33),
        'primary_savings': BankAccount(name_in='Primary Savings', account_type_in=AccountType.SAVINGS,
                                       balance_in=3_286.11)
    }

revolving_credit = {
    'discover_card': RevolvingCreditBill(name_in='Discovery', balance_in=693.65, account_type_in=AccountType.REVOLVING,
                                         initial_pay_date_in=date(2025,11,28),
                                         frequency_type_in=FrequencyType.MONTHLY, minimum_payment_in=400.00,
                                         payment_method_in=accounts['primary_checking'],apr_rate_in=.15,
                                         credit_limit_in=30_000.00,round_up=round_up_down
                                        )
}

incomes = {
    'primary_Income':Income(name_in='Primary Job', income_in=2_557.31,
                       initial_pay_date_in=date(2025, 11, 6),
                        account_contributions_in=
                            [
                                (accounts['primary_checking'], .9),  # 90% to primary checking
                                (accounts['primary_savings'], .1)  # 10% to primary savings
                             ],
                       frequency_type_in=FrequencyType.BI_WEEKLY, round_down=round_up_down)
}

bills = {
    'Mortgage': FinancedBill(name_in='Mortgage', balance_in=132_367.00, account_type_in=AccountType.LOAN,
                                         initial_pay_date_in=date(2025,11,1),
                                         frequency_type_in=FrequencyType.MONTHLY, minimum_payment_in=924.35,
                                         payment_method_in=accounts['primary_checking'],apr_rate_in=.0725,
                                         round_up=round_up_down),

    'Mortgage_Escrow': RecurringBill(name_in='Mortgage_Escrow', minimum_payment_in=924.35,account_type_in=AccountType.REOCCURRING,
                             initial_pay_date_in=date(2025, 11, 1),
                             frequency_type_in=FrequencyType.MONTHLY,
                             payment_method_in=accounts['primary_checking'], round_up=round_up_down),

    'Car_Payment_Ford': FinancedBill(name_in='Car Payment - Ford', balance_in=28_000.00,
                                       account_type_in=AccountType.LOAN,initial_pay_date_in=date(2025,11,15),
                                       frequency_type_in=FrequencyType.MONTHLY, minimum_payment_in=450.00,
                                       payment_method_in=accounts['primary_checking'], apr_rate_in=.06,
                                       round_up=round_up_down),

    'Student_Loans': FinancedBill(name_in='Student Loans', balance_in=35_000.00,
                                  account_type_in=AccountType.LOAN, initial_pay_date_in=date(2025, 11, 18),
                                  frequency_type_in=FrequencyType.MONTHLY, minimum_payment_in=461.00,
                                  payment_method_in=accounts['primary_checking'], apr_rate_in=.03,
                                  round_up=round_up_down),

    'Netflix': RecurringBill(name_in='Netflix', minimum_payment_in=12.99,account_type_in=AccountType.REOCCURRING,
                             initial_pay_date_in=date(2025, 11, 9),
                             frequency_type_in=FrequencyType.MONTHLY,
                             payment_method_in=accounts['primary_checking'], round_up=round_up_down),

    'Car_Insurance': RecurringBill(name_in='Car Insurance', minimum_payment_in=300.00,account_type_in=AccountType.REOCCURRING,
                             initial_pay_date_in=date(2025, 11, 16),
                             frequency_type_in=FrequencyType.MONTHLY,
                             payment_method_in=accounts['primary_checking'], round_up=round_up_down),


    'CrunchyRoll': RecurringBill(name_in='CrunchyRoll', minimum_payment_in=11.99,account_type_in=AccountType.REOCCURRING,
                             initial_pay_date_in=date(2025, 11, 13),
                             frequency_type_in=FrequencyType.MONTHLY,
                             payment_method_in=revolving_credit['discover_card'], round_up=round_up_down),

    'Spotify': RecurringBill(name_in='Spoify', minimum_payment_in=11.99, account_type_in=AccountType.REOCCURRING,
                                 initial_pay_date_in=date(2025, 11, 13),
                                 frequency_type_in=FrequencyType.MONTHLY,
                                 payment_method_in=revolving_credit['discover_card'], round_up=round_up_down),

    'Internet': RecurringBill(name_in='Internet', minimum_payment_in=59.99,account_type_in=AccountType.REOCCURRING,
                             initial_pay_date_in=date(2025, 11, 3),
                             frequency_type_in=FrequencyType.MONTHLY,
                             payment_method_in=accounts['primary_checking'], round_up=round_up_down),

    'Utilities': RecurringBill(name_in='Utilities', minimum_payment_in=150.00,account_type_in=AccountType.REOCCURRING,
                             initial_pay_date_in=date(2025, 11, 1),
                             frequency_type_in=FrequencyType.MONTHLY,
                             payment_method_in=accounts['primary_checking'], round_up=round_up_down),

    'ADT': RecurringBill(name_in='ADT', minimum_payment_in=50.00,account_type_in=AccountType.REOCCURRING,
                             initial_pay_date_in=date(2025, 11, 15),
                             frequency_type_in=FrequencyType.MONTHLY,
                             payment_method_in=accounts['primary_checking'], round_up=round_up_down),

    'Food': RecurringBill(name_in='Food', minimum_payment_in=75.00, account_type_in=AccountType.REOCCURRING,
                             initial_pay_date_in=date(2025, 11, 1),
                             frequency_type_in=FrequencyType.WEEKLY,
                             payment_method_in=accounts['primary_checking'], round_up=round_up_down),

    'Fun': RecurringBill(name_in='Fun', minimum_payment_in=25.00, account_type_in=AccountType.REOCCURRING,
                             initial_pay_date_in=date(2025, 11, 1),
                             frequency_type_in=FrequencyType.WEEKLY,
                             payment_method_in=accounts['primary_checking'], round_up=round_up_down),

    'Gas': RecurringBill(name_in='Gas', minimum_payment_in=10.00, account_type_in=AccountType.REOCCURRING,
                             initial_pay_date_in=date(2025, 11, 1),
                             frequency_type_in=FrequencyType.WEEKLY,
                             payment_method_in=accounts['primary_checking'], round_up=round_up_down),

    'Therapy': RecurringBill(name_in='Therapy', minimum_payment_in=30.00, account_type_in=AccountType.REOCCURRING,
                             initial_pay_date_in=date(2025, 11, 8),
                             frequency_type_in=FrequencyType.BI_WEEKLY,
                             payment_method_in=accounts['primary_checking'], round_up=round_up_down),

    'Cat_Bill': RecurringBill(name_in='Cat_Bill', minimum_payment_in=60.00, account_type_in=AccountType.REOCCURRING,
                             initial_pay_date_in=date(2025, 11, 28),
                             frequency_type_in=FrequencyType.BI_WEEKLY,
                             payment_method_in=accounts['primary_checking'], round_up=round_up_down)
}


today = date(2025, 11, 1)
end_date = date(2035, 11, 1)
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
workbook = xlsxwriter.Workbook(output_path)
accounting_format = workbook.add_format({'num_format': 44})
date_format = workbook.add_format({'num_format': 14})
for each in accounts:
    worksheet = workbook.add_worksheet(f'{each}_Table')
    add_table(worksheet_in=worksheet, table_name_in=each, data_in=accounts[each].raw_copy_ledger)
    add_chart(workbook_in=workbook, worksheet_in=worksheet, table_name_in=each,
              col_in=get_col(accounts[each].ledger_col_count+1))


for each in revolving_credit:
    worksheet = workbook.add_worksheet(f'{each}_Table')
    add_table(worksheet_in=worksheet, table_name_in=each, data_in=revolving_credit[each].raw_copy_ledger)
    add_chart(workbook_in=workbook, worksheet_in=worksheet, table_name_in=each,
              col_in=get_col(revolving_credit[each].ledger_col_count+1))

for each in bills:
    worksheet = workbook.add_worksheet(f'{each}_Table')
    add_table(worksheet_in=worksheet, table_name_in=each, data_in=bills[each].raw_copy_ledger)
    if isinstance(bills[each], FinancedBill):
        add_chart(workbook_in=workbook, worksheet_in=worksheet, table_name_in=each,
                  col_in=get_col(bills[each].ledger_col_count+1))

workbook.close()