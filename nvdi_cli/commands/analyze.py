import typer

app = typer.Typer()


@app.command()
def vuln(cve_id: str):
    """Analyze a CVE (risk summary, affected versions). Placeholder for extended analysis."""
    typer.echo(f"Analyze: {cve_id} (analysis engine not yet implemented)")
