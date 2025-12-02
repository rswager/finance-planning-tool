from models.bankAccount import BankAccount
from models.financed_bill import FinancedBill
from models.income import Income
from models.recurring_bill import RecurringBill
from models.revolving_credit_bill import RevolvingCreditBill
from resources.model_tables import ModelTables

headers = {
    BankAccount: ["Name", "Type", "Balance"],
    Income: ["Name", "Amt", "Frequency"],
    RevolvingCreditBill: ["Name", "Limit", "Min Payment", "Frequency"],
    FinancedBill: ["Name", "Financed Amt", "Min Payment", "Frequency"],
    RecurringBill: ["Name", "Payment Amt", "Frequency"]
}

class ModelManager:
    def __init__(self, table_reference, model_type_in, model_data_in=None):
        self.model = model_data_in if model_type_in is not None else {}
        self.model_type = model_type_in
        self.table_model = ModelTables(table_reference=table_reference,header_in=headers[self.model_type])



    # def get_data(self):
    #     # BankAccount: ["Name", "Type", "Balance"],
    #     # Income: ["Name", "Amt", "Frequency"],
    #     # RevolvingCreditBill: ["Name", "Limit", "Min Payment", "Frequency"],
    #     # FinancedBill: ["Name", "Financed Amt", "Min Payment", "Frequency"],
    #     # RecurringBill: ["Name", "Payment Amt", "Frequency"]
    #
    #     for model in model_data_in:
    #         finance_model = model_data_in[model]
    #         each = []
    #         if type(finance_model) == BankAccount :
    #             each = [finance_model.account_name, finance_model.account_type.name, f'${finance_model.balance_dollars:,.2f}']
    #         elif type(finance_model) == Income:
    #             each = [finance_model.account_name, f'${finance_model.income_amount_dollars:,.2f}',finance_model.frequency.name]
    #         elif type(finance_model) == RevolvingCreditBill:
    #             each = [finance_model.account_name, f'${finance_model.credit_limit_dollars:,.2f}',
    #                     f'${finance_model.min_payment_dollars:,.2f}', finance_model.frequency.name]
    #         elif type(finance_model) == FinancedBill:
    #             each = [finance_model.account_name,f"${finance_model.loan_balance_dollars:,.2f}",
    #                     f"${finance_model.min_payment_dollars:,.2f}",finance_model.frequency.name]
    #         elif type(finance_model) == RecurringBill:
    #             each = [finance_model.account_name,f"${finance_model.min_payment_dollars:,.2f}",
    #                     finance_model.frequency.name]
    #         else:
    #              return
    #         row_items = []
    #         for col in each:

