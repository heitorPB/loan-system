from time import sleep

from fastapi.testclient import TestClient

from loan.main import app

client = TestClient(app)


def test_invalid_cpf():
    data = {"name": "Alcis",
            "cpf": "1",
            "birthdate": "2000-07-16",
            "amount": 2500,
            "terms": "6",
            "income": 550}
    response = client.post('/loan', json=data)
    assert response.status_code == 422
    assert response.json() == {
                                "detail": [
                                  {
                                    "loc": [
                                      "body",
                                      "cpf"
                                    ],
                                    "msg": "string does not match regex \"^\\d{14}|\\d{2}.\\d{3}.\\d{3}/\\d{4}-\\d{2}$\"",
                                    "type": "value_error.str.regex",
                                    "ctx": {
                                      "pattern": "^\\d{14}|\\d{2}.\\d{3}.\\d{3}/\\d{4}-\\d{2}$"
                                    }
                                  }
                                ]
                              }


def test_low_amount():
    data = {"name": "Baldr",
            "cpf": "1"*14,
            "birthdate": "2000-01-01",
            "amount": 500,
            "terms": "6",
            "income": 550}
    response = client.post('/loan', json=data)
    assert response.status_code == 422
    assert response.json() == {
                                "detail": [
                                  {
                                    "loc": [
                                      "body",
                                      "amount"
                                    ],
                                    "msg": "ensure this value is greater than or equal to 1000",
                                    "type": "value_error.number.not_ge",
                                    "ctx": {
                                      "limit_value": 1000
                                    }
                                  }
                                ]
                              }


def test_high_amount():
    data = {"name": "Dellingr",
            "cpf": "1"*14,
            "birthdate": "2000-01-01",
            "amount": 9500,
            "terms": "6",
            "income": 550}
    response = client.post('/loan', json=data)
    assert response.status_code == 422
    assert response.json() == {
                                "detail": [
                                  {
                                    "loc": [
                                      "body",
                                      "amount"
                                    ],
                                    "msg": "ensure this value is less than or equal to 4000",
                                    "type": "value_error.number.not_le",
                                    "ctx": {
                                      "limit_value": 4000
                                    }
                                  }
                                ]
                              }


def test_invalid_terms():
    for n in range(1, 16, 2):
        data = {"name": "Eir",
                "cpf": "1"*14,
                "birthdate": "2000-01-01",
                "amount": 2500,
                "terms": n,
                "income": 550}
        response = client.post('/loan', json=data)
        assert response.status_code == 422
        assert response.json() == {
                                   "detail": [
                                     {
                                       "loc": [
                                         "body",
                                         "terms"
                                       ],
                                       "msg": "value is not a valid enumeration member; permitted: '6', '9', '12'",
                                       "type": "type_error.enum",
                                       "ctx": {
                                         "enum_values": [
                                           "6",
                                           "9",
                                           "12"
                                         ]
                                       }
                                     }
                                   ]
                                 }

def test_valid_terms():
    for n in [6, 9, 12]:
        data = {"name": "Freyja",
                "cpf": "1"*14,
                "birthdate": "2000-01-01",
                "amount": 2500,
                "terms": str(n),
                "income": 550}
        response = client.post('/loan', json=data)
        assert response.ok


def test_underage():
    data = {"name": "Gersemi",
            "cpf": "1"*14,
            "birthdate": "2020-04-02",
            "amount": 2500,
            "terms": "6",
            "income": 550}
    response = client.post('/loan', json=data)
    assert response.ok

    # wait a bit to process this loan request
    sleep(2)
    response = client.get(f"/loan/{response.json()['id']}")
    data = response.json()
    assert response.ok
    assert data['status'] == "completed"
    assert data['result'] == "refused"
    assert data['refused_policy'] == "age"
    assert data['amount'] == 2500
    assert data['terms'] == 6


def test_low_score():
    data = {"name": "Heimdallr",
            "cpf": "12312312312312",
            "birthdate": "2000-04-02",
            "amount": 2500,
            "terms": "6",
            "income": 550}
    response = client.post('/loan', json=data)
    assert response.ok

    # wait a bit to process this loan request
    sleep(2)
    response = client.get(f"/loan/{response.json()['id']}")
    data = response.json()
    assert response.ok
    assert data['status'] == "completed"
    assert data['result'] == "refused"
    assert data['refused_policy'] == "score"
    assert data['amount'] == 2500
    assert data['terms'] == 6


def test_low_commitment():
    data = {"name": "Ilmr",
            "cpf": "12312322342300",
            "birthdate": "2000-04-02",
            "amount": 4000,
            "terms": "6",
            "income": 550}
    response = client.post('/loan', json=data)
    assert response.ok

    # wait a bit to process this loan request
    sleep(2)
    response = client.get(f"/loan/{response.json()['id']}")
    data = response.json()
    assert response.ok
    assert data['status'] == "completed"
    assert data['result'] == "refused"
    assert data['refused_policy'] == "commitment"
    assert data['amount'] == 4000
    assert data['terms'] == 0


def test_good_loan():
    data = {"name": "Loki",
            "cpf": "12312312312311",
            "birthdate": "2000-04-02",
            "amount": 1000,
            "terms": "6",
            "income": 1234}
    response = client.post('/loan', json=data)
    assert response.ok

    # wait a bit to process this loan request
    sleep(2)
    response = client.get(f"/loan/{response.json()['id']}")
    data = response.json()
    assert response.ok
    assert data['status'] == "completed"
    assert data['result'] == "approved"
    assert data['refused_policy'] == ""
    assert data['amount'] == 1000
    assert data['terms'] == 6


def test_loan_not_found():
    id_ = '00000000-0000-0000-0000-000000000000'
    response = client.get(f"/loan/{id_}")
    assert response.status_code == 404
    assert response.json() == {'detail': f"Loan {id_} not found"}
