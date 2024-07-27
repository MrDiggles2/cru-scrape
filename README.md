
# Install Poetry (if you don't have it)
To check if you have it run
```
which poetry
```
To install poetry run
```
curl -sSL https://install.python-poetry.org | python3 -
```
## How to uninstall if you want
```
curl -sSL https://install.python-poetry.org | python3 - --uninstall
```

# Install dependencies 
Run this, it should create the virtual environment for you at the same time
```
poetry install
```

# Run the code
```
cd src
poetry run main.py
```
