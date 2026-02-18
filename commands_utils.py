"""
Utility commands for PythonParagon.

This module provides miscellaneous utilities like currency conversion, password generation, and markdown rendering.
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
import requests
import secrets
import string
from typing import Optional
from pathlib import Path
from config import config

utils_app = typer.Typer(help="General utility commands")
console = Console()


@utils_app.command("currency")
def currency_converter(
    amount: float = typer.Argument(..., help="Amount to convert"),
    from_currency: str = typer.Argument(..., help="Source currency code (e.g., USD)"),
    to_currency: str = typer.Argument(..., help="Target currency code (e.g., EUR)")
) -> None:
    """
    Convert currency using live exchange rates.
    
    Uses an external API to fetch current exchange rates and convert between currencies.
    """
    try:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
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
            raise typer.Exit(code=1)
        
        exchange_rate = data['rates'][to_currency]
        converted_amount = amount * exchange_rate
        
        # Display result
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
        
        # Show date if available
        if 'date' in data:
            console.print(f"[dim]Rate as of: {data['date']}[/dim]")
        
    except requests.RequestException as e:
        console.print(f"[red]Error fetching exchange rates: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


@utils_app.command("password")
def password_generator(
    length: int = typer.Option(16, help="Password length"),
    count: int = typer.Option(1, help="Number of passwords to generate"),
    no_special: bool = typer.Option(False, help="Exclude special characters"),
    no_numbers: bool = typer.Option(False, help="Exclude numbers"),
    no_uppercase: bool = typer.Option(False, help="Exclude uppercase letters")
) -> None:
    """
    Generate secure random passwords.
    
    Creates cryptographically secure passwords with customizable character sets.
    """
    try:
        if length < 4:
            console.print("[red]Password length must be at least 4 characters[/red]")
            raise typer.Exit(code=1)
        
        if count < 1 or count > 100:
            console.print("[red]Count must be between 1 and 100[/red]")
            raise typer.Exit(code=1)
        
        # Build character set
        characters = string.ascii_lowercase
        
        if not no_uppercase:
            characters += string.ascii_uppercase
        
        if not no_numbers:
            characters += string.digits
        
        if not no_special:
            characters += string.punctuation
        
        if len(characters) < 4:
            console.print("[red]Character set too small. Enable at least one character type.[/red]")
            raise typer.Exit(code=1)
        
        # Generate passwords
        passwords = []
        for _ in range(count):
            password = ''.join(secrets.choice(characters) for _ in range(length))
            passwords.append(password)
        
        # Display
        table = Table(title=f"Generated Password(s)", show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", justify="center")
        table.add_column("Password", style="green")
        table.add_column("Strength", style="yellow")
        
        for i, pwd in enumerate(passwords, 1):
            # Simple strength indicator
            if length >= 16 and not no_special and not no_numbers:
                strength = "🟢 Strong"
            elif length >= 12:
                strength = "🟡 Medium"
            else:
                strength = "🔴 Weak"
            
            table.add_row(str(i), f"[bold]{pwd}[/bold]", strength)
        
        console.print(table)
        
        # Show character set info
        char_info = []
        if not no_uppercase:
            char_info.append("uppercase")
        if not no_numbers:
            char_info.append("numbers")
        if not no_special:
            char_info.append("special chars")
        
        console.print(f"\n[dim]Character set: lowercase, {', '.join(char_info)}[/dim]")
        console.print("[dim]Tip: Use strong passwords (16+ chars with all character types)[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error generating password: {e}[/red]")
        raise typer.Exit(code=1)


@utils_app.command("markdown")
def markdown_renderer(
    file: Optional[str] = typer.Argument(None, help="Markdown file to render"),
    text: Optional[str] = typer.Option(None, help="Markdown text to render directly")
) -> None:
    """
    Render markdown with beautiful formatting.
    
    Displays markdown content with syntax highlighting and proper formatting.
    """
    try:
        markdown_content = ""
        
        if file:
            file_path = Path(file)
            if not file_path.exists():
                console.print(f"[red]File not found: {file}[/red]")
                raise typer.Exit(code=1)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        elif text:
            markdown_content = text
        else:
            console.print("[red]Please provide either a file or text to render[/red]")
            console.print("Usage: python main.py utils markdown <file> or --text 'your markdown'")
            raise typer.Exit(code=1)
        
        if not markdown_content:
            console.print("[yellow]No content to render[/yellow]")
            return
        
        md = Markdown(markdown_content)
        console.print(Panel(md, title="Markdown Preview", border_style="blue", expand=True))
        
    except Exception as e:
        console.print(f"[red]Error rendering markdown: {e}[/red]")
        raise typer.Exit(code=1)


@utils_app.command("base64")
def base64_converter(
    text: str = typer.Argument(..., help="Text to encode/decode"),
    decode: bool = typer.Option(False, help="Decode instead of encode")
) -> None:
    """
    Encode or decode Base64 strings.
    
    Converts text to/from Base64 encoding.
    """
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
                raise typer.Exit(code=1)
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
        raise typer.Exit(code=1)


@utils_app.command("hash")
def hash_text(
    text: str = typer.Argument(..., help="Text to hash"),
    algorithm: str = typer.Option("sha256", help="Hash algorithm (md5, sha1, sha256, sha512)")
) -> None:
    """
    Generate hash of text using various algorithms.
    
    Supports MD5, SHA1, SHA256, and SHA512 hashing algorithms.
    """
    try:
        import hashlib
        
        algorithm = algorithm.lower()
        
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
            raise typer.Exit(code=1)
        
        hash_value = hash_obj.hexdigest()
        
        table = Table(title="Hash Result", show_header=True, header_style="bold magenta")
        table.add_column("Algorithm", style="cyan")
        table.add_column("Hash", style="green")
        
        table.add_row(algorithm.upper(), hash_value)
        
        console.print(table)
        
        # Security note for MD5 and SHA1
        if algorithm in ["md5", "sha1"]:
            console.print("\n[yellow]⚠ Warning: This algorithm is not recommended for security purposes.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error generating hash: {e}[/red]")
        raise typer.Exit(code=1)


@utils_app.command("uuid")
def generate_uuid(
    count: int = typer.Option(1, help="Number of UUIDs to generate"),
    version: int = typer.Option(4, help="UUID version (1 or 4)")
) -> None:
    """
    Generate UUIDs (Universally Unique Identifiers).
    
    Creates UUID v1 (time-based) or UUID v4 (random) identifiers.
    """
    try:
        import uuid
        
        if version not in [1, 4]:
            console.print("[red]Only UUID version 1 and 4 are supported[/red]")
            raise typer.Exit(code=1)
        
        if count < 1 or count > 100:
            console.print("[red]Count must be between 1 and 100[/red]")
            raise typer.Exit(code=1)
        
        table = Table(title=f"Generated UUID v{version}", show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", justify="center")
        table.add_column("UUID", style="green")
        
        for i in range(count):
            if version == 1:
                new_uuid = str(uuid.uuid1())
            else:
                new_uuid = str(uuid.uuid4())
            
            table.add_row(str(i + 1), new_uuid)
        
        console.print(table)
        
        if version == 1:
            console.print("\n[dim]UUID v1: Time-based (includes MAC address and timestamp)[/dim]")
        else:
            console.print("\n[dim]UUID v4: Random (cryptographically secure)[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error generating UUID: {e}[/red]")
        raise typer.Exit(code=1)
