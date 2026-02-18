"""
Text and log analysis commands for PythonParagon.

This module provides commands for analyzing text files and logs.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
from typing import List
import re
from collections import Counter

console = Console()


def log_analyze(args: List[str]) -> None:
    """Analyze log files."""
    if not args:
        console.print("[red]Usage: log-analyze <file>[/red]")
        return
    
    file_path = Path(args[0])
    
    try:
        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Count log levels
        error_count = 0
        warning_count = 0
        info_count = 0
        debug_count = 0
        
        error_pattern = re.compile(r'\b(error|err|exception|failed|failure)\b', re.IGNORECASE)
        warning_pattern = re.compile(r'\b(warning|warn)\b', re.IGNORECASE)
        info_pattern = re.compile(r'\b(info|information)\b', re.IGNORECASE)
        debug_pattern = re.compile(r'\b(debug|trace)\b', re.IGNORECASE)
        
        recent_errors = []
        
        for i, line in enumerate(lines):
            if error_pattern.search(line):
                error_count += 1
                if len(recent_errors) < 5:
                    recent_errors.append((i + 1, line.strip()[:80]))
            elif warning_pattern.search(line):
                warning_count += 1
            elif info_pattern.search(line):
                info_count += 1
            elif debug_pattern.search(line):
                debug_count += 1
        
        # Display summary
        summary_text = f"[bold]Total Lines:[/bold] {len(lines)}\n"
        summary_text += f"[bold red]Errors:[/bold red] {error_count}\n"
        summary_text += f"[bold yellow]Warnings:[/bold yellow] {warning_count}\n"
        summary_text += f"[bold green]Info:[/bold green] {info_count}\n"
        summary_text += f"[bold blue]Debug:[/bold blue] {debug_count}\n"
        
        console.print(Panel(summary_text, title="Log Analysis Summary", border_style="blue"))
        
        # Show recent errors
        if recent_errors:
            table = Table(title="Recent Errors", show_header=True, header_style="bold magenta")
            table.add_column("Line", style="cyan", width=8)
            table.add_column("Message", style="red")
            
            for line_num, message in recent_errors:
                table.add_row(str(line_num), message)
            
            console.print(table)
        
        # Get most common words
        all_text = ' '.join(lines).lower()
        words = re.findall(r'\b\w{4,}\b', all_text)  # Words with 4+ chars
        word_counts = Counter(words).most_common(10)
        
        if word_counts:
            table = Table(title="Most Common Words", show_header=True, header_style="bold magenta")
            table.add_column("Word", style="cyan")
            table.add_column("Count", style="green", justify="right")
            
            for word, count in word_counts:
                table.add_row(word, str(count))
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error analyzing log: {e}[/red]")


def text_stats(args: List[str]) -> None:
    """Show statistics for text files."""
    if not args:
        console.print("[red]Usage: text-stats <file>[/red]")
        return
    
    file_path = Path(args[0])
    
    try:
        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        words = content.split()
        
        # Count various elements
        char_count = len(content)
        line_count = len(lines)
        word_count = len(words)
        
        # Empty lines
        empty_lines = sum(1 for line in lines if not line.strip())
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Longest line
        longest_line_length = max(len(line) for line in lines) if lines else 0
        
        # Display stats
        stats_text = f"[bold]Characters:[/bold] {char_count:,}\n"
        stats_text += f"[bold]Words:[/bold] {word_count:,}\n"
        stats_text += f"[bold]Lines:[/bold] {line_count:,}\n"
        stats_text += f"[bold]Empty Lines:[/bold] {empty_lines}\n"
        stats_text += f"[bold]Avg Word Length:[/bold] {avg_word_length:.1f}\n"
        stats_text += f"[bold]Longest Line:[/bold] {longest_line_length} chars\n"
        stats_text += f"[bold]File Size:[/bold] {file_path.stat().st_size / 1024:.2f} KB"
        
        console.print(Panel(stats_text, title="Text File Statistics", border_style="green"))
        
        # Word frequency
        word_freq = Counter(word.lower() for word in words)
        top_words = word_freq.most_common(10)
        
        if top_words:
            table = Table(title="Top 10 Words", show_header=True, header_style="bold magenta")
            table.add_column("Word", style="cyan")
            table.add_column("Frequency", style="green", justify="right")
            
            for word, freq in top_words:
                table.add_row(word, str(freq))
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error analyzing text: {e}[/red]")


def word_count(args: List[str]) -> None:
    """Count words and lines in a file."""
    if not args:
        console.print("[red]Usage: word-count <file>[/red]")
        return
    
    file_path = Path(args[0])
    
    try:
        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        words = content.split()
        chars = len(content)
        
        # Display results in a simple format
        result_text = f"""
[bold cyan]File:[/bold cyan] {file_path.name}

[bold yellow]Lines:[/bold yellow]      {len(lines):>10,}
[bold green]Words:[/bold green]      {len(words):>10,}
[bold blue]Characters:[/bold blue] {chars:>10,}
"""
        
        console.print(Panel(result_text, title="Word Count", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[red]Error counting words: {e}[/red]")
