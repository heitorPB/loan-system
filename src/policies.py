from datetime import date

def check_age(loan_request):
    birth = loan_request['birthdate']
    birth = date.fromisoformat(birth)

    today = date.today()

    age = today.year - birth.year
    full_year = (today.month, today.day) < (birth.month, birth.day)

    if not full_year:
        age -= 1

    return age >= 18
