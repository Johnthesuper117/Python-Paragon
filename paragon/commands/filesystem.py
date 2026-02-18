"""
Filesystem commands module for PythonParagon.
Provides file and directory manipulation commands similar to Unix/PowerShell.
"""
import os
import shutil
from pathlib import Path
from typing import List
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
from datetime import datetime
import re

console = Console()


def ls_command(args: List[str]):
    """Enhanced directory listing with detailed information."""
    path = args[0] if args else "."
    target = Path(path)
    
    if not target.exists():
        console.print(f"[red]✗[/red] Path does not exist: {path}")
        return
    
    if target.is_file():
        console.print(f"[yellow]{target.name}[/yellow] (file)")
        return
    
    table = Table(title=f"📁 Directory Listing: {target.resolve()}", show_header=True)
    table.add_column("Type", style="cyan", width=6)
    table.add_column("Name", style="yellow")
    table.add_column("Size", justify="right", style="green")
    table.add_column("Modified", style="blue")
    table.add_column("Permissions", style="magenta")
    
    try:
        items = sorted(target.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        
        for item in items:
            item_type = "DIR" if item.is_dir() else "FILE"
            name = f"📁 {item.name}" if item.is_dir() else f"📄 {item.name}"
            
            if item.is_file():
                size = item.stat().st_size
                size_str = format_size(size)
            else:
                size_str = "-"
            
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            modified = mtime.strftime("%Y-%m-%d %H:%M")
            
            perms = oct(item.stat().st_mode)[-3:]
            
            table.add_row(item_type, name, size_str, modified, perms)
        
        console.print(table)
        
        # Summary
        files = [x for x in items if x.is_file()]
        dirs = [x for x in items if x.is_dir()]
        total_size = sum(f.stat().st_size for f in files)
        
        console.print(f"\n[cyan]Directories:[/cyan] {len(dirs)} [cyan]Files:[/cyan] {len(files)} [cyan]Total Size:[/cyan] {format_size(total_size)}")
        
    except PermissionError:
        console.print(f"[red]✗[/red] Permission denied: {path}")


def cp_command(args: List[str]):
    """Copy files or directories."""
    if len(args) < 2:
        console.print("[red]✗[/red] Usage: cp <source> <destination>")
        return
    
    source = Path(args[0])
    dest = Path(args[1])
    
    if not source.exists():
        console.print(f"[red]✗[/red] Source does not exist: {source}")
        return
    
    try:
        if source.is_file():
            shutil.copy2(source, dest)
            console.print(f"[green]✓[/green] Copied file: {source} → {dest}")
        elif source.is_dir():
            shutil.copytree(source, dest, dirs_exist_ok=True)
            console.print(f"[green]✓[/green] Copied directory: {source} → {dest}")
    except Exception as e:
        console.print(f"[red]✗[/red] Copy failed: {e}")


def mv_command(args: List[str]):
    """Move or rename files/directories."""
    if len(args) < 2:
        console.print("[red]✗[/red] Usage: mv <source> <destination>")
        return
    
    source = Path(args[0])
    dest = Path(args[1])
    
    if not source.exists():
        console.print(f"[red]✗[/red] Source does not exist: {source}")
        return
    
    try:
        shutil.move(str(source), str(dest))
        console.print(f"[green]✓[/green] Moved: {source} → {dest}")
    except Exception as e:
        console.print(f"[red]✗[/red] Move failed: {e}")


def rm_command(args: List[str]):
    """Remove files or directories."""
    if not args:
        console.print("[red]✗[/red] Usage: rm <path> [-r for directories]")
        return
    
    recursive = "-r" in args or "--recursive" in args
    paths = [arg for arg in args if not arg.startswith("-")]
    
    for path_str in paths:
        path = Path(path_str)
        
        if not path.exists():
            console.print(f"[yellow]⚠[/yellow] Path does not exist: {path}")
            continue
        
        try:
            if path.is_file():
                path.unlink()
                console.print(f"[green]✓[/green] Removed file: {path}")
            elif path.is_dir():
                if recursive:
                    shutil.rmtree(path)
                    console.print(f"[green]✓[/green] Removed directory: {path}")
                else:
                    console.print(f"[yellow]⚠[/yellow] Use -r to remove directory: {path}")
        except Exception as e:
            console.print(f"[red]✗[/red] Remove failed: {e}")


def mkdir_command(args: List[str]):
    """Create directories."""
    if not args:
        console.print("[red]✗[/red] Usage: mkdir <directory> [-p for parents]")
        return
    
    parents = "-p" in args or "--parents" in args
    paths = [arg for arg in args if not arg.startswith("-")]
    
    for path_str in paths:
        path = Path(path_str)
        
        try:
            path.mkdir(parents=parents, exist_ok=parents)
            console.print(f"[green]✓[/green] Created directory: {path}")
        except FileExistsError:
            console.print(f"[yellow]⚠[/yellow] Directory already exists: {path}")
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to create directory: {e}")


def touch_command(args: List[str]):
    """Create empty files or update timestamps."""
    if not args:
        console.print("[red]✗[/red] Usage: touch <file> [<file2> ...]")
        return
    
    for path_str in args:
        path = Path(path_str)
        
        try:
            path.touch()
            if path.stat().st_size == 0:
                console.print(f"[green]✓[/green] Created file: {path}")
            else:
                console.print(f"[green]✓[/green] Updated timestamp: {path}")
        except Exception as e:
            console.print(f"[red]✗[/red] Failed: {e}")


def cat_command(args: List[str]):
    """Display file contents with syntax highlighting."""
    if not args:
        console.print("[red]✗[/red] Usage: cat <file>")
        return
    
    path = Path(args[0])
    
    if not path.exists():
        console.print(f"[red]✗[/red] File does not exist: {path}")
        return
    
    if not path.is_file():
        console.print(f"[red]✗[/red] Not a file: {path}")
        return
    
    try:
        content = path.read_text()
        
        # Try to detect file type for syntax highlighting
        ext = path.suffix.lstrip(".")
        if ext in ["py", "js", "java", "cpp", "c", "rs", "go", "rb", "php", "swift"]:
            syntax = Syntax(content, ext, theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"📄 {path.name}", border_style="cyan"))
        else:
            console.print(Panel(content, title=f"📄 {path.name}", border_style="cyan"))
            
    except UnicodeDecodeError:
        console.print(f"[yellow]⚠[/yellow] Binary file: {path}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to read file: {e}")


def head_command(args: List[str]):
    """Display first N lines of a file."""
    if not args:
        console.print("[red]✗[/red] Usage: head <file> [-n lines]")
        return
    
    lines = 10
    filepath = None
    
    for i, arg in enumerate(args):
        if arg == "-n" and i + 1 < len(args):
            try:
                lines = int(args[i + 1])
            except ValueError:
                console.print("[red]✗[/red] Invalid line count")
                return
        elif not arg.startswith("-") and not (i > 0 and args[i - 1] == "-n"):
            filepath = arg
    
    if not filepath:
        console.print("[red]✗[/red] No file specified")
        return
    
    path = Path(filepath)
    
    if not path.exists() or not path.is_file():
        console.print(f"[red]✗[/red] File not found: {filepath}")
        return
    
    try:
        with open(path, "r") as f:
            content_lines = [f.readline() for _ in range(lines)]
        
        console.print(Panel(
            "".join(content_lines),
            title=f"📄 {path.name} (first {lines} lines)",
            border_style="cyan"
        ))
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to read file: {e}")


def tail_command(args: List[str]):
    """Display last N lines of a file."""
    if not args:
        console.print("[red]✗[/red] Usage: tail <file> [-n lines]")
        return
    
    lines = 10
    filepath = None
    
    for i, arg in enumerate(args):
        if arg == "-n" and i + 1 < len(args):
            try:
                lines = int(args[i + 1])
            except ValueError:
                console.print("[red]✗[/red] Invalid line count")
                return
        elif not arg.startswith("-") and not (i > 0 and args[i - 1] == "-n"):
            filepath = arg
    
    if not filepath:
        console.print("[red]✗[/red] No file specified")
        return
    
    path = Path(filepath)
    
    if not path.exists() or not path.is_file():
        console.print(f"[red]✗[/red] File not found: {filepath}")
        return
    
    try:
        with open(path, "r") as f:
            all_lines = f.readlines()
            content_lines = all_lines[-lines:]
        
        console.print(Panel(
            "".join(content_lines),
            title=f"📄 {path.name} (last {lines} lines)",
            border_style="cyan"
        ))
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to read file: {e}")


def grep_command(args: List[str]):
    """Search for patterns in files."""
    if len(args) < 2:
        console.print("[red]✗[/red] Usage: grep <pattern> <file> [-i for case-insensitive]")
        return
    
    pattern = args[0]
    filepath = args[1]
    case_insensitive = "-i" in args or "--ignore-case" in args
    
    path = Path(filepath)
    
    if not path.exists() or not path.is_file():
        console.print(f"[red]✗[/red] File not found: {filepath}")
        return
    
    try:
        flags = re.IGNORECASE if case_insensitive else 0
        regex = re.compile(pattern, flags)
        
        matches = []
        with open(path, "r") as f:
            for line_num, line in enumerate(f, 1):
                if regex.search(line):
                    matches.append((line_num, line.rstrip()))
        
        if matches:
            table = Table(title=f"🔍 Grep Results: '{pattern}' in {path.name}")
            table.add_column("Line", style="cyan", width=8)
            table.add_column("Content", style="yellow")
            
            for line_num, content in matches:
                # Highlight the match
                highlighted = regex.sub(lambda m: f"[red bold]{m.group()}[/red bold]", content)
                table.add_row(str(line_num), highlighted)
            
            console.print(table)
            console.print(f"[green]Found {len(matches)} match(es)[/green]")
        else:
            console.print(f"[yellow]No matches found for pattern: {pattern}[/yellow]")
            
    except re.error:
        console.print(f"[red]✗[/red] Invalid regex pattern: {pattern}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed: {e}")


def sort_command(args: List[str]):
    """Sort file contents."""
    if not args:
        console.print("[red]✗[/red] Usage: sort <file> [-r for reverse] [-n for numeric]")
        return
    
    reverse = "-r" in args or "--reverse" in args
    numeric = "-n" in args or "--numeric" in args
    filepath = [arg for arg in args if not arg.startswith("-")][0]
    
    path = Path(filepath)
    
    if not path.exists() or not path.is_file():
        console.print(f"[red]✗[/red] File not found: {filepath}")
        return
    
    try:
        with open(path, "r") as f:
            lines = f.readlines()
        
        if numeric:
            # Try to sort numerically
            try:
                sorted_lines = sorted(lines, key=lambda x: float(x.strip()), reverse=reverse)
            except ValueError:
                console.print("[yellow]⚠[/yellow] Non-numeric content, falling back to text sort")
                sorted_lines = sorted(lines, reverse=reverse)
        else:
            sorted_lines = sorted(lines, reverse=reverse)
        
        console.print(Panel(
            "".join(sorted_lines),
            title=f"📄 {path.name} (sorted{'  reverse' if reverse else ''})",
            border_style="cyan"
        ))
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed: {e}")


def format_size(size: int) -> str:
    """Format byte size to human-readable string."""
    size_float = float(size)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_float < 1024:
            return f"{size_float:.1f}{unit}"
        size_float /= 1024
    return f"{size_float:.1f}PB"
