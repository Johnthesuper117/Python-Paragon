"""
System monitoring commands for PythonParagon.

This module provides commands for monitoring system resources like CPU, RAM, processes, and disk usage.
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import psutil
from typing import Optional
import time

system_app = typer.Typer(help="System monitoring and information commands")
console = Console()


@system_app.command("cpu")
def monitor_cpu(
    interval: int = typer.Option(1, help="Update interval in seconds"),
    count: int = typer.Option(5, help="Number of readings to take")
) -> None:
    """
    Monitor CPU usage in real-time.
    
    Displays CPU usage percentage with beautiful formatting.
    """
    try:
        table = Table(title="CPU Monitoring", show_header=True, header_style="bold magenta")
        table.add_column("Reading", style="cyan", justify="center")
        table.add_column("CPU Usage (%)", style="green", justify="center")
        table.add_column("Per Core", style="yellow")
        
        for i in range(count):
            cpu_percent = psutil.cpu_percent(interval=interval)
            per_core = psutil.cpu_percent(interval=0, percpu=True)
            core_str = ", ".join([f"{c:.1f}%" for c in per_core])
            
            table.add_row(
                f"{i + 1}/{count}",
                f"{cpu_percent:.1f}%",
                core_str
            )
        
        console.print(table)
        
        # Summary
        cpu_count = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)
        console.print(f"\n[bold]Total CPU Cores:[/bold] {cpu_count} logical, {cpu_count_physical} physical")
        
    except Exception as e:
        console.print(f"[red]Error monitoring CPU: {e}[/red]")
        raise typer.Exit(code=1)


@system_app.command("memory")
def monitor_memory() -> None:
    """
    Display current memory (RAM) usage.
    
    Shows detailed information about system memory usage including total, available, and used memory.
    """
    try:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Create memory table
        table = Table(title="Memory Usage", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")
        table.add_column("Percentage", style="yellow", justify="right")
        
        # Virtual Memory
        table.add_row("Total RAM", f"{mem.total / (1024**3):.2f} GB", "")
        table.add_row("Available RAM", f"{mem.available / (1024**3):.2f} GB", f"{100 - mem.percent:.1f}%")
        table.add_row("Used RAM", f"{mem.used / (1024**3):.2f} GB", f"{mem.percent}%")
        table.add_section()
        
        # Swap Memory
        table.add_row("Total Swap", f"{swap.total / (1024**3):.2f} GB", "")
        table.add_row("Used Swap", f"{swap.used / (1024**3):.2f} GB", f"{swap.percent}%")
        
        console.print(table)
        
        # Visual indicator
        if mem.percent > 80:
            console.print("\n[red]⚠ Warning: High memory usage detected![/red]")
        elif mem.percent > 60:
            console.print("\n[yellow]⚠ Caution: Moderate memory usage.[/yellow]")
        else:
            console.print("\n[green]✓ Memory usage is healthy.[/green]")
            
    except Exception as e:
        console.print(f"[red]Error monitoring memory: {e}[/red]")
        raise typer.Exit(code=1)


@system_app.command("processes")
def list_processes(
    limit: int = typer.Option(10, help="Number of processes to display"),
    sort_by: str = typer.Option("memory", help="Sort by: memory, cpu, name")
) -> None:
    """
    List running processes sorted by resource usage.
    
    Shows top processes with their PID, name, CPU%, and memory usage.
    """
    try:
        processes = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Collecting process information...", total=None)
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            progress.update(task, completed=True)
        
        # Sort processes
        if sort_by == "memory":
            processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        elif sort_by == "cpu":
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        else:
            processes.sort(key=lambda x: x.get('name', '').lower())
        
        # Create table
        table = Table(title=f"Top {limit} Processes (sorted by {sort_by})", show_header=True, header_style="bold magenta")
        table.add_column("PID", style="cyan", justify="right")
        table.add_column("Name", style="green")
        table.add_column("CPU %", style="yellow", justify="right")
        table.add_column("Memory %", style="red", justify="right")
        
        for proc in processes[:limit]:
            table.add_row(
                str(proc.get('pid', 'N/A')),
                proc.get('name', 'N/A')[:30],
                f"{proc.get('cpu_percent', 0):.1f}%",
                f"{proc.get('memory_percent', 0):.2f}%"
            )
        
        console.print(table)
        console.print(f"\n[dim]Total processes running: {len(processes)}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error listing processes: {e}[/red]")
        raise typer.Exit(code=1)


@system_app.command("disk")
def disk_usage(path: str = typer.Option("/", help="Path to check disk usage")) -> None:
    """
    Display disk usage information.
    
    Shows disk usage statistics for all mounted partitions or a specific path.
    """
    try:
        partitions = psutil.disk_partitions()
        
        table = Table(title="Disk Usage", show_header=True, header_style="bold magenta")
        table.add_column("Device", style="cyan")
        table.add_column("Mount Point", style="green")
        table.add_column("File System", style="blue")
        table.add_column("Total", style="yellow", justify="right")
        table.add_column("Used", style="red", justify="right")
        table.add_column("Free", style="green", justify="right")
        table.add_column("Usage %", style="magenta", justify="right")
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                table.add_row(
                    partition.device,
                    partition.mountpoint,
                    partition.fstype,
                    f"{usage.total / (1024**3):.1f} GB",
                    f"{usage.used / (1024**3):.1f} GB",
                    f"{usage.free / (1024**3):.1f} GB",
                    f"{usage.percent}%"
                )
            except PermissionError:
                continue
        
        console.print(table)
        
        # Show specific path if provided and different from root
        if path != "/" and path != partitions[0].mountpoint:
            try:
                usage = psutil.disk_usage(path)
                console.print(Panel(
                    f"[bold]Path:[/bold] {path}\n"
                    f"[bold]Total:[/bold] {usage.total / (1024**3):.1f} GB\n"
                    f"[bold]Used:[/bold] {usage.used / (1024**3):.1f} GB\n"
                    f"[bold]Free:[/bold] {usage.free / (1024**3):.1f} GB\n"
                    f"[bold]Usage:[/bold] {usage.percent}%",
                    title="Specific Path Usage",
                    border_style="blue"
                ))
            except Exception as e:
                console.print(f"[yellow]Could not get usage for {path}: {e}[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error checking disk usage: {e}[/red]")
        raise typer.Exit(code=1)
