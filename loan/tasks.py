import json
from time import sleep
from uuid import UUID

from celery import Celery
import etcd3
from decouple import config

from loan.models import RefusedPolicies, Result, Status
from loan.policies import check_age, check_commitment, check_score


RABBITMQ_USER = config('RABBITMQ_USER')
RABBITMQ_PASS = config('RABBITMQ_PASS')
RABBITMQ_HOST = config('RABBITMQ_HOST')
RABBITMQ_PORT = config('RABBITMQ_PORT')
URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}'

ETCD_HOST = config('ETCD_HOST')
ETCD_PORT = config('ETCD_PORT')


celery_app = Celery('tasks',
                    broker=URL)


@celery_app.task
def pipeline(loan_id: UUID):
    loan_id = str(loan_id)
    print(f'Checking {loan_id}')

    etcd = etcd3.client(host=ETCD_HOST,
                        port=ETCD_PORT)
    r = etcd.get(loan_id)
    request = json.loads(r[0])

    if not check_age(request):
        print('Under age')
        request['status'] = Status.COMPLETED
        request['result'] = Result.REFUSED
        request['refused_policy'] = RefusedPolicies.AGE
        etcd.put(loan_id, json.dumps(request))
        return

    if not check_score(request):
        print('Low score')
        request['status'] = Status.COMPLETED
        request['result'] = Result.REFUSED
        request['refused_policy'] = RefusedPolicies.SCORE
        etcd.put(loan_id, json.dumps(request))
        return

    if not check_commitment(request):
        print('Compromised commitment')
        request['status'] = Status.COMPLETED
        request['result'] = Result.REFUSED
        request['refused_policy'] = RefusedPolicies.COMMITMENT
        etcd.put(loan_id, json.dumps(request))
        return

    print('All policies OK')

    request['status'] = Status.COMPLETED
    request['result'] = Result.APPROVED
    etcd.put(loan_id, json.dumps(request))


if __name__ == '__main__':
    celery_app.start()