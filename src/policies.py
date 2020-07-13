from datetime import date

from decouple import config
import requests

API_KEY = config('API_KEY')
SCORE_URL = 'https://challenge.noverde.name/score'

def check_age(loan_request):
    birth = loan_request['birthdate']
    birth = date.fromisoformat(birth)

    today = date.today()

    age = today.year - birth.year
    full_year = (today.month, today.day) < (birth.month, birth.day)

    if not full_year:
        age -= 1

    return age >= 18


def check_score(request):
    headers = {'x-api-key': API_KEY}
    payload = {'cpf': request['cpf']}
    r = requests.post(SCORE_URL, headers=headers, json=payload)
    score = r.json()['score']

    return score > 600
