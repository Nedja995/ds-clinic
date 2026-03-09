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

### Make Windows executable (CLI)

```bash
pyinstaller --noconfirm --onefile --console --name "DSClinic_v2_0_1" --paths "src" src/main.py
```

### Make Windows executable (GUI)

```bash
pyinstaller --noconfirm --onefile --windowed --name "DSClinicGUI2" --paths "src" src/gui_dsclinic/main.py
```

```bash
pyinstaller --noconfirm --onefile --windowed --name "DSClinicGUI" --paths "src" testgui.py
```

### VSCode Project Configuration

- Windows: `"autopep8.interpreter":["${workspaceFolder}/.venv/Scripts/python.exe"]`

- Unix: `"autopep8.interpreter":["${workspaceFolder}/.venv/bin/python"]`

### Output format

- nalaz
- terapija
- napomena
