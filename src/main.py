import json
from uuid import UUID, uuid4

import etcd3
from decouple import config
from fastapi import FastAPI, HTTPException

from .models import Id, Loan, LoanStatus, Error
from .tasks import celery_app


ETCD_HOST = config('ETCD_HOST', default='localhost')
ETCD_PORT = config('ETCD_PORT', default='2379')

app = FastAPI(title='Loan System',
              description="Parse and accept/decline a user's request for loans",
              version='0.2.0')


@app.post('/loan',
          response_model=Id,
          status_code=201)
async def request_loan(loan: Loan):
    uuid = uuid4()
    data = {'id': str(uuid),
            'name': loan.name,
            'cpf': loan.cpf,
            'birthdate': loan.birthdate.isoformat(),
            'amount': loan.amount,
            'terms': loan.terms.value,
            'income': loan.income,
            'status': 'processing',
            'result': '',
            'refused_policy': ''}
    body = json.dumps(data)

    etcd = etcd3.client(host=ETCD_HOST,
                        port=ETCD_PORT)
    r = etcd.put(str(uuid), body)

    celery_app.send_task('src.tasks.pipeline', args=[str(uuid)])

    return {'id': uuid}


@app.get('/loan/{loan_id}',
         response_model=LoanStatus,
         responses={404: {"model": Error}})
async def loan_status(loan_id: UUID):
    etcd = etcd3.client(host=ETCD_HOST,
                        port=ETCD_PORT)
    r = etcd.get(str(loan_id))
    data = r[0]
    if data is None:
        raise HTTPException(status_code=404,
                            detail=f"Loan {loan_id} not found")

    data = json.loads(data)
    status = LoanStatus(**data)
    return status
