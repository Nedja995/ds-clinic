# DSKlinika

Medical analysis tools

## Using

### Using virtual enviroment (venv)

- Create: `python -m venv .venv`
- Activate (unix): `source .venv/bin/activate`
- Activate (windows): `.venv\Scripts\activate.bat`
- Install dependencies: `pip install -r requirements.txt`
- spacy dep: `python -m spacy download en_core_web_sm`
- spacy dep: `python -m spacy download en_core_web_lg` (no)
- Run script: `python dsclinic.py`

### Parameters

Check ```config.py, settings.ini, config.json```

### Usage with Poetry

#### MacOS brew: `brew install pipx`

```bash
pipx install poetry
poetry install
poetry run python dsclinic.py
```

#### Windows PowerShell: `Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -`

Add to PATH: After installation, you may need to manually add the installation path to your system's environment variables if prompted. The default location is typically %APPDATA%\pypoetry or %APPDATA%\Python\Scripts. The installer output should provide the exact path. You might need to close and reopen PowerShell for the changes to take effec.

## Development

### Make Windows executables

```bash
# CLI
pyinstaller --noconfirm --onefile --console --name "DSClinic_v2_0_1" --paths "src" src/dsclinic_cli.py

# Win
#pyinstaller --noconfirm --onefile --windowed --name "Holisticki Centar Dar Prirode - Izvestaji" --paths "src" src/dsclinic_gui/dsclinic_gui_app.py
pyinstaller --noconfirm --onefile --windowed --name "MedAI Assistant - ViTec" --paths "src" src/dsclinic_gui/dsclinic_gui_app.py

# Win icon (dont work)
pyinstaller --noconfirm --onefile --windowed --name "Holisticki Centar Dar Prirode - Izvestaji" --icon "src/assets/icon.ico" --add-data "src/assets/icon.ico;." --paths "src" src/dsclinic_gui/dsclinic_gui_app.py

# 
pyinstaller --noconfirm --onefile --windowed --name "DSClinicGUI" --paths "src" src/testgui.py
```

### VSCode Project Configuration

- Windows: `"autopep8.interpreter":["${workspaceFolder}/.venv/Scripts/python.exe"]`

- Unix: `"autopep8.interpreter":["${workspaceFolder}/.venv/bin/python"]`

### Output data

- title
- date
- patient_name
- diagnosis
- findings table
- additional: chat responses
