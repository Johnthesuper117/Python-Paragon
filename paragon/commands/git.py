"""
Git integration commands for PythonParagon.

This module provides commands for Git repository operations.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from pathlib import Path
from typing import List
import subprocess
import os

console = Console()


def git_status(args: List[str]) -> None:
    """Show git repository status."""
    try:
        # Check if we're in a git repository
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print("[red]Not a git repository[/red]")
            return
        
        # Get current branch
        branch_result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True
        )
        current_branch = branch_result.stdout.strip()
        
        # Get status
        status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True
        )
        
        status_lines = status_result.stdout.strip().split('\n') if status_result.stdout.strip() else []
        
        # Count changes
        modified = [line for line in status_lines if line.startswith(' M')]
        added = [line for line in status_lines if line.startswith('A') or line.startswith('??')]
        deleted = [line for line in status_lines if line.startswith(' D')]
        
        # Display status
        info_text = f"[bold]Branch:[/bold] {current_branch}\n"
        info_text += f"[bold]Modified:[/bold] {len(modified)}\n"
        info_text += f"[bold]Added:[/bold] {len(added)}\n"
        info_text += f"[bold]Deleted:[/bold] {len(deleted)}\n"
        
        console.print(Panel(info_text, title="Git Status", border_style="blue"))
        
        if status_lines and status_lines[0]:
            table = Table(title="Changed Files", show_header=True, header_style="bold magenta")
            table.add_column("Status", style="yellow", width=10)
            table.add_column("File", style="cyan")
            
            for line in status_lines[:20]:
                status = line[:2]
                filename = line[3:]
                
                if status.strip() == 'M':
                    status_display = "[yellow]Modified[/yellow]"
                elif status.strip() == 'A' or status.strip() == '??':
                    status_display = "[green]Added[/green]"
                elif status.strip() == 'D':
                    status_display = "[red]Deleted[/red]"
                else:
                    status_display = status
                
                table.add_row(status_display, filename)
            
            console.print(table)
            
            if len(status_lines) > 20:
                console.print(f"\n[dim]Showing first 20 of {len(status_lines)} changed files[/dim]")
        else:
            console.print("\n[green]✓ Working directory clean[/green]")
        
    except FileNotFoundError:
        console.print("[red]Git is not installed or not in PATH[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def git_log(args: List[str]) -> None:
    """Show commit history."""
    count = 10
    
    # Parse args
    i = 0
    while i < len(args):
        if args[i] in ['--count', '-n'] and i + 1 < len(args):
            count = int(args[i + 1])
            i += 2
        else:
            i += 1
    
    try:
        result = subprocess.run(
            ['git', 'log', f'-{count}', '--pretty=format:%h|%an|%ar|%s'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print("[red]Not a git repository or no commits found[/red]")
            return
        
        commits = result.stdout.strip().split('\n')
        
        table = Table(title=f"Commit History (last {count})", show_header=True, header_style="bold magenta")
        table.add_column("Hash", style="cyan", width=10)
        table.add_column("Author", style="green", width=20)
        table.add_column("When", style="yellow", width=15)
        table.add_column("Message", style="white")
        
        for commit in commits:
            if not commit:
                continue
            parts = commit.split('|')
            if len(parts) == 4:
                table.add_row(parts[0], parts[1][:20], parts[2], parts[3][:50])
        
        console.print(table)
        
    except FileNotFoundError:
        console.print("[red]Git is not installed or not in PATH[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def git_branches(args: List[str]) -> None:
    """List git branches."""
    show_all = '--all' in args or '-a' in args
    
    try:
        cmd = ['git', 'branch', '-v']
        if show_all:
            cmd.append('-a')
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print("[red]Not a git repository[/red]")
            return
        
        branches = result.stdout.strip().split('\n')
        
        table = Table(title="Git Branches", show_header=True, header_style="bold magenta")
        table.add_column("Current", style="yellow", width=8)
        table.add_column("Branch", style="cyan")
        table.add_column("Commit", style="green", width=10)
        table.add_column("Message", style="white")
        
        for branch in branches:
            if not branch.strip():
                continue
            
            is_current = branch.startswith('*')
            branch = branch.lstrip('* ').strip()
            
            parts = branch.split(maxsplit=2)
            if len(parts) >= 2:
                branch_name = parts[0]
                commit_hash = parts[1]
                message = parts[2] if len(parts) > 2 else ""
                
                table.add_row(
                    "✓" if is_current else "",
                    branch_name,
                    commit_hash,
                    message[:40]
                )
        
        console.print(table)
        
    except FileNotFoundError:
        console.print("[red]Git is not installed or not in PATH[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def git_diff(args: List[str]) -> None:
    """Show git diff."""
    file_path = None
    if args:
        file_path = args[0]
    
    try:
        cmd = ['git', 'diff']
        if file_path:
            cmd.append(file_path)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print("[red]Error getting diff[/red]")
            return
        
        diff_output = result.stdout
        
        if not diff_output.strip():
            console.print("[green]No changes to show[/green]")
            return
        
        # Display with syntax highlighting
        syntax = Syntax(diff_output, "diff", theme="monokai", line_numbers=False)
        console.print(Panel(syntax, title="Git Diff", border_style="blue", expand=True))
        
    except FileNotFoundError:
        console.print("[red]Git is not installed or not in PATH[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
