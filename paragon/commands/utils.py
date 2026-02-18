"""
Utility commands for PythonParagon.

This module provides miscellaneous utilities like currency conversion, password generation, and markdown rendering.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from alive_progress import alive_bar
import requests
import secrets
import string
from pathlib import Path
from typing import List
from paragon.core.config import config

console = Console()


def currency_converter(args: List[str]) -> None:
    """Convert currency using live exchange rates."""
    if len(args) < 3:
        console.print("[red]Usage: currency <amount> <from_currency> <to_currency>[/red]")
        return
    
    try:
        amount = float(args[0])
        from_currency = args[1].upper()
        to_currency = args[2].upper()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Fetching exchange rates...", total=None)
            
            api_url = config.get("api.currency_api", "https://api.exchangerate-api.com/v4/latest/")
            timeout = config.get("network.timeout", 10)
            
            response = requests.get(f"{api_url}{from_currency}", timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
        
        if 'rates' not in data or to_currency not in data['rates']:
            console.print(f"[red]Currency code not found: {to_currency}[/red]")
            return
        
        exchange_rate = data['rates'][to_currency]
        converted_amount = amount * exchange_rate
        
        result_text = f"[bold]{amount:,.2f} {from_currency}[/bold]\n"
        result_text += f"[dim]=[/dim]\n"
        result_text += f"[bold green]{converted_amount:,.2f} {to_currency}[/bold green]\n\n"
        result_text += f"[dim]Exchange Rate: 1 {from_currency} = {exchange_rate:.4f} {to_currency}[/dim]"
        
        console.print(Panel(
            result_text,
            title="Currency Conversion",
            border_style="green",
            expand=False
        ))
        
        if 'date' in data:
            console.print(f"[dim]Rate as of: {data['date']}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def password_generator(args: List[str]) -> None:
    """Generate secure random passwords."""
    length = 16
    count = 1
    no_special = False
    no_numbers = False
    no_uppercase = False
    
    # Parse args
    i = 0
    while i < len(args):
        if args[i] in ['--length', '-l'] and i + 1 < len(args):
            length = int(args[i + 1])
            i += 2
        elif args[i] in ['--count', '-c'] and i + 1 < len(args):
            count = int(args[i + 1])
            i += 2
        elif args[i] == '--no-special':
            no_special = True
            i += 1
        elif args[i] == '--no-numbers':
            no_numbers = True
            i += 1
        elif args[i] == '--no-uppercase':
            no_uppercase = True
            i += 1
        else:
            i += 1
    
    try:
        if length < 4:
            console.print("[red]Password length must be at least 4 characters[/red]")
            return
        
        if count < 1 or count > 100:
            console.print("[red]Count must be between 1 and 100[/red]")
            return
        
        characters = string.ascii_lowercase
        
        if not no_uppercase:
            characters += string.ascii_uppercase
        
        if not no_numbers:
            characters += string.digits
        
        if not no_special:
            characters += string.punctuation
        
        if len(characters) < 4:
            console.print("[red]Character set too small. Enable at least one character type.[/red]")
            return
        
        passwords = []
        
        if count > 5:
            with alive_bar(count, title='Generating passwords', bar='classic', spinner='dots') as bar:
                for _ in range(count):
                    password = ''.join(secrets.choice(characters) for _ in range(length))
                    passwords.append(password)
                    bar()
        else:
            for _ in range(count):
                password = ''.join(secrets.choice(characters) for _ in range(length))
                passwords.append(password)
        
        table = Table(title=f"Generated Password(s)", show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", justify="center")
        table.add_column("Password", style="green")
        table.add_column("Strength", style="yellow")
        
        for i, pwd in enumerate(passwords, 1):
            if length >= 16 and not no_special and not no_numbers:
                strength = "🟢 Strong"
            elif length >= 12:
                strength = "🟡 Medium"
            else:
                strength = "🔴 Weak"
            
            table.add_row(str(i), f"[bold]{pwd}[/bold]", strength)
        
        console.print(table)
        
        char_info = []
        if not no_uppercase:
            char_info.append("uppercase")
        if not no_numbers:
            char_info.append("numbers")
        if not no_special:
            char_info.append("special chars")
        
        console.print(f"\n[dim]Character set: lowercase, {', '.join(char_info)}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error generating password: {e}[/red]")


def markdown_renderer(args: List[str]) -> None:
    """Render markdown with beautiful formatting."""
    if not args:
        console.print("[red]Usage: markdown <file>[/red]")
        return
    
    file = args[0]
    
    try:
        file_path = Path(file)
        if not file_path.exists():
            console.print(f"[red]File not found: {file}[/red]")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        if not markdown_content:
            console.print("[yellow]No content to render[/yellow]")
            return
        
        md = Markdown(markdown_content)
        console.print(Panel(md, title="Markdown Preview", border_style="blue", expand=True))
        
    except Exception as e:
        console.print(f"[red]Error rendering markdown: {e}[/red]")


def base64_converter(args: List[str]) -> None:
    """Encode or decode Base64 strings."""
    if not args:
        console.print("[red]Usage: base64 <text> [--decode][/red]")
        return
    
    text = args[0]
    decode = '--decode' in args or '-d' in args
    
    try:
        import base64
        
        if decode:
            try:
                decoded = base64.b64decode(text).decode('utf-8')
                result = decoded
                operation = "Decoded"
                color = "green"
            except Exception as e:
                console.print(f"[red]Invalid Base64 string: {e}[/red]")
                return
        else:
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            result = encoded
            operation = "Encoded"
            color = "blue"
        
        console.print(Panel(
            f"[{color}]{result}[/{color}]",
            title=f"{operation} Result",
            border_style=color,
            expand=False
        ))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def hash_text(args: List[str]) -> None:
    """Generate hash of text using various algorithms."""
    if not args:
        console.print("[red]Usage: hash <text> [--algorithm sha256][/red]")
        return
    
    text = args[0]
    algorithm = "sha256"
    
    # Parse algorithm
    i = 1
    while i < len(args):
        if args[i] in ['--algorithm', '-a'] and i + 1 < len(args):
            algorithm = args[i + 1].lower()
            i += 2
        else:
            i += 1
    
    try:
        import hashlib
        
        if algorithm == "md5":
            hash_obj = hashlib.md5(text.encode('utf-8'))
        elif algorithm == "sha1":
            hash_obj = hashlib.sha1(text.encode('utf-8'))
        elif algorithm == "sha256":
            hash_obj = hashlib.sha256(text.encode('utf-8'))
        elif algorithm == "sha512":
            hash_obj = hashlib.sha512(text.encode('utf-8'))
        else:
            console.print(f"[red]Unsupported algorithm: {algorithm}[/red]")
            console.print("Supported: md5, sha1, sha256, sha512")
            return
        
        hash_value = hash_obj.hexdigest()
        
        table = Table(title="Hash Result", show_header=True, header_style="bold magenta")
        table.add_column("Algorithm", style="cyan")
        table.add_column("Hash", style="green")
        
        table.add_row(algorithm.upper(), hash_value)
        
        console.print(table)
        
        if algorithm in ["md5", "sha1"]:
            console.print("\n[yellow]⚠ Warning: This algorithm is not recommended for security purposes.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error generating hash: {e}[/red]")


def generate_uuid(args: List[str]) -> None:
    """Generate UUIDs (Universally Unique Identifiers)."""
    count = 1
    uuid_version = 4
    
    # Parse args
    i = 0
    while i < len(args):
        if args[i] in ['--count', '-c'] and i + 1 < len(args):
            count = int(args[i + 1])
            i += 2
        elif args[i] in ['--version', '-v'] and i + 1 < len(args):
            uuid_version = int(args[i + 1])
            i += 2
        else:
            i += 1
    
    try:
        import uuid
        
        if uuid_version not in [1, 4]:
            console.print("[red]Only UUID version 1 and 4 are supported[/red]")
            return
        
        if count < 1 or count > 100:
            console.print("[red]Count must be between 1 and 100[/red]")
            return
        
        table = Table(title=f"Generated UUID v{uuid_version}", show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", justify="center")
        table.add_column("UUID", style="green")
        
        for i in range(count):
            if uuid_version == 1:
                new_uuid = str(uuid.uuid1())
            else:
                new_uuid = str(uuid.uuid4())
            
            table.add_row(str(i + 1), new_uuid)
        
        console.print(table)
        
        if uuid_version == 1:
            console.print("\n[dim]UUID v1: Time-based (includes MAC address and timestamp)[/dim]")
        else:
            console.print("\n[dim]UUID v4: Random (cryptographically secure)[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error generating UUID: {e}[/red]")
