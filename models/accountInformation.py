from models.enumType import AccountType

class AccountInformation:
    def __init__(self, name_in: str, balance_in: float, account_type_in: AccountType) -> None:
        self._balance: float = 0.00
        self._account_name: str = name_in
        self._account_type: AccountType = account_type_in
        self.update_balance(balance_in,0)

    @property
    def balance(self) -> float:
        # immutable type
        return self._balance

    @property
    def is_overdrafted(self) -> bool:
        # We only want to show over draft on checking and savings accounts
        if self._account_type in(AccountType.SAVINGS,AccountType.CHECKING):
            return self._balance<0
        return False

    @balance.setter
    def balance(self,dollar_amount_in:float) -> None:
        self._balance= dollar_amount_in

    def update_balance(self,credit:float=0, debit:float=0) -> None:
        self._balance = self._balance + credit - debit

    @property
    def account_name(self) -> str:
        # immutable type
        return self._account_name

    @property
    def account_type(self) -> AccountType:
        # immutable type
        return self._account_type
