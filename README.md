# Loan System

Simple REST system for loan requests.

## Architecture

The server receives HTTP requests with details about the loan. This is stored
in the database and queued to be processed later. The workers get an
instruction from the queue, process it and store in the database.

Techs used:
- [Celery](https://celeryproject.org/) as task queue
- [etcd](https://etcd.io) as key-value store
- [RabbitMQ](https://www.rabbitmq.com) as messaging system (backend for Celery)
- [FastAPI](https://fastapi.tiangolo.com) as the web framework


## Endpoints

This system has 3 endpoints:

- POST `/loan`: to request a loan
- GET `/loan/{id}`: to query the status/result of a request


## Running

The first step is to acquire an API secret key. Then, modify
[settings.ini](settings.ini) with it and follow the next sections.

### Docker

The simplest way:

```
$ docker-compose up -d
```

This will fire etcd, rabbitmq, the server and the worker.

RabbitMQ provides a [web Management system](http://localhost:15672).

etcd provides [metrics](http://localhost:2379/metrics) and [health
check](http://localhost:2379/health) for monitoring.

The server uses [gunicorn](https://gunicorn.org/) to manage
[uvicorn](https://www.uvicorn.org/) workers.

### Manually (dev environment)

It's also possible to run the server and the worker in the terminal. They
require a RabbitMQ and etcd instances somewhere. The default is to check
`localhost` on their default ports, but it can be changed with environment
variables. Check the [docker-compose](docker-compose.yml) file for details.

Install the dependencies and run:

```
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ uvicorn loan.main:app --reload & # reload flag to autoreload on file changes
$ celery -A loan.tasks worker --loglevel=info
```

### Tests

Tests are available in the folder [tests](tests/), using `pytest`. To run them,
first start RabbitMQ and etcd:

```
$ docker-compose up -d etcd rabbitmq
```

The worker needs to be up to process the tasks:

```
$ docker-compose up -d worker
```

Now, run `pytest` and generate a nice HTML coverage report:

```
$ coverage run -m --souce=loan pytest
$ coverage html
```

The report is available in `htmlcov/index.html`.

Note: if your computer is to busy, you might need to increase the `sleep`s in
the test code, this way the worker can process before checking the result.


## Using

After the system boots up (might take a while, but less than a minute), check
the online documentation at:

- [swagger](http://localhost/docs)
- [redoc](http://localhost/redoc)
- [openapi documentation](http://localhost/openapi.json)

A simple way to test the system is to access the swagger and use the `Try it
out` buttons on each endpoint.


## License

Distributed under the GNU GPLv3. See [LICENSE](LICENSE) for details.
