"""
System monitoring commands for PythonParagon.

This module provides commands for monitoring system resources like CPU, RAM, processes, disk usage, and environment.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from alive_progress import alive_bar
import psutil
import os
from typing import List

console = Console()


def monitor_cpu(args: List[str]) -> None:
    """Monitor CPU usage in real-time."""
    interval = 1
    count = 5
    
    # Parse args
    i = 0
    while i < len(args):
        if args[i] in ['--interval', '-i'] and i + 1 < len(args):
            interval = int(args[i + 1])
            i += 2
        elif args[i] in ['--count', '-c'] and i + 1 < len(args):
            count = int(args[i + 1])
            i += 2
        else:
            i += 1
    
    try:
        table = Table(title="CPU Monitoring", show_header=True, header_style="bold magenta")
        table.add_column("Reading", style="cyan", justify="center")
        table.add_column("CPU Usage (%)", style="green", justify="center")
        table.add_column("Per Core", style="yellow")
        
        with alive_bar(count, title='Monitoring CPU', bar='filling', spinner='dots_waves') as bar:
            for i in range(count):
                cpu_percent = psutil.cpu_percent(interval=interval)
                per_core = psutil.cpu_percent(interval=0, percpu=True)
                core_str = ", ".join([f"{c:.1f}%" for c in per_core])
                
                table.add_row(f"{i + 1}/{count}", f"{cpu_percent:.1f}%", core_str)
                bar()
        
        console.print(table)
        
        # Summary
        cpu_count = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)
        console.print(f"\n[bold]Total CPU Cores:[/bold] {cpu_count} logical, {cpu_count_physical} physical")
        
    except Exception as e:
        console.print(f"[red]Error monitoring CPU: {e}[/red]")


def monitor_memory(args: List[str]) -> None:
    """Display current memory (RAM) usage."""
    try:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        table = Table(title="Memory Usage", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")
        table.add_column("Percentage", style="yellow", justify="right")
        
        table.add_row("Total RAM", f"{mem.total / (1024**3):.2f} GB", "")
        table.add_row("Available RAM", f"{mem.available / (1024**3):.2f} GB", f"{100 - mem.percent:.1f}%")
        table.add_row("Used RAM", f"{mem.used / (1024**3):.2f} GB", f"{mem.percent}%")
        table.add_section()
        table.add_row("Total Swap", f"{swap.total / (1024**3):.2f} GB", "")
        table.add_row("Used Swap", f"{swap.used / (1024**3):.2f} GB", f"{swap.percent}%")
        
        console.print(table)
        
        if mem.percent > 80:
            console.print("\n[red]⚠ Warning: High memory usage detected![/red]")
        elif mem.percent > 60:
            console.print("\n[yellow]⚠ Caution: Moderate memory usage.[/yellow]")
        else:
            console.print("\n[green]✓ Memory usage is healthy.[/green]")
            
    except Exception as e:
        console.print(f"[red]Error monitoring memory: {e}[/red]")


def list_processes(args: List[str]) -> None:
    """List running processes sorted by resource usage."""
    limit = 10
    sort_by = "memory"
    
    # Parse args
    i = 0
    while i < len(args):
        if args[i] in ['--limit', '-l'] and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        elif args[i] in ['--sort-by', '-s'] and i + 1 < len(args):
            sort_by = args[i + 1]
            i += 2
        else:
            i += 1
    
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


def disk_usage(args: List[str]) -> None:
    """Display disk usage information."""
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
        
    except Exception as e:
        console.print(f"[red]Error checking disk usage: {e}[/red]")


def show_environment(args: List[str]) -> None:
    """Show environment variables."""
    filter_str = ""
    if len(args) > 0:
        filter_str = args[0].upper()
    
    try:
        table = Table(title="Environment Variables", show_header=True, header_style="bold magenta")
        table.add_column("Variable", style="cyan")
        table.add_column("Value", style="green")
        
        count = 0
        for key, value in sorted(os.environ.items()):
            if filter_str and filter_str not in key.upper():
                continue
            table.add_row(key, value[:80] + "..." if len(value) > 80 else value)
            count += 1
            if count >= 50:
                break
        
        console.print(table)
        
        if filter_str:
            console.print(f"\n[dim]Showing variables containing '{filter_str}'[/dim]")
        else:
            console.print(f"\n[dim]Showing first 50 variables. Use: env <filter> to search[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error displaying environment: {e}[/red]")


def whoami_command(args: List[str]) -> None:
    """Display current user information."""
    import pwd
    import grp
    
    try:
        user_info = pwd.getpwuid(os.getuid())
        username = user_info.pw_name
        uid = user_info.pw_uid
        gid = user_info.pw_gid
        home = user_info.pw_dir
        shell = user_info.pw_shell
        
        # Get group info
        group_info = grp.getgrgid(gid)
        groupname = group_info.gr_name
        
        # Get all groups
        groups = [grp.getgrgid(g).gr_name for g in os.getgroups()]
        
        table = Table(title="👤 Current User Information", show_header=False)
        table.add_column("Property", style="cyan bold")
        table.add_column("Value", style="green")
        
        table.add_row("Username", username)
        table.add_row("User ID (UID)", str(uid))
        table.add_row("Group ID (GID)", str(gid))
        table.add_row("Primary Group", groupname)
        table.add_row("All Groups", ", ".join(groups))
        table.add_row("Home Directory", home)
        table.add_row("Shell", shell)
        table.add_row("Process ID", str(os.getpid()))
        table.add_row("Parent Process ID", str(os.getppid()))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error getting user info: {e}[/red]")


def hostname_command(args: List[str]) -> None:
    """Display system hostname and network information."""
    import socket
    import platform
    
    try:
        hostname = socket.gethostname()
        fqdn = socket.getfqdn()
        
        # Try to get IP address
        try:
            ip_address = socket.gethostbyname(hostname)
        except:
            ip_address = "Unable to resolve"
        
        # System information
        system = platform.system()
        release = platform.release()
        version = platform.version()
        machine = platform.machine()
        processor = platform.processor()
        
        table = Table(title="🖥️  System & Network Information", show_header=False)
        table.add_column("Property", style="cyan bold")
        table.add_column("Value", style="green")
        
        table.add_row("Hostname", hostname)
        table.add_row("FQDN", fqdn)
        table.add_row("IP Address", ip_address)
        table.add_row("OS", system)
        table.add_row("Release", release)
        table.add_row("Version", version)
        table.add_row("Architecture", machine)
        table.add_row("Processor", processor or "Unknown")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error getting hostname: {e}[/red]")


def uptime_command(args: List[str]) -> None:
    """Display system uptime and load average."""
    from datetime import timedelta
    import time as time_module
    import datetime as datetime_module
    
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = time_module.time() - boot_time
        uptime_delta = timedelta(seconds=int(uptime_seconds))
        
        # Get load average (Unix-like systems)
        try:
            load1, load5, load15 = os.getloadavg()
            load_available = True
        except (AttributeError, OSError):
            load_available = False
        
        # Get user count
        users = len(psutil.users())
        
        # Format uptime
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        table = Table(title="⏱️  System Uptime", show_header=False)
        table.add_column("Metric", style="cyan bold", width=20)
        table.add_column("Value", style="green")
        
        table.add_row("Uptime", f"{days} days, {hours} hours, {minutes} minutes")
        table.add_row("Boot Time", datetime_module.datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S"))
        table.add_row("Current Users", str(users))
        
        if load_available:
            table.add_row("Load Average (1m)", f"{load1:.2f}")
            table.add_row("Load Average (5m)", f"{load5:.2f}")
            table.add_row("Load Average (15m)", f"{load15:.2f}")
        
        # CPU and Memory summary
        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        
        table.add_row("CPU Usage", f"{cpu_percent}%")
        table.add_row("Memory Usage", f"{mem.percent}%")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error getting uptime: {e}[/red]")


def date_command(args: List[str]) -> None:
    """Display current date and time in various formats."""
    from datetime import datetime, timezone
    import time
    
    now = datetime.now()
    utc_now = datetime.now(timezone.utc)
    
    table = Table(title="📅 Date & Time", show_header=False)
    table.add_column("Format", style="cyan bold", width=25)
    table.add_column("Value", style="green")
    
    table.add_row("Local Time", now.strftime("%Y-%m-%d %H:%M:%S"))
    table.add_row("UTC Time", utc_now.strftime("%Y-%m-%d %H:%M:%S UTC"))
    table.add_row("Unix Timestamp", str(int(time.time())))
    table.add_row("ISO 8601", now.isoformat())
    table.add_row("RFC 2822", now.strftime("%a, %d %b %Y %H:%M:%S %z"))
    table.add_row("Day of Week", now.strftime("%A"))
    table.add_row("Day of Year", now.strftime("%j"))
    table.add_row("Week Number", now.strftime("%U"))
    table.add_row("Timezone", time.tzname[time.daylight])
    
    console.print(table)


def which_command(args: List[str]) -> None:
    """Find the location of a command/executable."""
    if not args:
        console.print("[red]✗[/red] Usage: which <command>")
        return
    
    command = args[0]
    
    # Search in PATH
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    found_paths = []
    
    for directory in path_dirs:
        if not directory:
            continue
        
        full_path = os.path.join(directory, command)
        
        # Check with and without common extensions
        for ext in ["", ".exe", ".bat", ".cmd", ".sh"]:
            check_path = full_path + ext
            if os.path.isfile(check_path) and os.access(check_path, os.X_OK):
                found_paths.append(check_path)
    
    if found_paths:
        table = Table(title=f"🔍 Location of '{command}'")
        table.add_column("Path", style="green")
        table.add_column("Size", style="cyan")
        table.add_column("Modified", style="yellow")
        
        for path in found_paths:
            try:
                import datetime as datetime_module
                stat_info = os.stat(path)
                size = stat_info.st_size
                mtime = datetime_module.datetime.fromtimestamp(stat_info.st_mtime)
                
                # Format size
                size_str = f"{size:,} bytes"
                if size > 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.2f} MB"
                elif size > 1024:
                    size_str = f"{size / 1024:.2f} KB"
                
                table.add_row(path, size_str, mtime.strftime("%Y-%m-%d %H:%M"))
            except:
                table.add_row(path, "N/A", "N/A")
        
        console.print(table)
    else:
        console.print(f"[yellow]Command not found in PATH: {command}[/yellow]")


def kill_command(args: List[str]) -> None:
    """Terminate a process by PID."""
    if not args:
        console.print("[red]✗[/red] Usage: kill <pid> [-9 for force]")
        return
    
    force = "-9" in args or "--force" in args
    pid_str = [arg for arg in args if not arg.startswith("-")][0]
    
    try:
        pid = int(pid_str)
        process = psutil.Process(pid)
        
        # Get process info before killing
        name = process.name()
        
        if force:
            process.kill()  # SIGKILL
            console.print(f"[green]✓[/green] Force killed process {pid} ({name})")
        else:
            process.terminate()  # SIGTERM
            console.print(f"[green]✓[/green] Terminated process {pid} ({name})")
        
    except ValueError:
        console.print(f"[red]✗[/red] Invalid PID: {pid_str}")
    except psutil.NoSuchProcess:
        console.print(f"[red]✗[/red] No process with PID: {pid_str}")
    except psutil.AccessDenied:
        console.print(f"[red]✗[/red] Permission denied to kill process {pid_str}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
