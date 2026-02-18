# PythonParagon 🚀

A sophisticated Python CLI application that demonstrates the peak of Python's terminal capabilities by integrating multiple powerful libraries into a single, cohesive interface.

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

PythonParagon showcases professional CLI development with:

- 🎨 **Beautiful Terminal UI** - Rich formatting with tables, progress bars, panels, and syntax highlighting
- 🏗️ **Modular Architecture** - Clean command structure using Typer subcommands
- 📊 **System Monitoring** - CPU, RAM, process, and disk usage monitoring
- 🌐 **Network Utilities** - IP lookup, HTTP status checking, and port scanning
- 📁 **File Operations** - Bulk renaming, metadata extraction, and directory visualization
- 🛠️ **Utilities** - Currency conversion, password generation, markdown rendering, and more
- 🔒 **Type Safety** - Full type hinting throughout the codebase
- 📝 **Documentation** - Comprehensive docstrings for every command
- ⚙️ **Configuration** - Centralized YAML-based configuration management
- 🎯 **Error Handling** - Robust error handling with helpful messages

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Johnthesuper117/Python-Paragon.git
cd Python-Paragon
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Command Categories

### 🖥️ System Commands

Monitor and analyze system resources:

- `system cpu` - Real-time CPU usage monitoring with per-core statistics
- `system memory` - Detailed RAM and swap memory usage
- `system processes` - List top processes sorted by CPU or memory
- `system disk` - Display disk usage for all partitions

**Examples:**
```bash
python main.py system cpu --count 10 --interval 1
python main.py system memory
python main.py system processes --limit 20 --sort-by cpu
python main.py system disk
```

### 🌐 Network Commands

Network diagnostics and utilities:

- `network ip` - Get your public IP address
- `network http-check` - Check HTTP status and headers of any URL
- `network port-scan` - Scan ports on a host (basic scanner)
- `network ping` - Check host connectivity

**Examples:**
```bash
python main.py network ip
python main.py network http-check https://github.com
python main.py network port-scan localhost --start-port 80 --end-port 443
python main.py network ping google.com --count 5
```

### 📁 File Lab Commands

File management and operations:

- `filelab rename` - Bulk rename files with patterns
- `filelab metadata` - Extract and display file metadata
- `filelab tree` - Visualize directory structure as a tree
- `filelab search` - Search files by name, extension, or size

**Examples:**
```bash
python main.py filelab tree . --max-depth 3
python main.py filelab metadata /path/to/directory
python main.py filelab rename ./photos --prefix "vacation_" --dry-run
python main.py filelab search . --extension .py --min-size 1000
```

### 🛠️ Utility Commands

General-purpose utilities:

- `utils currency` - Convert between currencies with live rates
- `utils password` - Generate secure random passwords
- `utils markdown` - Render markdown files beautifully
- `utils base64` - Encode/decode Base64 strings
- `utils hash` - Generate hashes (MD5, SHA256, etc.)
- `utils uuid` - Generate UUIDs (v1 or v4)

**Examples:**
```bash
python main.py utils currency 100 USD EUR
python main.py utils password --length 20 --count 5
python main.py utils markdown README.md
python main.py utils base64 "Hello World"
python main.py utils hash "secret" --algorithm sha256
python main.py utils uuid --count 3 --version 4
```

## Project Structure

```
Python-Paragon/
├── main.py                  # Main application entry point
├── config.py                # Centralized configuration manager
├── config.yaml              # Configuration file
├── commands_system.py       # System monitoring commands
├── commands_network.py      # Network utility commands
├── commands_filelab.py      # File operation commands
├── commands_utils.py        # General utility commands
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── LICENSE                 # MIT License
```

## Configuration

The application uses a `config.yaml` file for centralized configuration. You can customize:

- API endpoints for external services
- Network timeouts and retry settings
- File operation limits
- Security settings for password generation

Example configuration:
```yaml
api:
  currency_api: "https://api.exchangerate-api.com/v4/latest/"
  ip_api: "https://api.ipify.org?format=json"

network:
  timeout: 10
  max_retries: 3

security:
  password_length: 16
  include_special_chars: true
```

## Development

### Adding New Commands

The application is designed for easy extensibility. To add new commands:

1. Create or edit a command module (e.g., `commands_category.py`)
2. Import and register the Typer app in `main.py`
3. Add comprehensive docstrings and type hints
4. Include error handling and Rich formatting

Example:
```python
# In commands_category.py
import typer
from rich.console import Console

category_app = typer.Typer(help="Category description")
console = Console()

@category_app.command("mycommand")
def my_command(arg: str = typer.Argument(..., help="Description")) -> None:
    """Command description."""
    try:
        # Your command logic here
        console.print(f"[green]Success![/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)
```

### Type Hints

All functions include proper type hints for better IDE support and code quality:

```python
def function_name(
    param1: str,
    param2: int = 10,
    param3: Optional[List[str]] = None
) -> None:
    """Function docstring."""
    pass
```

## Technologies Used

- **[Typer](https://typer.tiangolo.com/)** - Modern CLI framework with automatic help generation
- **[Rich](https://rich.readthedocs.io/)** - Beautiful terminal formatting and progress bars
- **[psutil](https://psutil.readthedocs.io/)** - Cross-platform system and process utilities
- **[requests](https://requests.readthedocs.io/)** - HTTP library for API interactions
- **[pandas](https://pandas.pydata.org/)** - Data manipulation and analysis
- **[PyYAML](https://pyyaml.org/)** - YAML parser for configuration management
- **[pathlib](https://docs.python.org/3/library/pathlib.html)** - Object-oriented filesystem paths

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code:
- Includes type hints
- Has comprehensive docstrings
- Follows the existing code style
- Includes error handling
- Uses Rich for output formatting

## Roadmap

Future enhancements planned:

- [ ] Data analysis commands (CSV processing, statistics)
- [ ] Git integration commands
- [ ] Docker container management
- [ ] Cloud service integrations (AWS, Azure, GCP)
- [ ] Database query tools
- [ ] Web scraping utilities
- [ ] Image processing commands
- [ ] JSON/YAML processing tools
- [ ] Log file analysis
- [ ] Performance profiling tools

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**PythonParagon Team**

## Acknowledgments

- Built with love for the Python community
- Inspired by modern CLI tools like `httpie`, `exa`, and `bat`
- Thanks to all the amazing open-source library maintainers

---

⭐ If you find this project useful, please consider giving it a star!

**Happy CLI-ing!** 🎉