
# Install Poetry (if you don't have it)
To check if you have it run
```
which poetry
```
To install poetry run
```
curl -sSL https://install.python-poetry.org | python3 -
```

Don't forget to add the poetry path to your bashrc, it will give you the export command at the end of the install logs

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
poetry run python main.py
```

# How to add libraries
```
poetry add <library name>
```