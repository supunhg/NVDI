from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from typing import List
import json
from nvdi_cli.api.models import CVEModel

console = Console()


def _get_severity_color(score: float) -> str:
    """Get color based on CVSS score"""
    if score >= 9.0:
        return "red bold"
    elif score >= 7.0:
        return "red"
    elif score >= 4.0:
        return "yellow"
    else:
        return "green"


def _extract_cvss_score(cvssv3) -> float:
    """Safely extract CVSS score"""
    if not cvssv3:
        return None
    if hasattr(cvssv3, 'baseScore'):
        return cvssv3.baseScore
    if isinstance(cvssv3, dict):
        return cvssv3.get('baseScore')
    return None


def print_cve(cve: CVEModel) -> None:
    """Print basic CVE information"""
    score = _extract_cvss_score(cve.cvssv3)
    score_text = f"{score}" if score else "N/A"
    score_color = _get_severity_color(score) if score else "white"
    
    table = Table(title=f"[bold cyan]{cve.id}[/bold cyan]", show_header=False, box=None)
    table.add_column("Field", style="bold cyan", width=20)
    table.add_column("Value")
    
    desc = cve.description or "No description available"
    if len(desc) > 100:
        desc = desc[:300] + "..."
    
    table.add_row("Description", desc)
    table.add_row("Published", cve.publishedDate or "N/A")
    table.add_row("Last Modified", cve.lastModifiedDate or "N/A")
    table.add_row("Status", cve.vulnStatus or "N/A")
    table.add_row("CVSS v3 Score", f"[{score_color}]{score_text}[/{score_color}]")
    
    if cve.cvssv3:
        vector = cve.cvssv3.vectorString if hasattr(cve.cvssv3, 'vectorString') else cve.cvssv3.get('vectorString') if isinstance(cve.cvssv3, dict) else None
        if vector:
            table.add_row("CVSS v3 Vector", vector)
    
    console.print(Panel(table, border_style="cyan"))


def print_cve_full(cve: CVEModel) -> None:
    """Print comprehensive CVE information"""
    console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
    console.print(f"[bold white]{cve.id}[/bold white]")
    console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")
    
    # Basic Info
    console.print("[bold yellow]BASIC INFORMATION[/bold yellow]")
    console.print(f"  Source: {cve.sourceIdentifier or 'N/A'}")
    console.print(f"  Status: {cve.vulnStatus or 'N/A'}")
    console.print(f"  Published: {cve.publishedDate or 'N/A'}")
    console.print(f"  Modified: {cve.lastModifiedDate or 'N/A'}")
    console.print(f"\n  Description:\n  {cve.description or 'N/A'}\n")
    
    # CVSS Scores
    if cve.cvssv3:
        console.print("[bold yellow]CVSS v3 METRICS[/bold yellow]")
        cvss = cve.cvssv3 if isinstance(cve.cvssv3, dict) else cve.cvssv3.dict()
        console.print(f"  Base Score: {cvss.get('baseScore', 'N/A')}")
        console.print(f"  Severity: {cvss.get('baseSeverity', 'N/A')}")
        console.print(f"  Vector: {cvss.get('vectorString', 'N/A')}")
        console.print(f"  Exploitability: {cvss.get('exploitabilityScore', 'N/A')}")
        console.print(f"  Impact: {cvss.get('impactScore', 'N/A')}\n")
    
    if cve.cvssv2:
        console.print("[bold yellow]CVSS v2 METRICS[/bold yellow]")
        cvss = cve.cvssv2 if isinstance(cve.cvssv2, dict) else cve.cvssv2.dict()
        console.print(f"  Base Score: {cvss.get('baseScore', 'N/A')}")
        console.print(f"  Severity: {cvss.get('severity', 'N/A')}")
        console.print(f"  Vector: {cvss.get('vectorString', 'N/A')}\n")
    
    # Weaknesses
    if cve.weaknesses:
        console.print("[bold yellow]WEAKNESSES (CWE)[/bold yellow]")
        for w in cve.weaknesses:
            if isinstance(w, dict):
                console.print(f"  {w.get('source', 'N/A')}: {', '.join(w.get('description', []))}")
        console.print()
    
    # References
    if cve.references:
        console.print(f"[bold yellow]REFERENCES ({len(cve.references)})[/bold yellow]")
        for ref in cve.references[:10]:  # Limit to first 10
            ref_dict = ref if isinstance(ref, dict) else ref.dict()
            tags = ", ".join(ref_dict.get('tags', []))
            console.print(f"  • {ref_dict.get('url')}")
            if tags:
                console.print(f"    Tags: {tags}")
        if len(cve.references) > 10:
            console.print(f"  ... and {len(cve.references) - 10} more")
        console.print()
    
    # CPE Configurations
    if cve.configurations:
        console.print(f"[bold yellow]AFFECTED CONFIGURATIONS ({len(cve.configurations)})[/bold yellow]")
        for cfg in cve.configurations[:5]:  # Limit to first 5
            cfg_dict = cfg if isinstance(cfg, dict) else cfg.dict()
            console.print(f"  • {cfg_dict.get('criteria', 'N/A')}")
        if len(cve.configurations) > 5:
            console.print(f"  ... and {len(cve.configurations) - 5} more")
        console.print()


def print_cve_fields(cve: CVEModel, fields: List[str]) -> None:
    """Print specific fields of CVE"""
    data = cve.dict()
    table = Table(title=f"[bold cyan]{cve.id}[/bold cyan]")
    table.add_column("Field", style="cyan bold")
    table.add_column("Value")
    
    for field in fields:
        if field in data:
            value = data[field]
            if isinstance(value, (list, dict)):
                value = json.dumps(value, indent=2)
            table.add_row(field, str(value))
        else:
            table.add_row(field, "[red]Not found[/red]")
    
    console.print(table)


def print_cve_list(cves: List[CVEModel]) -> None:
    """Print list of CVEs in a table"""
    table = Table(title=f"[bold]CVE Search Results[/bold] ({len(cves)} found)", show_lines=False)
    table.add_column("CVE ID", style="cyan bold", width=18)
    table.add_column("Score", justify="center", width=8)
    table.add_column("Published", width=12)
    table.add_column("Description", max_width=60)
    
    for c in cves:
        score = _extract_cvss_score(c.cvssv3)
        score_str = f"{score:.1f}" if score else "N/A"
        score_color = _get_severity_color(score) if score else "dim"
        
        pub_date = c.publishedDate[:10] if c.publishedDate else "N/A"
        
        desc = (c.description or "No description")[:120]
        if len(c.description or "") > 120:
            desc += "..."
        
        table.add_row(
            c.id,
            f"[{score_color}]{score_str}[/{score_color}]",
            pub_date,
            desc
        )
    
    console.print(table)
