import typer
import asyncio
from typing import Optional
from nvdi_cli.db import init_db
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


@app.command()
def show(year: Optional[int] = None):
    """Show CVE statistics from local database"""
    async def _stats():
        db = await init_db()
        stats = await db.get_stats(year=year)
        await db.close()
        
        table = Table(title=f"CVE Statistics" + (f" ({year})" if year else ""))
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total CVEs", str(stats["total_cves"]))
        table.add_row("Average CVSS Score", str(stats["avg_score"]))
        table.add_row("Highest CVSS Score", str(stats["max_score"]))
        
        console.print(table)
    
    asyncio.run(_stats())
