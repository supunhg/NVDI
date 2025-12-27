import typer

app = typer.Typer()


@app.command()
def cves(a: str, b: str):
    """Compare two CVE queries or IDs (placeholder)"""
    typer.echo(f"Compare {a} vs {b} — comparison engine not implemented yet.")
