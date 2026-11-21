from enum import Enum


class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"


class NormalBalance(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class OverdraftPolicy(str, Enum):
    DISALLOW = "disallow"
    ALLOW = "allow"
    LIMIT = "limit"
