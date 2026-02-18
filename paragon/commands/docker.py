"""
Docker commands for PythonParagon.

This module provides commands for Docker container and image management.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import List
import subprocess

console = Console()


def docker_ps(args: List[str]) -> None:
    """List Docker containers."""
    show_all = '--all' in args or '-a' in args
    
    try:
        cmd = ['docker', 'ps']
        if show_all:
            cmd.append('-a')
        cmd.extend(['--format', '{{.ID}}|{{.Image}}|{{.Status}}|{{.Names}}|{{.Ports}}'])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"[red]Error: {result.stderr}[/red]")
            console.print("[yellow]Is Docker running?[/yellow]")
            return
        
        containers = result.stdout.strip().split('\n')
        
        if not containers or containers[0] == '':
            console.print("[yellow]No containers found[/yellow]")
            return
        
        table = Table(title="Docker Containers", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=12)
        table.add_column("Image", style="green", width=25)
        table.add_column("Status", style="yellow", width=20)
        table.add_column("Name", style="blue", width=20)
        table.add_column("Ports", style="magenta")
        
        for container in containers:
            if not container:
                continue
            parts = container.split('|')
            if len(parts) >= 4:
                table.add_row(
                    parts[0],
                    parts[1][:25],
                    parts[2][:20],
                    parts[3][:20],
                    parts[4][:30] if len(parts) > 4 else ""
                )
        
        console.print(table)
        
        if not show_all:
            console.print("\n[dim]Tip: Use --all to show stopped containers[/dim]")
        
    except FileNotFoundError:
        console.print("[red]Docker is not installed or not in PATH[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def docker_images(args: List[str]) -> None:
    """List Docker images."""
    try:
        cmd = ['docker', 'images', '--format', '{{.Repository}}|{{.Tag}}|{{.ID}}|{{.Size}}|{{.CreatedSince}}']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"[red]Error: {result.stderr}[/red]")
            return
        
        images = result.stdout.strip().split('\n')
        
        if not images or images[0] == '':
            console.print("[yellow]No images found[/yellow]")
            return
        
        table = Table(title="Docker Images", show_header=True, header_style="bold magenta")
        table.add_column("Repository", style="cyan", width=30)
        table.add_column("Tag", style="green", width=15)
        table.add_column("ID", style="yellow", width=12)
        table.add_column("Size", style="blue", width=12)
        table.add_column("Created", style="magenta")
        
        for image in images:
            if not image:
                continue
            parts = image.split('|')
            if len(parts) >= 5:
                table.add_row(
                    parts[0][:30],
                    parts[1][:15],
                    parts[2],
                    parts[3],
                    parts[4]
                )
        
        console.print(table)
        
    except FileNotFoundError:
        console.print("[red]Docker is not installed or not in PATH[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def docker_stats(args: List[str]) -> None:
    """Show Docker container resource stats."""
    try:
        cmd = ['docker', 'stats', '--no-stream', '--format', '{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.NetIO}}|{{.BlockIO}}']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"[red]Error: {result.stderr}[/red]")
            return
        
        stats = result.stdout.strip().split('\n')
        
        if not stats or stats[0] == '':
            console.print("[yellow]No running containers found[/yellow]")
            return
        
        table = Table(title="Docker Container Stats", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", width=25)
        table.add_column("CPU %", style="yellow", width=10)
        table.add_column("Memory", style="green", width=20)
        table.add_column("Net I/O", style="blue", width=20)
        table.add_column("Block I/O", style="magenta", width=20)
        
        for stat in stats:
            if not stat:
                continue
            parts = stat.split('|')
            if len(parts) >= 5:
                table.add_row(
                    parts[0][:25],
                    parts[1],
                    parts[2],
                    parts[3],
                    parts[4]
                )
        
        console.print(table)
        console.print("\n[dim]Tip: This is a snapshot. Use 'docker stats' for live monitoring[/dim]")
        
    except FileNotFoundError:
        console.print("[red]Docker is not installed or not in PATH[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
