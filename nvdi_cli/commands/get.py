import typer
import asyncio
from typing import Optional, List
from nvdi_cli.api.client import NVDClient
from nvdi_cli.utils.formatters import print_cve, print_cve_full, print_cve_fields
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def cve(cve_id: str, 
        full: bool = typer.Option(False, "--full", "-f", help="Show all available data"),
        fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated fields to show")):
    """Get a single CVE by ID"""
    async def _get():
        console.print(f"[cyan]Fetching {cve_id}...[/cyan]")
        client = NVDClient()
        try:
            result = await client.get_cve(cve_id)
            if not result:
                console.print(f"[red]CVE {cve_id} not found[/red]")
                raise typer.Exit(code=1)
            
            if full:
                print_cve_full(result)
            elif fields:
                field_list = [f.strip() for f in fields.split(",")]
                print_cve_fields(result, field_list)
            else:
                print_cve(result)
        finally:
            await client.close()
    
    asyncio.run(_get())
