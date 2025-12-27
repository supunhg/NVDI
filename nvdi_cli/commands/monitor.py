import typer
import asyncio
from typing import List
from nvdi_cli.db import init_db
from nvdi_cli.api.client import NVDClient
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer()
console = Console()


@app.command()
def add(product: str):
    """Add a product to monitoring list"""
    async def _add():
        db = await init_db()
        await db.add_monitored_product(product)
        await db.close()
        console.print(f"[green]Added {product} to monitoring list[/green]")
    
    asyncio.run(_add())


@app.command()
def list_products():
    """List all monitored products"""
    async def _list():
        db = await init_db()
        products = await db.get_monitored_products()
        await db.close()
        
        if not products:
            console.print("[yellow]No products being monitored[/yellow]")
            return
        
        console.print("[cyan]Monitored Products:[/cyan]")
        for p in products:
            console.print(f"  • {p}")
    
    asyncio.run(_list())


@app.command()
def watch(product: str, interval: int = 300):
    """Watch for new CVEs for a product (blocking loop)"""
    async def _watch():
        db = await init_db()
        await db.add_monitored_product(product)
        client = NVDClient()
        
        console.print(f"[green]Monitoring {product} for new CVEs (Ctrl+C to stop)[/green]")
        
        try:
            while True:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task(f"Checking {product}...", total=None)
                    results = await client.search_cves(keyword=product, resultsPerPage=5)
                    progress.update(task, completed=True)
                
                if results:
                    console.print(f"[cyan]Found {len(results)} recent CVEs[/cyan]")
                    for cve in results:
                        await db.link_product_cve(product, cve.id)
                
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopped monitoring[/yellow]")
        finally:
            await db.close()
    
    asyncio.run(_watch())
