"""
Network utility commands for PythonParagon.

This module provides commands for network operations like IP lookup, HTTP status checking, and port scanning.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from alive_progress import alive_bar
import requests
import socket
import time
import os
from typing import List
from paragon.core.config import config

console = Console()


def public_ip(args: List[str]) -> None:
    """Get your public IP address."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Fetching public IP...", total=None)
            
            api_url = config.get("api.ip_api", "https://api.ipify.org?format=json")
            timeout = config.get("network.timeout", 10)
            
            response = requests.get(api_url, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            ip_address = data.get('ip', 'Unknown')
        
        console.print(Panel(
            f"[bold green]{ip_address}[/bold green]",
            title="Your Public IP Address",
            border_style="green",
            expand=False
        ))
        
    except Exception as e:
        console.print(f"[red]Error fetching public IP: {e}[/red]")


def http_status_checker(args: List[str]) -> None:
    """Check HTTP status of a URL."""
    if not args:
        console.print("[red]Usage: http <url> [--method GET|POST|HEAD][/red]")
        return
    
    url = args[0]
    method = "GET"
    
    # Parse method
    i = 1
    while i < len(args):
        if args[i] in ['--method', '-m'] and i + 1 < len(args):
            method = args[i + 1].upper()
            i += 2
        else:
            i += 1
    
    try:
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(f"Checking {url}...", total=None)
            
            timeout = config.get("network.timeout", 10)
            
            if method == "GET":
                response = requests.get(url, timeout=timeout, allow_redirects=True)
            elif method == "POST":
                response = requests.post(url, timeout=timeout, allow_redirects=True)
            elif method == "HEAD":
                response = requests.head(url, timeout=timeout, allow_redirects=True)
            else:
                console.print(f"[red]Unsupported HTTP method: {method}[/red]")
                return
        
        if response.status_code < 300:
            status_color = "green"
        elif response.status_code < 400:
            status_color = "yellow"
        else:
            status_color = "red"
        
        result_text = f"[bold]URL:[/bold] {url}\n"
        result_text += f"[bold]Method:[/bold] {method}\n"
        result_text += f"[bold]Status Code:[/bold] [{status_color}]{response.status_code}[/{status_color}]\n"
        result_text += f"[bold]Response Time:[/bold] {response.elapsed.total_seconds():.3f}s\n"
        
        console.print(Panel(result_text, title="HTTP Status Check", border_style=status_color))
        
        if response.headers:
            table = Table(title="Response Headers", show_header=True, header_style="bold magenta")
            table.add_column("Header", style="cyan")
            table.add_column("Value", style="green")
            
            important_headers = ['content-type', 'content-length', 'server', 'date', 'cache-control']
            for header in important_headers:
                if header in response.headers:
                    table.add_row(header.title(), response.headers[header])
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error checking URL: {e}[/red]")


def port_scanner(args: List[str]) -> None:
    """Perform a basic port scan on a host."""
    if not args:
        console.print("[red]Usage: scan <host> [--start-port 1] [--end-port 1024] [--timeout 0.5][/red]")
        return
    
    host = args[0]
    start_port = 1
    end_port = 1024
    timeout = 0.5
    
    # Parse args
    i = 1
    while i < len(args):
        if args[i] in ['--start-port', '-s'] and i + 1 < len(args):
            start_port = int(args[i + 1])
            i += 2
        elif args[i] in ['--end-port', '-e'] and i + 1 < len(args):
            end_port = int(args[i + 1])
            i += 2
        elif args[i] in ['--timeout', '-t'] and i + 1 < len(args):
            timeout = float(args[i + 1])
            i += 2
        else:
            i += 1
    
    try:
        if start_port < 1 or end_port > 65535 or start_port > end_port:
            console.print("[red]Invalid port range. Ports must be between 1-65535 and start <= end[/red]")
            return
        
        if end_port - start_port > 1000:
            console.print("[yellow]Warning: Scanning more than 1000 ports. This may take a while...[/yellow]")
        
        console.print(f"[bold]Scanning {host} from port {start_port} to {end_port}...[/bold]\n")
        
        open_ports = []
        total_ports = end_port - start_port + 1
        
        with alive_bar(total_ports, title='Scanning ports', bar='smooth', spinner='dots_waves') as bar:
            for port in range(start_port, end_port + 1):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                
                try:
                    result = sock.connect_ex((host, port))
                    if result == 0:
                        open_ports.append(port)
                        try:
                            service = socket.getservbyport(port)
                        except:
                            service = "unknown"
                        console.print(f"[green]✓ Port {port} is OPEN ({service})[/green]")
                except socket.gaierror:
                    console.print(f"[red]Could not resolve hostname: {host}[/red]")
                    return
                except socket.error:
                    pass
                finally:
                    sock.close()
                
                bar()
        
        if open_ports:
            console.print(f"\n[bold green]Found {len(open_ports)} open port(s):[/bold green]")
            console.print(f"[green]{', '.join(map(str, open_ports))}[/green]")
        else:
            console.print(f"\n[yellow]No open ports found in range {start_port}-{end_port}[/yellow]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Scan interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error during port scan: {e}[/red]")


def ping_host(args: List[str]) -> None:
    """Check if a host is reachable."""
    if not args:
        console.print("[red]Usage: ping <host> [--count 4][/red]")
        return
    
    host = args[0]
    count = 4
    
    # Parse args
    i = 1
    while i < len(args):
        if args[i] in ['--count', '-c'] and i + 1 < len(args):
            count = int(args[i + 1])
            i += 2
        else:
            i += 1
    
    try:
        console.print(f"[bold]Pinging {host}...[/bold]\n")
        
        try:
            ip_address = socket.gethostbyname(host)
            console.print(f"[green]Resolved {host} to {ip_address}[/green]\n")
        except socket.gaierror:
            console.print(f"[red]Could not resolve hostname: {host}[/red]")
            return
        
        successful = 0
        table = Table(title=f"Ping Results for {host}", show_header=True, header_style="bold magenta")
        table.add_column("Attempt", style="cyan", justify="center")
        table.add_column("Result", style="green")
        
        for i in range(count):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            
            try:
                start_time = time.time()
                result = sock.connect_ex((ip_address, 80))
                end_time = time.time()
                
                if result == 0:
                    successful += 1
                    response_time = (end_time - start_time) * 1000
                    table.add_row(f"{i + 1}/{count}", f"[green]✓ Reachable ({response_time:.2f}ms)[/green]")
                else:
                    table.add_row(f"{i + 1}/{count}", "[yellow]✗ No response[/yellow]")
            except Exception as e:
                table.add_row(f"{i + 1}/{count}", f"[red]✗ Error: {e}[/red]")
            finally:
                sock.close()
        
        console.print(table)
        console.print(f"\n[bold]Success Rate:[/bold] {successful}/{count} ({successful/count*100:.1f}%)")
        
    except Exception as e:
        console.print(f"[red]Error pinging host: {e}[/red]")


def wget_command(args: List[str]) -> None:
    """Download files from URLs."""
    if not args:
        console.print("[red]✗[/red] Usage: wget <url> [output_filename]")
        return
    
    url = args[0]
    output_file = args[1] if len(args) > 1 else None
    
    # If no output filename specified, extract from URL
    if not output_file:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        output_file = os.path.basename(parsed.path) or "downloaded_file"
    
    try:
        console.print(f"[cyan]Downloading:[/cyan] {url}")
        console.print(f"[cyan]Saving to:[/cyan] {output_file}\n")
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Get file size if available
        total_size = int(response.headers.get('content-length', 0))
        
        from rich.progress import Progress, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, BarColumn
        
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Downloading", total=total_size)
            
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
        
        # Show summary
        file_size = os.path.getsize(output_file)
        
        table = Table(title="📥 Download Complete")
        table.add_column("Property", style="cyan bold")
        table.add_column("Value", style="green")
        
        table.add_row("URL", url)
        table.add_row("Saved As", output_file)
        table.add_row("File Size", format_size(file_size))
        table.add_row("Status", "[green]✓ Success[/green]")
        
        console.print(table)
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]✗[/red] Download failed: {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")


def format_size(size: int) -> str:
    """Format byte size to human-readable string."""
    size_float = float(size)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_float < 1024:
            return f"{size_float:.1f}{unit}"
        size_float /= 1024
    return f"{size_float:.1f}PB"
