"""
File operations and utilities for PythonParagon.

This module provides commands for file management, metadata extraction, and directory visualization.
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from pathlib import Path
from typing import Optional, List
import os
import shutil
from datetime import datetime

filelab_app = typer.Typer(help="File operations and management utilities")
console = Console()


@filelab_app.command("rename")
def bulk_rename(
    directory: str = typer.Argument(..., help="Directory containing files to rename"),
    pattern: str = typer.Option("", help="Pattern to match in filenames (empty = all files)"),
    prefix: str = typer.Option("", help="Prefix to add"),
    suffix: str = typer.Option("", help="Suffix to add (before extension)"),
    replace_from: str = typer.Option("", help="Text to replace"),
    replace_to: str = typer.Option("", help="Replacement text"),
    dry_run: bool = typer.Option(True, help="Preview changes without applying them")
) -> None:
    """
    Bulk rename files in a directory.
    
    Supports adding prefix/suffix and find-replace operations on filenames.
    """
    try:
        dir_path = Path(directory)
        
        if not dir_path.exists():
            console.print(f"[red]Directory not found: {directory}[/red]")
            raise typer.Exit(code=1)
        
        if not dir_path.is_dir():
            console.print(f"[red]Path is not a directory: {directory}[/red]")
            raise typer.Exit(code=1)
        
        # Get files to rename
        files = [f for f in dir_path.iterdir() if f.is_file()]
        
        if pattern:
            files = [f for f in files if pattern in f.name]
        
        if not files:
            console.print("[yellow]No files found matching criteria[/yellow]")
            return
        
        # Prepare rename operations
        rename_ops = []
        
        for file_path in files:
            old_name = file_path.name
            new_name = old_name
            
            # Apply prefix
            if prefix:
                new_name = prefix + new_name
            
            # Apply suffix (before extension)
            if suffix:
                stem = Path(new_name).stem
                ext = Path(new_name).suffix
                new_name = stem + suffix + ext
            
            # Apply replace
            if replace_from:
                new_name = new_name.replace(replace_from, replace_to)
            
            if old_name != new_name:
                rename_ops.append((file_path, file_path.parent / new_name, old_name, new_name))
        
        if not rename_ops:
            console.print("[yellow]No files would be renamed with current options[/yellow]")
            return
        
        # Display preview
        table = Table(title=f"Bulk Rename Preview ({len(rename_ops)} files)", show_header=True, header_style="bold magenta")
        table.add_column("Old Name", style="red")
        table.add_column("➜", justify="center")
        table.add_column("New Name", style="green")
        
        for _, _, old_name, new_name in rename_ops:
            table.add_row(old_name, "→", new_name)
        
        console.print(table)
        
        if dry_run:
            console.print("\n[yellow]This was a dry run. Use --no-dry-run to apply changes.[/yellow]")
        else:
            # Confirm
            confirm = typer.confirm("\nApply these changes?")
            if confirm:
                success_count = 0
                for old_path, new_path, old_name, new_name in rename_ops:
                    try:
                        old_path.rename(new_path)
                        success_count += 1
                    except Exception as e:
                        console.print(f"[red]Error renaming {old_name}: {e}[/red]")
                
                console.print(f"\n[green]Successfully renamed {success_count}/{len(rename_ops)} files[/green]")
            else:
                console.print("[yellow]Operation cancelled[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error during bulk rename: {e}[/red]")
        raise typer.Exit(code=1)


@filelab_app.command("metadata")
def file_metadata(
    path: str = typer.Argument(..., help="File or directory path")
) -> None:
    """
    Extract and display file metadata.
    
    Shows detailed information about a file or all files in a directory.
    """
    try:
        target_path = Path(path)
        
        if not target_path.exists():
            console.print(f"[red]Path not found: {path}[/red]")
            raise typer.Exit(code=1)
        
        files_to_process = []
        
        if target_path.is_file():
            files_to_process = [target_path]
        elif target_path.is_dir():
            files_to_process = [f for f in target_path.iterdir() if f.is_file()]
        
        if not files_to_process:
            console.print("[yellow]No files found[/yellow]")
            return
        
        table = Table(title="File Metadata", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Size", style="green", justify="right")
        table.add_column("Type", style="yellow")
        table.add_column("Modified", style="blue")
        table.add_column("Permissions", style="magenta")
        
        for file_path in sorted(files_to_process)[:50]:  # Limit to 50 files
            try:
                stat = file_path.stat()
                
                # Format size
                size = stat.st_size
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024**2:
                    size_str = f"{size/1024:.1f} KB"
                elif size < 1024**3:
                    size_str = f"{size/(1024**2):.1f} MB"
                else:
                    size_str = f"{size/(1024**3):.2f} GB"
                
                # Format modified time
                modified = datetime.fromtimestamp(stat.st_mtime)
                modified_str = modified.strftime("%Y-%m-%d %H:%M:%S")
                
                # Get file type
                file_type = file_path.suffix[1:].upper() if file_path.suffix else "No ext"
                
                # Format permissions
                perms = oct(stat.st_mode)[-3:]
                
                table.add_row(
                    file_path.name[:40],
                    size_str,
                    file_type,
                    modified_str,
                    perms
                )
            except Exception as e:
                console.print(f"[yellow]Could not read metadata for {file_path.name}: {e}[/yellow]")
        
        console.print(table)
        
        if len(files_to_process) > 50:
            console.print(f"\n[dim]Showing first 50 of {len(files_to_process)} files[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error extracting metadata: {e}[/red]")
        raise typer.Exit(code=1)


@filelab_app.command("tree")
def directory_tree(
    directory: str = typer.Argument(".", help="Directory to visualize"),
    max_depth: int = typer.Option(3, help="Maximum depth to traverse"),
    show_hidden: bool = typer.Option(False, help="Show hidden files")
) -> None:
    """
    Visualize directory structure as a tree.
    
    Displays a beautiful tree representation of the directory structure.
    """
    try:
        root_path = Path(directory).resolve()
        
        if not root_path.exists():
            console.print(f"[red]Directory not found: {directory}[/red]")
            raise typer.Exit(code=1)
        
        if not root_path.is_dir():
            console.print(f"[red]Path is not a directory: {directory}[/red]")
            raise typer.Exit(code=1)
        
        tree = Tree(
            f"[bold blue]{root_path.name}[/bold blue]",
            guide_style="bold bright_blue"
        )
        
        def add_to_tree(path: Path, tree_node: Tree, current_depth: int = 0) -> None:
            """Recursively add directories and files to tree."""
            if current_depth >= max_depth:
                return
            
            try:
                items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                
                if not show_hidden:
                    items = [item for item in items if not item.name.startswith('.')]
                
                for item in items:
                    if item.is_dir():
                        branch = tree_node.add(f"[bold cyan]📁 {item.name}[/bold cyan]")
                        add_to_tree(item, branch, current_depth + 1)
                    else:
                        # Color code by file type
                        ext = item.suffix.lower()
                        if ext in ['.py', '.js', '.java', '.cpp', '.c']:
                            color = "green"
                            icon = "📄"
                        elif ext in ['.txt', '.md', '.rst']:
                            color = "yellow"
                            icon = "📝"
                        elif ext in ['.json', '.yaml', '.yml', '.xml']:
                            color = "magenta"
                            icon = "📋"
                        elif ext in ['.jpg', '.png', '.gif', '.svg']:
                            color = "blue"
                            icon = "🖼️"
                        else:
                            color = "white"
                            icon = "📄"
                        
                        tree_node.add(f"[{color}]{icon} {item.name}[/{color}]")
            except PermissionError:
                tree_node.add("[red]❌ Permission Denied[/red]")
        
        add_to_tree(root_path, tree)
        console.print(tree)
        
    except Exception as e:
        console.print(f"[red]Error creating directory tree: {e}[/red]")
        raise typer.Exit(code=1)


@filelab_app.command("search")
def search_files(
    directory: str = typer.Argument(".", help="Directory to search"),
    name: str = typer.Option("", help="Filename pattern to search"),
    extension: str = typer.Option("", help="File extension to filter (e.g., .py)"),
    min_size: int = typer.Option(0, help="Minimum file size in bytes"),
    max_size: int = typer.Option(0, help="Maximum file size in bytes (0 = no limit)")
) -> None:
    """
    Search for files based on various criteria.
    
    Finds files matching specified patterns and size constraints.
    """
    try:
        search_path = Path(directory)
        
        if not search_path.exists():
            console.print(f"[red]Directory not found: {directory}[/red]")
            raise typer.Exit(code=1)
        
        console.print(f"[bold]Searching in {search_path.resolve()}...[/bold]\n")
        
        results = []
        
        for file_path in search_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            # Apply filters
            if name and name.lower() not in file_path.name.lower():
                continue
            
            if extension and file_path.suffix.lower() != extension.lower():
                continue
            
            try:
                file_size = file_path.stat().st_size
                
                if min_size and file_size < min_size:
                    continue
                
                if max_size and file_size > max_size:
                    continue
                
                results.append((file_path, file_size))
            except Exception:
                continue
        
        if not results:
            console.print("[yellow]No files found matching criteria[/yellow]")
            return
        
        # Display results
        table = Table(title=f"Search Results ({len(results)} files)", show_header=True, header_style="bold magenta")
        table.add_column("Path", style="cyan")
        table.add_column("Size", style="green", justify="right")
        
        for file_path, size in sorted(results, key=lambda x: x[1], reverse=True)[:100]:
            # Format size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024**2:
                size_str = f"{size/1024:.1f} KB"
            elif size < 1024**3:
                size_str = f"{size/(1024**2):.1f} MB"
            else:
                size_str = f"{size/(1024**3):.2f} GB"
            
            rel_path = file_path.relative_to(search_path)
            table.add_row(str(rel_path), size_str)
        
        console.print(table)
        
        if len(results) > 100:
            console.print(f"\n[dim]Showing first 100 of {len(results)} results[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error searching files: {e}[/red]")
        raise typer.Exit(code=1)
