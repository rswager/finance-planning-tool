from enum import Enum

class FrequencyType(Enum):
    MONTHLY = 1
    BI_WEEKLY = 2
    WEEKLY = 3
    DAILY = 4

class AccountType(Enum):
    CHECKING = 1
    SAVINGS = 2
    LOAN = 3
    REVOLVING = 4
    SUBSCRIPTION = 5
    REOCCURRING = 6
