import typer
import asyncio
from typing import Optional
from nvdi_cli.api.client import NVDClient
from nvdi_cli.utils.formatters import print_cve_list
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def keyword(q: str, limit: int = 20, min_score: Optional[float] = None):
    """Search CVEs by keyword with optional CVSS filter"""
    async def _search():
        console.print(f"[cyan]Searching for '{q}'...[/cyan]")
        client = NVDClient()
        try:
            results = await client.search_cves(keyword=q, resultsPerPage=limit, min_score=min_score)
            if not results:
                console.print("[yellow]No results found[/yellow]")
                raise typer.Exit()
            print_cve_list(results)
        finally:
            await client.close()
    
    asyncio.run(_search())
