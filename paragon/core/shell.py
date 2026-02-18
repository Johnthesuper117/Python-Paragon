"""
Interactive shell for PythonParagon.

This module provides the interactive terminal interface for running commands.
"""
import sys
from typing import List, Optional, Dict, Callable
from pathlib import Path
import shlex

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich import box
import questionary
from questionary import Style

from paragon.core.config import config

console = Console()

# Custom style for questionary
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'fg:#f8f8f2 bold'),
    ('answer', 'fg:#50fa7b bold'),
    ('pointer', 'fg:#ff79c6 bold'),
    ('highlighted', 'fg:#ff79c6 bold'),
    ('selected', 'fg:#50fa7b'),
    ('separator', 'fg:#6272a4'),
    ('instruction', 'fg:#8be9fd'),
    ('text', 'fg:#f8f8f2'),
])


class InteractiveShell:
    """Interactive shell for PythonParagon."""
    
    def __init__(self):
        """Initialize the interactive shell."""
        self.console = Console()
        self.running = True
        self.command_history: List[str] = []
        self.commands: Dict[str, Callable] = {}
        self.aliases: Dict[str, str] = {}
        
    def register_command(self, name: str, func: Callable) -> None:
        """Register a command function."""
        self.commands[name] = func
    
    def register_alias(self, alias: str, command: str) -> None:
        """Register a command alias."""
        self.aliases[alias] = command
    
    def display_welcome(self) -> None:
        """Display welcome banner."""
        app_name = config.get("app.name", "PythonParagon")
        app_version = config.get("app.version", "2.0.0")
        
        welcome_text = f"""
[bold cyan]{app_name}[/bold cyan] Interactive Terminal - v{app_version}
        
Welcome to the professional Python terminal application!

[bold]Quick Start:[/bold]
  • Type [cyan]help[/cyan] to see all available commands
  • Type [cyan]menu[/cyan] to use the interactive menu
  • Type [cyan]info[/cyan] to see detailed information
  • Type [cyan]exit[/cyan] or [cyan]quit[/cyan] to leave the shell

[bold]Example Commands:[/bold]
  • [green]cpu[/green] - Monitor CPU usage
  • [green]ip[/green] - Get your public IP
  • [green]git status[/green] - Check git status
  • [green]docker ps[/green] - List Docker containers
  • [green]json-format file.json[/green] - Format JSON file
"""
        
        self.console.print(Panel(
            welcome_text,
            title=f"🚀 {app_name}",
            border_style="bold blue",
            box=box.DOUBLE
        ))
    
    def display_help(self) -> None:
        """Display help information with all available commands."""
        table = Table(
            title="📚 Available Commands",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED
        )
        table.add_column("Command", style="cyan", width=25)
        table.add_column("Category", style="yellow", width=12)
        table.add_column("Description", style="white")
        
        # System commands
        table.add_row("cpu", "System", "Monitor CPU usage in real-time")
        table.add_row("memory / mem", "System", "Display memory (RAM) usage")
        table.add_row("processes / ps", "System", "List running processes")
        table.add_row("disk", "System", "Display disk usage")
        table.add_row("env", "System", "Show environment variables")
        table.add_section()
        
        # Network commands
        table.add_row("ip", "Network", "Get your public IP address")
        table.add_row("http <url>", "Network", "Check HTTP status of URL")
        table.add_row("scan <host>", "Network", "Scan ports on a host")
        table.add_row("ping <host>", "Network", "Check if host is reachable")
        table.add_section()
        
        # File commands
        table.add_row("rename <dir>", "Files", "Bulk rename files")
        table.add_row("metadata <file>", "Files", "Show file metadata")
        table.add_row("tree <path>", "Files", "Display directory tree")
        table.add_row("search <path>", "Files", "Search for files")
        table.add_section()
        
        # Data commands
        table.add_row("json-format <file>", "Data", "Format/validate JSON")
        table.add_row("yaml-format <file>", "Data", "Format/validate YAML")
        table.add_row("csv-stats <file>", "Data", "Show CSV statistics")
        table.add_row("json-query <file> <path>", "Data", "Query JSON with path")
        table.add_section()
        
        # Git commands
        table.add_row("git status", "Git", "Show git status")
        table.add_row("git log", "Git", "Show commit history")
        table.add_row("git branches", "Git", "List branches")
        table.add_row("git diff", "Git", "Show changes")
        table.add_section()
        
        # Docker commands
        table.add_row("docker ps", "Docker", "List containers")
        table.add_row("docker images", "Docker", "List images")
        table.add_row("docker stats", "Docker", "Show container stats")
        table.add_section()
        
        # Text/Log commands
        table.add_row("log-analyze <file>", "Text", "Analyze log files")
        table.add_row("text-stats <file>", "Text", "Text file statistics")
        table.add_row("word-count <file>", "Text", "Count words/lines")
        table.add_section()
        
        # Utility commands
        table.add_row("currency <amt> <from> <to>", "Utils", "Convert currency")
        table.add_row("password / pwd", "Utils", "Generate passwords")
        table.add_row("markdown / md <file>", "Utils", "Render markdown")
        table.add_row("base64 / b64", "Utils", "Encode/decode Base64")
        table.add_row("hash <text>", "Utils", "Generate hash")
        table.add_row("uuid", "Utils", "Generate UUID")
        table.add_section()
        
        # Shell commands
        table.add_row("help", "Shell", "Show this help message")
        table.add_row("menu", "Shell", "Open interactive menu")
        table.add_row("info", "Shell", "Show application info")
        table.add_row("clear", "Shell", "Clear the screen")
        table.add_row("history", "Shell", "Show command history")
        table.add_row("exit / quit", "Shell", "Exit the shell")
        
        self.console.print(table)
        self.console.print("\n[dim]💡 Tip: Most commands support --help flag for detailed options[/dim]")
    
    def display_info(self) -> None:
        """Display detailed application information."""
        app_name = config.get("app.name", "PythonParagon")
        app_version = config.get("app.version", "2.0.0")
        app_author = config.get("app.author", "PythonParagon Team")
        
        info_text = f"""
[bold cyan]{app_name}[/bold cyan] - Version {app_version}
[dim]by {app_author}[/dim]

A professional Python terminal application with powerful integrations.

[bold]Features:[/bold]
  • [cyan]System Monitoring[/cyan] - CPU, RAM, processes, disk
  • [cyan]Network Tools[/cyan] - IP lookup, HTTP checker, port scanner
  • [cyan]File Operations[/cyan] - Management, metadata, tree view
  • [cyan]Data Processing[/cyan] - JSON, YAML, CSV handling
  • [cyan]Git Integration[/cyan] - Status, logs, branches, diffs
  • [cyan]Docker Support[/cyan] - Container and image management
  • [cyan]Text Analysis[/cyan] - Log analysis, word counting
  • [cyan]Utilities[/cyan] - Currency, passwords, hashing, and more

[bold]Command Categories:[/bold]
  🖥️  System  |  🌐 Network  |  📁 Files  |  📊 Data
  🔧 Git  |  🐳 Docker  |  📄 Text  |  🛠️  Utils
"""
        
        self.console.print(Panel(
            info_text,
            title=f"🚀 About {app_name}",
            border_style="bold blue",
            box=box.DOUBLE
        ))
    
    def show_interactive_menu(self) -> Optional[str]:
        """Show interactive menu using questionary."""
        categories = questionary.select(
            "Select a command category:",
            choices=[
                "🖥️  System Commands",
                "🌐 Network Commands",
                "📁 File Commands",
                "📊 Data Processing",
                "🔧 Git Commands",
                "🐳 Docker Commands",
                "📄 Text & Log Analysis",
                "🛠️  Utility Commands",
                "❓ Help & Info",
                "← Back to Command Prompt"
            ],
            style=custom_style
        ).ask()
        
        if not categories or categories == "← Back to Command Prompt":
            return None
        
        # Show commands for selected category
        if "System" in categories:
            choices = ["cpu", "memory", "processes", "disk", "env", "← Back"]
        elif "Network" in categories:
            choices = ["ip", "http-check", "port-scan", "ping", "← Back"]
        elif "File" in categories:
            choices = ["tree", "metadata", "rename", "search", "← Back"]
        elif "Data" in categories:
            choices = ["json-format", "yaml-format", "csv-stats", "json-query", "← Back"]
        elif "Git" in categories:
            choices = ["git status", "git log", "git branches", "git diff", "← Back"]
        elif "Docker" in categories:
            choices = ["docker ps", "docker images", "docker stats", "← Back"]
        elif "Text" in categories:
            choices = ["log-analyze", "text-stats", "word-count", "← Back"]
        elif "Utility" in categories:
            choices = ["password", "uuid", "currency", "hash", "base64", "markdown", "← Back"]
        elif "Help" in categories:
            choices = ["help", "info", "history", "← Back"]
        else:
            return None
        
        command = questionary.select(
            "Select a command:",
            choices=choices,
            style=custom_style
        ).ask()
        
        if not command or command == "← Back":
            return self.show_interactive_menu()
       
        return command
    
    def parse_command(self, input_text: str) -> tuple:
        """
        Parse command input into command name and arguments.
        
        Args:
            input_text: Raw input from user
            
        Returns:
            Tuple of (command_name, arguments_list)
        """
        try:
            parts = shlex.split(input_text)
        except ValueError:
            parts = input_text.split()
        
        if not parts:
            return "", []
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        return cmd, args
    
    def execute_command(self, cmd: str, args: List[str]) -> bool:
        """
        Execute a command with given arguments.
        
        Args:
            cmd: Command name
            args: List of arguments
            
        Returns:
            True if command was executed, False otherwise
        """
        # Check if it's an alias
        if cmd in self.aliases:
            cmd = self.aliases[cmd]
        
        # Handle built-in shell commands
        if cmd in ['exit', 'quit']:
            self.running = False
            self.console.print("[yellow]👋 Goodbye![/yellow]")
            return True
        
        elif cmd == 'help':
            self.display_help()
            return True
        
        elif cmd == 'info':
            self.display_info()
            return True
        
        elif cmd == 'menu':
            menu_cmd = self.show_interactive_menu()
            if menu_cmd:
                return self.execute_command(menu_cmd, [])
            return True
        
        elif cmd == 'clear':
            self.console.clear()
            return True
        
        elif cmd == 'history':
            if not self.command_history:
                self.console.print("[yellow]No command history yet[/yellow]")
            else:
                table = Table(title="Command History", show_header=True, header_style="bold magenta")
                table.add_column("#", style="cyan", width=5)
                table.add_column("Command", style="green")
                
                for i, hist_cmd in enumerate(self.command_history[-20:], 1):
                    table.add_row(str(i), hist_cmd)
                
                self.console.print(table)
            return True
        
        elif cmd == '':
            return True
        
        # Check if command exists in registry
        if cmd in self.commands:
            try:
                self.commands[cmd](args)
                return True
            except Exception as e:
                self.console.print(f"[red]Error executing command: {e}[/red]")
                return True
        else:
            self.console.print(f"[red]Unknown command: {cmd}[/red]")
            self.console.print("[dim]Type 'help' for available commands or 'menu' for interactive menu[/dim]")
            return False
    
    def run(self) -> None:
        """Run the interactive shell."""
        self.display_welcome()
        
        while self.running:
            try:
                user_input = Prompt.ask(
                    "\n[bold cyan]PythonParagon[/bold cyan] [bold yellow]>[/bold yellow]",
                    default=""
                ).strip()
                
                if not user_input:
                    continue
                
                self.command_history.append(user_input)
                
                cmd, args = self.parse_command(user_input)
                self.execute_command(cmd, args)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' or 'quit' to leave the shell[/yellow]")
                continue
            except EOFError:
                self.running = False
                self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Unexpected error: {e}[/red]")
                continue
