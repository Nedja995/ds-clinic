# DSKlinika

Medical analysis tools

## Using

### Without virtual environment

- Install dependencies: ```pip install -r requirements.txt```
- Run script: ```python dsclinic.py```

### Using virtual enviroment (venv)

- Create: ```python3.12 -m venv .venv```
- Activate (unix): ```source .venv/bin/activate```
- Activate (windows): ```.venv\Scripts\activate.bat```
- Install dependencies: ```pip install -r requirements.txt```
- Run script: ```python dsclinic.py```

### Parameters

Check ```config.py```

- Models:
  - gemini-3-pro-preview
  - gemini-3-flash-preview
  - gemini-3-pro-image-preview

## Development

### Make Windows executable

```bash
pyinstaller --onefile dsclinic.py
```

### Output format

- nalaz
- terapija
- napomena
