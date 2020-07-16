from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class Terms(str, Enum):
    SIX = 6
    NINE = 9
    TWELVE = 12


class Id(BaseModel):
    id: UUID


class Status(str, Enum):
    PROCESSING = 'processing'
    COMPLETED = 'completed'


class Result(str, Enum):
    APPROVED = 'approved'
    REFUSED = 'refused'
    NULL = ''

class RefusedPolicies(str, Enum):
    AGE = 'age'
    COMMITMENT = 'commitment'
    SCORE = 'score'
    NULL = ''


class LoanStatus(BaseModel):
    id: UUID
    status: Status
    result: Result
    refused_policy: RefusedPolicies
    amount: Decimal
    terms: int


class Loan(BaseModel):
    name: str = Field(..., max_length=80, description="Client's name")
    cpf: str = Field(..., regex="^\d{14}|\d{2}.\d{3}.\d{3}/\d{4}-\d{2}$",
                     description="CPF with or without formatting")
    birthdate: date = Field(..., description="Client's birthdate (YYYY-MM-DD)")
    amount: Decimal = Field(..., ge=1000, le=4000, description="Loan amount")
    terms: Terms = Field(..., description="Desired number of terms")
    income: Decimal = Field(..., description="Client's monthly income")


class Error(BaseModel):
    detail: str
