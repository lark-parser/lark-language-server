# lark-language-server
Provides a language server for the Lark grammar.

## Development

Layout:
```
├── lark_language_server  # The lang server python package
└── editors   # Editor specific extensions
    └── vscode   # VSCode language server client extension
```


Development is against the VSCode extension:
- Open the root directory in VSCode
- Create a local python virtualenv i.e. `python -m venv .venv`
- Install the language server package in development mode `pip install -e .`
- Create `.vscode/settings.json` file and set `python.pythonPath` to point to your python venv `python` executable 
- Goto the vscode extension `cd editors/vscode`
- Install the environment `npm install` 
- Compile the extension `npm run compile`
- Within the debug view of VSCode, select `Server + Client` and press `F5` or click on the green arrow (Start Debugging).
- This is boot a vscode extension host & the python language server under debuggers.
- Open a `.lark` document, it currently just sends some notifications to the client.
