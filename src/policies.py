from datetime import date
from functools import lru_cache

from decouple import config
import requests

API_KEY = config('API_KEY')
SCORE_URL = 'https://challenge.noverde.name/score'
COMMITMENT_URL = 'https://challenge.noverde.name/commitment'

# TODO retry any policy in case it is impossible to contact score/commitment
#      systems

def check_age(loan_request) -> bool:
    birth = loan_request['birthdate']
    birth = date.fromisoformat(birth)

    today = date.today()

    age = today.year - birth.year
    full_year = (today.month, today.day) < (birth.month, birth.day)

    if not full_year:
        age -= 1

    return age >= 18

@lru_cache
def get_score(cpf: str) -> int:
    headers = {'x-api-key': API_KEY}
    payload = {'cpf': cpf}
    r = requests.post(SCORE_URL, headers=headers, json=payload)
    score = r.json()['score']
    return score


def check_score(request) -> bool:
    score = get_score(request['cpf'])
    return score > 600


def get_commitment(cpf: str) -> float:
    headers = {'x-api-key': API_KEY}
    payload = {'cpf': cpf}
    r = requests.post(COMMITMENT_URL, headers=headers, json=payload)
    commitment = r.json()['commitment']
    return commitment


def interest(score: int, parcels: int) -> float:
    """Monthly interest rate, based on score and number of parcels"""

    # TODO change from float to decimal
    if 600 <= score <= 699:
        if 6 == parcels: return 3.9/100
        if 9 == parcels: return 4.2/100
        if 12 == parcels: return 4.5/100
    elif 700 <= score <= 799:
        if 6 == parcels: return 4.7/100
        if 9 == parcels: return 5.0/100
        if 12 == parcels: return 5.3/100
    elif 800 <= score <= 899:
        if 6 == parcels: return 5.5/100
        if 9 == parcels: return 5.8/100
        if 12 == parcels: return 6.1/100
    elif 900 <= score:
        if 6 == parcels: return 6.4/100
        if 9 == parcels: return 6.6/100
        if 12 == parcels: return 6.9/100


def calculate_parcel(pv, n, i) -> float:
    """ Calculate parcel value

    - pv: present value - request loan value
    - n: number of parcels
    - i: monthly interest rate
    """
    return pv * (i + 1)**n * i / ((i + 1)**n - 1)


def calculate_number_of_parcels(available_income,
                                requested_amount,
                                requested_parcels,
                                score):
    i = interest(score, requested_parcels)
    parcel = calculate_parcel(requested_amount, requested_parcels, i)

    if parcel > available_income:
        # increase number of parcels and try again
        if 6 == requested_parcels:
            return calculate_number_of_parcels(available_income,
                                               requested_amount, 9, score)
        elif 9 == requested_parcels:
            return calculate_number_of_parcels(available_income,
                                               requested_amount, 12, score)
        else:
            return 0

    return requested_parcels


def check_commitment(request) -> bool:
    commitment = get_commitment(request['cpf'])
    compromised = commitment * request['income']
    available_income = (1 - commitment) * request['income']

    amount = float(request['amount'])
    score = get_score(request['cpf'])
    n = int(request['terms'])

    number_of_parcels = calculate_number_of_parcels(available_income, amount, n, score)
    request['terms'] = number_of_parcels

    return number_of_parcels > 0
