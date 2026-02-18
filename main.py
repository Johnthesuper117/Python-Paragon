#!/usr/bin/env python3
"""
PythonParagon - A Sophisticated Python CLI Application

This application demonstrates the peak of Python's terminal capabilities by integrating
multiple powerful libraries into a single, cohesive interface.

Author: PythonParagon Team
Version: 1.0.0
"""
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional

from commands_system import system_app
from commands_network import network_app
from commands_filelab import filelab_app
from commands_utils import utils_app
from config import config

# Initialize the main Typer app
app = typer.Typer(
    name="pythonparagon",
    help="🚀 PythonParagon - A sophisticated Python CLI showcasing terminal capabilities",
    add_completion=True,
    rich_markup_mode="rich"
)

# Initialize Rich console
console = Console()

# Register command groups as subcommands
app.add_typer(system_app, name="system", help="🖥️  System monitoring and information")
app.add_typer(network_app, name="network", help="🌐 Network utilities and diagnostics")
app.add_typer(filelab_app, name="filelab", help="📁 File operations and management")
app.add_typer(utils_app, name="utils", help="🛠️  General utility commands")


@app.command()
def info() -> None:
    """
    Display information about PythonParagon.
    
    Shows application details, version, and available command categories.
    """
    app_name = config.get("app.name", "PythonParagon")
    app_version = config.get("app.version", "1.0.0")
    app_author = config.get("app.author", "PythonParagon Team")
    
    info_text = f"""
[bold cyan]{app_name}[/bold cyan] - Version {app_version}
[dim]by {app_author}[/dim]

A sophisticated Python CLI application demonstrating the peak of Python's 
terminal capabilities through beautiful interfaces and powerful integrations.

[bold]Command Categories:[/bold]
  🖥️  [cyan]system[/cyan]   - System monitoring (CPU, RAM, processes, disk)
  🌐 [cyan]network[/cyan]  - Network utilities (IP lookup, HTTP checker, port scanner)
  📁 [cyan]filelab[/cyan]  - File operations (bulk rename, metadata, tree view)
  🛠️  [cyan]utils[/cyan]    - Utilities (currency, password gen, markdown renderer)

[bold]Usage:[/bold]
  python main.py [CATEGORY] [COMMAND] [OPTIONS]

[bold]Examples:[/bold]
  python main.py system cpu
  python main.py network ip
  python main.py filelab tree .
  python main.py utils password --length 20

[bold]Get Help:[/bold]
  python main.py --help
  python main.py [CATEGORY] --help
  python main.py [CATEGORY] [COMMAND] --help
"""
    
    console.print(Panel(
        info_text,
        title=f"🚀 {app_name}",
        border_style="bold blue",
        expand=False
    ))


@app.command()
def list_commands() -> None:
    """
    List all available commands organized by category.
    
    Provides a comprehensive overview of all commands in the application.
    """
    commands_by_category = {
        "System": [
            ("cpu", "Monitor CPU usage in real-time"),
            ("memory", "Display current memory (RAM) usage"),
            ("processes", "List running processes sorted by resource usage"),
            ("disk", "Display disk usage information")
        ],
        "Network": [
            ("ip", "Get your public IP address"),
            ("http-check", "Check HTTP status of a URL"),
            ("port-scan", "Perform a basic port scan on a host"),
            ("ping", "Check if a host is reachable")
        ],
        "File Lab": [
            ("rename", "Bulk rename files in a directory"),
            ("metadata", "Extract and display file metadata"),
            ("tree", "Visualize directory structure as a tree"),
            ("search", "Search for files based on various criteria")
        ],
        "Utils": [
            ("currency", "Convert currency using live exchange rates"),
            ("password", "Generate secure random passwords"),
            ("markdown", "Render markdown with beautiful formatting"),
            ("base64", "Encode or decode Base64 strings"),
            ("hash", "Generate hash of text using various algorithms"),
            ("uuid", "Generate UUIDs (Universally Unique Identifiers)")
        ]
    }
    
    table = Table(
        title="🎯 Available Commands",
        show_header=True,
        header_style="bold magenta",
        title_style="bold cyan"
    )
    table.add_column("Category", style="cyan", width=15)
    table.add_column("Command", style="green", width=15)
    table.add_column("Description", style="white")
    
    for category, commands in commands_by_category.items():
        for i, (cmd, desc) in enumerate(commands):
            if i == 0:
                table.add_row(f"[bold]{category}[/bold]", cmd, desc)
            else:
                table.add_row("", cmd, desc)
        table.add_section()
    
    console.print(table)
    console.print(f"\n[bold]Total Commands:[/bold] {sum(len(cmds) for cmds in commands_by_category.values())}")
    console.print("[dim]Run 'python main.py [CATEGORY] [COMMAND] --help' for detailed usage[/dim]")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit")
) -> None:
    """
    PythonParagon - Main application entry point.
    
    Run without commands to see the welcome screen, or use subcommands for specific operations.
    """
    if version:
        app_name = config.get("app.name", "PythonParagon")
        app_version = config.get("app.version", "1.0.0")
        console.print(f"[bold]{app_name}[/bold] version [cyan]{app_version}[/cyan]")
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        # Show welcome screen
        welcome_art = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗    ║
║   ██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║    ║
║   ██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║    ║
║   ██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║    ║
║   ██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║    ║
║   ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ║
║                                                               ║
║              ██████╗  █████╗ ██████╗  █████╗  ██████╗  ██████╗ ███╗   ██╗
║              ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔════╝ ██╔═══██╗████╗  ██║
║              ██████╔╝███████║██████╔╝███████║██║  ███╗██║   ██║██╔██╗ ██║
║              ██╔═══╝ ██╔══██║██╔══██╗██╔══██║██║   ██║██║   ██║██║╚██╗██║
║              ██║     ██║  ██║██║  ██║██║  ██║╚██████╔╝╚██████╔╝██║ ╚████║
║              ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
        console.print(f"[bold cyan]{welcome_art}[/bold cyan]")
        
        console.print("\n[bold]Welcome to PythonParagon![/bold] 🚀\n")
        console.print("A sophisticated CLI showcasing Python's terminal capabilities.\n")
        
        console.print("[bold cyan]Quick Start:[/bold cyan]")
        console.print("  • Run [green]python main.py info[/green] for app information")
        console.print("  • Run [green]python main.py list-commands[/green] to see all commands")
        console.print("  • Run [green]python main.py --help[/green] for detailed help\n")
        
        console.print("[bold cyan]Command Categories:[/bold cyan]")
        console.print("  🖥️  [cyan]system[/cyan]   - Monitor CPU, RAM, processes, disk")
        console.print("  🌐 [cyan]network[/cyan]  - IP lookup, HTTP checks, port scanning")
        console.print("  📁 [cyan]filelab[/cyan]  - File operations and management")
        console.print("  🛠️  [cyan]utils[/cyan]    - Passwords, currency, markdown, and more\n")
        
        console.print("[dim]Tip: Add --help after any command for detailed usage[/dim]\n")


if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(code=0)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)
