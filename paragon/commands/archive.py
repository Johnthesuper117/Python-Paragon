"""
Archive and compression commands for PythonParagon.
Provides zip, unzip, and tar operations.
"""
import zipfile
import tarfile
import os
from pathlib import Path
from typing import List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel

console = Console()


def zip_command(args: List[str]):
    """Create a zip archive."""
    if len(args) < 2:
        console.print("[red]✗[/red] Usage: zip <archive.zip> <file1> [file2 ...]")
        return
    
    archive_name = args[0]
    files_to_zip = args[1:]
    
    if not archive_name.endswith('.zip'):
        archive_name += '.zip'
    
    try:
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Creating archive...", total=len(files_to_zip))
                
                added_files = []
                for item in files_to_zip:
                    path = Path(item)
                    
                    if path.is_file():
                        zipf.write(path, path.name)
                        added_files.append((path.name, path.stat().st_size))
                        progress.update(task, advance=1)
                    elif path.is_dir():
                        # Add directory recursively
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, path.parent)
                                zipf.write(file_path, arcname)
                                added_files.append((arcname, os.path.getsize(file_path)))
                        progress.update(task, advance=1)
                    else:
                        console.print(f"[yellow]⚠[/yellow] Skipping non-existent: {item}")
                        progress.update(task, advance=1)
        
        # Show summary
        archive_size = os.path.getsize(archive_name)
        total_size = sum(size for _, size in added_files)
        compression_ratio = (1 - archive_size / total_size) * 100 if total_size > 0 else 0
        
        table = Table(title=f"📦 Archive Created: {archive_name}")
        table.add_column("Metric", style="cyan bold")
        table.add_column("Value", style="green")
        
        table.add_row("Files Added", str(len(added_files)))
        table.add_row("Original Size", format_size(total_size))
        table.add_row("Archive Size", format_size(archive_size))
        table.add_row("Compression", f"{compression_ratio:.1f}%")
        
        console.print(table)
        console.print(f"[green]✓[/green] Archive created successfully: {archive_name}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create archive: {e}")


def unzip_command(args: List[str]):
    """Extract a zip archive."""
    if not args:
        console.print("[red]✗[/red] Usage: unzip <archive.zip> [destination]")
        return
    
    archive_name = args[0]
    destination = args[1] if len(args) > 1 else "."
    
    archive_path = Path(archive_name)
    
    if not archive_path.exists():
        console.print(f"[red]✗[/red] Archive not found: {archive_name}")
        return
    
    if not zipfile.is_zipfile(archive_path):
        console.print(f"[red]✗[/red] Not a valid zip file: {archive_name}")
        return
    
    try:
        dest_path = Path(destination)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            members = zipf.namelist()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Extracting files...", total=len(members))
                
                extracted_files = []
                for member in members:
                    zipf.extract(member, dest_path)
                    extracted_files.append(member)
                    progress.update(task, advance=1)
        
        # Show summary
        table = Table(title=f"📂 Archive Extracted: {archive_name}")
        table.add_column("Property", style="cyan bold")
        table.add_column("Value", style="green")
        
        table.add_row("Files Extracted", str(len(extracted_files)))
        table.add_row("Destination", str(dest_path.resolve()))
        table.add_row("Archive Size", format_size(archive_path.stat().st_size))
        
        console.print(table)
        console.print(f"[green]✓[/green] Extracted {len(extracted_files)} file(s) to {destination}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to extract archive: {e}")


def tar_command(args: List[str]):
    """Create or extract tar archives."""
    if not args:
        console.print("[red]✗[/red] Usage: tar -c/-x <archive.tar> <files...> [-z for gzip] [-j for bzip2]")
        console.print("  -c: Create archive")
        console.print("  -x: Extract archive")
        console.print("  -z: Use gzip compression")
        console.print("  -j: Use bzip2 compression")
        return
    
    # Parse flags
    create_mode = "-c" in args or "--create" in args
    extract_mode = "-x" in args or "--extract" in args
    use_gzip = "-z" in args or "--gzip" in args
    use_bzip2 = "-j" in args or "--bzip2" in args
    
    if not create_mode and not extract_mode:
        console.print("[red]✗[/red] Specify -c (create) or -x (extract)")
        return
    
    # Get file arguments (non-flag arguments)
    file_args = [arg for arg in args if not arg.startswith("-")]
    
    if not file_args:
        console.print("[red]✗[/red] No archive name specified")
        return
    
    archive_name = file_args[0]
    
    # Determine compression mode
    if use_gzip:
        mode_suffix = "gz"
        mode_write = "w:gz"
        mode_read = "r:gz"
    elif use_bzip2:
        mode_suffix = "bz2"
        mode_write = "w:bz2"
        mode_read = "r:bz2"
    else:
        mode_suffix = ""
        mode_write = "w"
        mode_read = "r"
    
    try:
        if create_mode:
            # Create tar archive
            if len(file_args) < 2:
                console.print("[red]✗[/red] No files specified to archive")
                return
            
            files_to_tar = file_args[1:]
            
            with tarfile.open(archive_name, mode_write) as tar:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    console=console
                ) as progress:
                    task = progress.add_task("[cyan]Creating tar archive...", total=len(files_to_tar))
                    
                    added_files = []
                    total_size = 0
                    
                    for item in files_to_tar:
                        path = Path(item)
                        
                        if path.exists():
                            tar.add(item, arcname=path.name)
                            
                            if path.is_file():
                                size = path.stat().st_size
                                added_files.append(path.name)
                                total_size += size
                            else:
                                # Count files in directory
                                for root, dirs, files in os.walk(path):
                                    for f in files:
                                        fp = os.path.join(root, f)
                                        total_size += os.path.getsize(fp)
                                        added_files.append(os.path.relpath(fp, path.parent))
                            
                            progress.update(task, advance=1)
                        else:
                            console.print(f"[yellow]⚠[/yellow] Skipping non-existent: {item}")
                            progress.update(task, advance=1)
            
            # Show summary
            archive_size = os.path.getsize(archive_name)
            compression_ratio = (1 - archive_size / total_size) * 100 if total_size > 0 else 0
            
            table = Table(title=f"📦 Tar Archive Created: {archive_name}")
            table.add_column("Metric", style="cyan bold")
            table.add_column("Value", style="green")
            
            table.add_row("Files Added", str(len(added_files)))
            table.add_row("Original Size", format_size(total_size))
            table.add_row("Archive Size", format_size(archive_size))
            
            if use_gzip or use_bzip2:
                table.add_row("Compression", f"{compression_ratio:.1f}%")
            
            console.print(table)
            console.print(f"[green]✓[/green] Archive created: {archive_name}")
            
        elif extract_mode:
            # Extract tar archive
            destination = file_args[1] if len(file_args) > 1 else "."
            
            archive_path = Path(archive_name)
            
            if not archive_path.exists():
                console.print(f"[red]✗[/red] Archive not found: {archive_name}")
                return
            
            dest_path = Path(destination)
            dest_path.mkdir(parents=True, exist_ok=True)
            
            with tarfile.open(archive_path, mode_read) as tar:
                members = tar.getmembers()
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    console=console
                ) as progress:
                    task = progress.add_task("[cyan]Extracting tar archive...", total=len(members))
                    
                    for member in members:
                        tar.extract(member, dest_path)
                        progress.update(task, advance=1)
            
            # Show summary
            table = Table(title=f"📂 Tar Archive Extracted: {archive_name}")
            table.add_column("Property", style="cyan bold")
            table.add_column("Value", style="green")
            
            table.add_row("Files Extracted", str(len(members)))
            table.add_row("Destination", str(dest_path.resolve()))
            table.add_row("Archive Size", format_size(archive_path.stat().st_size))
            
            console.print(table)
            console.print(f"[green]✓[/green] Extracted {len(members)} file(s) to {destination}")
            
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
