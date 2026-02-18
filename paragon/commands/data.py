"""
Data processing commands for PythonParagon.

This module provides commands for working with JSON, YAML, and CSV files.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from pathlib import Path
from typing import List
import json
import yaml

console = Console()


def json_format(args: List[str]) -> None:
    """Format and validate JSON files."""
    if not args:
        console.print("[red]Usage: json-format <file> [--indent 2] [--output file][/red]")
        return
    
    file_path = Path(args[0])
    indent = 2
    output_file = None
    
    # Parse args
    i = 1
    while i < len(args):
        if args[i] in ['--indent', '-i'] and i + 1 < len(args):
            indent = int(args[i + 1])
            i += 2
        elif args[i] in ['--output', '-o'] and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        else:
            i += 1
    
    try:
        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        console.print("[green]✓ Valid JSON file[/green]\n")
        
        # Format JSON
        formatted_json = json.dumps(data, indent=indent, sort_keys=False)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(formatted_json)
            console.print(f"[green]Formatted JSON written to {output_file}[/green]")
        else:
            # Display formatted JSON with syntax highlighting
            syntax = Syntax(formatted_json, "json", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Formatted JSON", border_style="green"))
        
        # Show statistics
        def count_elements(obj):
            if isinstance(obj, dict):
                return 1 + sum(count_elements(v) for v in obj.values())
            elif isinstance(obj, list):
                return 1 + sum(count_elements(item) for item in obj)
            else:
                return 1
        
        total_elements = count_elements(data)
        console.print(f"\n[dim]Total elements: {total_elements}[/dim]")
        
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def yaml_format(args: List[str]) -> None:
    """Format and validate YAML files."""
    if not args:
        console.print("[red]Usage: yaml-format <file> [--output file][/red]")
        return
    
    file_path = Path(args[0])
    output_file = None
    
    # Parse args
    i = 1
    while i < len(args):
        if args[i] in ['--output', '-o'] and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        else:
            i += 1
    
    try:
        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return
        
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        console.print("[green]✓ Valid YAML file[/green]\n")
        
        # Format YAML
        formatted_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(formatted_yaml)
            console.print(f"[green]Formatted YAML written to {output_file}[/green]")
        else:
            # Display formatted YAML with syntax highlighting
            syntax = Syntax(formatted_yaml, "yaml", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Formatted YAML", border_style="green"))
        
    except yaml.YAMLError as e:
        console.print(f"[red]Invalid YAML: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def csv_stats(args: List[str]) -> None:
    """Show statistics for CSV files."""
    if not args:
        console.print("[red]Usage: csv-stats <file>[/red]")
        return
    
    file_path = Path(args[0])
    
    try:
        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return
        
        import pandas as pd
        
        df = pd.read_csv(file_path)
        
        # Basic stats
        console.print(Panel(
            f"[bold]Rows:[/bold] {len(df)}\n"
            f"[bold]Columns:[/bold] {len(df.columns)}\n"
            f"[bold]Size:[/bold] {file_path.stat().st_size / 1024:.2f} KB",
            title="CSV Statistics",
            border_style="blue"
        ))
        
        # Column info
        table = Table(title="Column Information", show_header=True, header_style="bold magenta")
        table.add_column("Column", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Non-Null", style="green", justify="right")
        table.add_column("Unique", style="blue", justify="right")
        
        for col in df.columns:
            table.add_row(
                col,
                str(df[col].dtype),
                str(df[col].notna().sum()),
                str(df[col].nunique())
            )
        
        console.print(table)
        
        # Show first few rows
        console.print("\n[bold]Preview (first 5 rows):[/bold]")
        preview_table = Table(show_header=True, header_style="bold magenta")
        
        for col in df.columns[:10]:  # Limit to 10 columns for display
            preview_table.add_column(col, style="cyan")
        
        for idx in range(min(5, len(df))):
            row_data = [str(df.iloc[idx][col])[:30] for col in df.columns[:10]]
            preview_table.add_row(*row_data)
        
        console.print(preview_table)
        
        if len(df.columns) > 10:
            console.print(f"\n[dim]Showing first 10 of {len(df.columns)} columns[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error analyzing CSV: {e}[/red]")


def json_query(args: List[str]) -> None:
    """Query JSON files using dot notation path."""
    if len(args) < 2:
        console.print("[red]Usage: json-query <file> <path>[/red]")
        console.print("[dim]Example: json-query data.json users.0.name[/dim]")
        return
    
    file_path = Path(args[0])
    query_path = args[1]
    
    try:
        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Parse query path
        parts = query_path.split('.')
        result = data
        
        for part in parts:
            if part.isdigit():
                result = result[int(part)]
            else:
                result = result[part]
        
        # Display result
        result_json = json.dumps(result, indent=2)
        syntax = Syntax(result_json, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"Query Result: {query_path}", border_style="green"))
        
    except KeyError as e:
        console.print(f"[red]Key not found: {e}[/red]")
    except IndexError as e:
        console.print(f"[red]Index out of range: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
