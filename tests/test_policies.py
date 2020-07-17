from datetime import date
from decimal import Decimal

from loan.policies import check_age

def test_underage():
    fake_request = {'birthdate': date.today().isoformat()}
    assert not check_age(fake_request)


def test_legalage():
    fake_request = {'birthdate': '1997-02-05'}
    assert check_age(fake_request)