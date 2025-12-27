import typer
import asyncio
from nvdi_cli.db import init_db
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def clear():
    """Clear/reset all database data"""
    async def _reset():
        confirm = typer.confirm("Are you sure you want to clear all database data?")
        if not confirm:
            console.print("[yellow]Operation cancelled[/yellow]")
            return
        
        db = await init_db()
        try:
            await db.reset()
            console.print("[green]✓ Database cleared successfully[/green]")
        finally:
            await db.close()
    
    asyncio.run(_reset())


@app.command()
def info():
    """Show database information"""
    async def _info():
        db = await init_db()
        try:
            stats = await db.get_stats()
            products = await db.get_monitored_products()
            
            console.print(f"[cyan]Database:[/cyan] .nvdi-data/nvdi.db")
            console.print(f"[cyan]CVEs Cached:[/cyan] {stats['total_cves']}")
            console.print(f"[cyan]Monitored Products:[/cyan] {len(products)}")
        finally:
            await db.close()
    
    asyncio.run(_info())
