"""
Shell utility commands for PythonParagon.
Provides echo, history, and other shell-related commands.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from typing import List
import time
import os

console = Console()


def echo_command(args: List[str]):
    """Print text to console."""
    if not args:
        console.print("")
        return
    
    text = " ".join(args)
    
    # Check for special formatting flags
    if text.startswith("-n "):
        # No newline at end
        text = text[3:]
        console.print(text, end="")
    elif text.startswith("-e "):
        # Enable interpretation of backslash escapes
        text = text[3:]
        # Simple escape sequence handling
        text = text.replace("\\n", "\n")
        text = text.replace("\\t", "\t")
        text = text.replace("\\\\", "\\")
        console.print(text)
    else:
        console.print(text)


def history_command(args: List[str]):
    """Display command history."""
    from paragon.core.shell import InteractiveShell
    
    # Get history from shell (this is a placeholder - actual implementation would need shell instance)
    console.print("[yellow]Note:[/yellow] History tracking is managed by the shell session")
    console.print("Use arrow keys to navigate through command history during your session")
    
    # If shell history is accessible, we could display it here
    # For now, show example format
    table = Table(title="📜 Command History", show_header=True)
    table.add_column("#", style="cyan", justify="right", width=6)
    table.add_column("Command", style="green")
    table.add_column("Time", style="yellow")
    
    # This would be populated from actual history
    console.print(table)
    console.print("\n[dim]Tip: Use ↑/↓ arrow keys to navigate history[/dim]")


def alias_command(args: List[str]):
    """Create or display command aliases."""
    if not args:
        # Show current aliases
        table = Table(title="⚡ Command Aliases", show_header=True)
        table.add_column("Alias", style="cyan bold")
        table.add_column("Command", style="green")
        
        # These are the built-in aliases from main.py
        aliases = {
            "c": "cpu",
            "m": "memory",
            "p": "processes",
            "d": "disk",
            "e": "env",
            "i": "ip",
            "h": "http-check",
            "s": "search",
            "t": "tree",
            "r": "rename",
            "md": "metadata",
            "curr": "currency",
            "pwd": "password",
            "b64": "base64",
            "ll": "ls",
            "cat": "cat"
        }
        
        for alias, command in sorted(aliases.items()):
            table.add_row(alias, command)
        
        console.print(table)
        console.print("\n[dim]Note: Aliases are defined in the shell configuration[/dim]")
    else:
        console.print("[yellow]Dynamic alias creation is not yet implemented[/yellow]")
        console.print("Aliases are currently defined in the main configuration")


def clear_command(args: List[str]):
    """Clear the terminal screen."""
    console.clear()


def sleep_command(args: List[str]):
    """Pause execution for specified seconds."""
    if not args:
        console.print("[red]✗[/red] Usage: sleep <seconds>")
        return
    
    try:
        seconds = float(args[0])
        
        if seconds < 0:
            console.print("[red]✗[/red] Sleep time must be positive")
            return
        
        from rich.progress import Progress, SpinnerColumn, TextColumn
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Sleeping for {seconds} seconds...", total=None)
            time.sleep(seconds)
        
        console.print(f"[green]✓[/green] Slept for {seconds} seconds")
        
    except ValueError:
        console.print("[red]✗[/red] Invalid number format")
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠[/yellow] Sleep interrupted")


def pwd_command(args: List[str]):
    """Print working directory."""
    cwd = os.getcwd()
    console.print(Panel(
        f"[green]{cwd}[/green]",
        title="📂 Current Working Directory",
        border_style="cyan"
    ))


def cd_command(args: List[str]):
    """Change current directory."""
    if not args:
        # Go to home directory
        home = os.path.expanduser("~")
        try:
            os.chdir(home)
            console.print(f"[green]✓[/green] Changed to home directory: {home}")
        except Exception as e:
            console.print(f"[red]✗[/red] Failed: {e}")
        return
    
    path = args[0]
    
    # Handle special cases
    if path == "-":
        console.print("[yellow]⚠[/yellow] Previous directory tracking not implemented")
        return
    
    # Expand ~ to home directory
    path = os.path.expanduser(path)
    
    try:
        os.chdir(path)
        new_cwd = os.getcwd()
        console.print(f"[green]✓[/green] Changed directory to: {new_cwd}")
    except FileNotFoundError:
        console.print(f"[red]✗[/red] Directory not found: {path}")
    except NotADirectoryError:
        console.print(f"[red]✗[/red] Not a directory: {path}")
    except PermissionError:
        console.print(f"[red]✗[/red] Permission denied: {path}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed: {e}")


def export_command(args: List[str]):
    """Set environment variable."""
    if not args:
        console.print("[red]✗[/red] Usage: export VAR=value")
        return
    
    assignment = " ".join(args)
    
    if "=" not in assignment:
        console.print("[red]✗[/red] Invalid format. Use: export VAR=value")
        return
    
    var_name, var_value = assignment.split("=", 1)
    var_name = var_name.strip()
    var_value = var_value.strip()
    
    # Remove quotes if present
    if var_value.startswith('"') and var_value.endswith('"'):
        var_value = var_value[1:-1]
    elif var_value.startswith("'") and var_value.endswith("'"):
        var_value = var_value[1:-1]
    
    try:
        os.environ[var_name] = var_value
        console.print(f"[green]✓[/green] Set {var_name}={var_value}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to set environment variable: {e}")


def printenv_command(args: List[str]):
    """Print environment variable value."""
    if not args:
        # Print all environment variables (like env command)
        from paragon.commands.system import show_environment
        show_environment([])
        return
    
    var_name = args[0]
    
    if var_name in os.environ:
        value = os.environ[var_name]
        console.print(Panel(
            f"[green]{value}[/green]",
            title=f"🔧 ${var_name}",
            border_style="cyan"
        ))
    else:
        console.print(f"[yellow]Environment variable not set: {var_name}[/yellow]")
