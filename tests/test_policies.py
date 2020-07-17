from datetime import date
from decimal import Decimal

from loan.policies import check_age, get_score, check_score, get_commitment, \
                          interest

def test_underage():
    fake_request = {'birthdate': date.today().isoformat()}
    assert not check_age(fake_request)


def test_legalage():
    fake_request = {'birthdate': '1997-02-05'}
    assert check_age(fake_request)


def test_score():
    assert get_score('12312312312310') == 208
    assert get_score('12312312312311') == 698
    assert get_score('12312312312312') == 381
    assert get_score('12312312312313') == 174
    assert get_score('12312312312314') == 758
    assert get_score('12312312312315') == 170
    assert get_score('12312312312316') == 690
    assert get_score('12312312312317') == 116

    assert check_score({'cpf': '12312312312310'}) == False
    assert check_score({'cpf': '12312312312311'}) == True
    assert check_score({'cpf': '12312312312312'}) == False
    assert check_score({'cpf': '12312312312313'}) == False
    assert check_score({'cpf': '12312312312314'}) == True
    assert check_score({'cpf': '12312312312315'}) == False
    assert check_score({'cpf': '12312312312316'}) == True
    assert check_score({'cpf': '12312312312317'}) == False

def test_commitment_value():
    assert get_commitment('12312312312310') == Decimal('.57')
    assert get_commitment('12312312312311') == Decimal('.47')
    assert get_commitment('12312312312312') == Decimal('.36')
    assert get_commitment('12312312312313') == Decimal('.72')
    assert get_commitment('12312312312314') == Decimal('.99')
    assert get_commitment('12312312312315') == Decimal('.62')
    assert get_commitment('12312312312316') == Decimal('.14')
    assert get_commitment('12312312312317') == Decimal('.83')


def test_interest():
    assert interest(900, 6) == Decimal('0.039')
    assert interest(900, 9) == Decimal('0.042')
    assert interest(900, 12) == Decimal('0.045')
    assert interest(800, 6) == Decimal('0.047')
    assert interest(800, 9) == Decimal('0.05')
    assert interest(800, 12) == Decimal('0.053')
    assert interest(700, 6) == Decimal('0.055')
    assert interest(700, 9) == Decimal('0.058')
    assert interest(700, 12) == Decimal('0.061')
    assert interest(600, 6) == Decimal('0.064')
    assert interest(600, 9) == Decimal('0.066')
    assert interest(600, 12) == Decimal('0.069')