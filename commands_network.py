"""
Network utility commands for PythonParagon.

This module provides commands for network operations like IP lookup, HTTP status checking, and port scanning.
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import requests
import socket
from typing import Optional, List
from config import config

network_app = typer.Typer(help="Network utilities and diagnostics")
console = Console()


@network_app.command("ip")
def public_ip() -> None:
    """
    Get your public IP address.
    
    Retrieves and displays your public IP address using an external API.
    """
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
        
    except requests.RequestException as e:
        console.print(f"[red]Error fetching public IP: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@network_app.command("http-check")
def http_status_checker(
    url: str = typer.Argument(..., help="URL to check"),
    method: str = typer.Option("GET", help="HTTP method (GET, POST, HEAD)")
) -> None:
    """
    Check HTTP status of a URL.
    
    Sends an HTTP request to the specified URL and displays the response status and headers.
    """
    try:
        # Ensure URL has scheme
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
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=timeout, allow_redirects=True)
            elif method.upper() == "POST":
                response = requests.post(url, timeout=timeout, allow_redirects=True)
            elif method.upper() == "HEAD":
                response = requests.head(url, timeout=timeout, allow_redirects=True)
            else:
                console.print(f"[red]Unsupported HTTP method: {method}[/red]")
                raise typer.Exit(code=1)
        
        # Determine status color
        if response.status_code < 300:
            status_color = "green"
        elif response.status_code < 400:
            status_color = "yellow"
        else:
            status_color = "red"
        
        # Create results panel
        result_text = f"[bold]URL:[/bold] {url}\n"
        result_text += f"[bold]Method:[/bold] {method.upper()}\n"
        result_text += f"[bold]Status Code:[/bold] [{status_color}]{response.status_code}[/{status_color}]\n"
        result_text += f"[bold]Response Time:[/bold] {response.elapsed.total_seconds():.3f}s\n"
        
        console.print(Panel(result_text, title="HTTP Status Check", border_style=status_color))
        
        # Display key headers
        if response.headers:
            table = Table(title="Response Headers", show_header=True, header_style="bold magenta")
            table.add_column("Header", style="cyan")
            table.add_column("Value", style="green")
            
            important_headers = ['content-type', 'content-length', 'server', 'date', 'cache-control']
            for header in important_headers:
                if header in response.headers:
                    table.add_row(header.title(), response.headers[header])
            
            console.print(table)
        
    except requests.Timeout:
        console.print(f"[red]Request timed out after {timeout} seconds[/red]")
        raise typer.Exit(code=1)
    except requests.RequestException as e:
        console.print(f"[red]Error checking URL: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@network_app.command("port-scan")
def port_scanner(
    host: str = typer.Argument(..., help="Host to scan (IP or hostname)"),
    start_port: int = typer.Option(1, help="Starting port number"),
    end_port: int = typer.Option(1024, help="Ending port number"),
    timeout: float = typer.Option(0.5, help="Connection timeout in seconds")
) -> None:
    """
    Perform a basic port scan on a host.
    
    Scans a range of ports on the specified host to check which ports are open.
    Note: This is a basic scanner for educational purposes.
    """
    try:
        if start_port < 1 or end_port > 65535 or start_port > end_port:
            console.print("[red]Invalid port range. Ports must be between 1-65535 and start <= end[/red]")
            raise typer.Exit(code=1)
        
        # Limit scan range for safety
        if end_port - start_port > 1000:
            console.print("[yellow]Warning: Scanning more than 1000 ports. This may take a while...[/yellow]")
        
        console.print(f"[bold]Scanning {host} from port {start_port} to {end_port}...[/bold]\n")
        
        open_ports = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Scanning ports...", total=end_port - start_port + 1)
            
            for port in range(start_port, end_port + 1):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                
                try:
                    result = sock.connect_ex((host, port))
                    if result == 0:
                        open_ports.append(port)
                        # Try to get service name
                        try:
                            service = socket.getservbyport(port)
                        except:
                            service = "unknown"
                        console.print(f"[green]✓ Port {port} is OPEN ({service})[/green]")
                except socket.gaierror:
                    console.print(f"[red]Could not resolve hostname: {host}[/red]")
                    raise typer.Exit(code=1)
                except socket.error:
                    pass
                finally:
                    sock.close()
                
                progress.update(task, advance=1)
        
        # Summary
        if open_ports:
            console.print(f"\n[bold green]Found {len(open_ports)} open port(s):[/bold green]")
            console.print(f"[green]{', '.join(map(str, open_ports))}[/green]")
        else:
            console.print(f"\n[yellow]No open ports found in range {start_port}-{end_port}[/yellow]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Scan interrupted by user[/yellow]")
        raise typer.Exit(code=0)
    except Exception as e:
        console.print(f"[red]Error during port scan: {e}[/red]")
        raise typer.Exit(code=1)


@network_app.command("ping")
def ping_host(
    host: str = typer.Argument(..., help="Host to ping"),
    count: int = typer.Option(4, help="Number of ping attempts")
) -> None:
    """
    Check if a host is reachable.
    
    Attempts to resolve and connect to a host to check connectivity.
    """
    try:
        console.print(f"[bold]Pinging {host}...[/bold]\n")
        
        # Resolve hostname
        try:
            ip_address = socket.gethostbyname(host)
            console.print(f"[green]Resolved {host} to {ip_address}[/green]\n")
        except socket.gaierror:
            console.print(f"[red]Could not resolve hostname: {host}[/red]")
            raise typer.Exit(code=1)
        
        # Attempt connections
        successful = 0
        table = Table(title=f"Ping Results for {host}", show_header=True, header_style="bold magenta")
        table.add_column("Attempt", style="cyan", justify="center")
        table.add_column("Result", style="green")
        
        for i in range(count):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            
            try:
                start_time = socket.time.time()
                result = sock.connect_ex((ip_address, 80))  # Try port 80
                end_time = socket.time.time()
                
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
        raise typer.Exit(code=1)
