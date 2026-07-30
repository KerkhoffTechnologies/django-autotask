## django-autotask

Django app for working with Autotask. Defines models (tickets,
resources, accounts, etc.).

## Requirements

-  Python 3.12, 3.13 or 3.14
-  Django 4.2, 5.2 or 6.0
-  PostgreSQL (the models declare `GinIndex` indexes)

Other versions may work; we haven't tried.

## Installation

From source:

    git clone git@github.com:KerkhoffTechnologies/django-autotask.git
    cd django-autotask
    pip install .

## Usage

1. Add to INSTALLED_APPS

    ```
    INSTALLED_APPS = [
        ...
        'djautotask',
        'django.contrib.postgres',
        ...
    ]
    ```

    `django.contrib.postgres` is required: our models declare `GinIndex`
    indexes, and as of Django 6.0 the `postgres.E005` system check fails
    if the app is not installed.


## Testing

```
pip install --upgrade -r requirements_test.txt
```

Try one of:

    ./runtests.py
    make test

## Contributing

- Fork this repo
- Make a branch
- Make your improvements

    Making migrations? Run:

    ```
    ./makemigrations.py
    ```

- Run the tests (see above)
- Make a pull request

## License

MIT

## Copyright

©2018 Kerkhoff Technologies Inc.
