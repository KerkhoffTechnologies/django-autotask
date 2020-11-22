## django-autotask

Django app for working with Autotask. Defines models (tickets,
resources, accounts, etc.).

## Requirements

-  Python 3.5
-  Django 2.0

Other versions may work; we haven't tried.

## Installation

From source:

    git clone git@github.com:KerkhoffTechnologies/django-autotask.git
    cd django-autotask
    python setup.py install

## Usage

1. Add to INSTALLED_APPS

    ```
    INSTALLED_APPS = [
        ...
        'djautotask',
        ...
    ]
    ```


## Testing

```
pip install --upgrade -r requirements_test.txt
```

Try one of:

    ./runtests.py
    python setup.py test
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
