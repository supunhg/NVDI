import typer
import json
import csv
import sys
from typing import Optional
from nvdi_cli.api.client import NVDClient
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def cve(cve_id: str, 
        fmt: str = typer.Option("json", "--format", "-f", help="Export format: json, csv, yaml, txt"),
        fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated fields to export"),
        outfile: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path")):
    """Export a CVE in various formats"""
    import asyncio

    async def _export():
        client = NVDClient()
        try:
            model = await client.get_cve(cve_id)
            if not model:
                console.print(f"[red]CVE {cve_id} not found[/red]")
                raise typer.Exit(code=1)
            
            data = model.dict()
            
            # Filter fields if specified
            if fields:
                field_list = [f.strip() for f in fields.split(",")]
                data = {k: v for k, v in data.items() if k in field_list}
            
            # Generate output
            output_content = None
            if fmt == "json":
                output_content = json.dumps(data, indent=2, default=str)
            elif fmt == "yaml":
                try:
                    import yaml
                    output_content = yaml.dump(data, default_flow_style=False)
                except ImportError:
                    console.print("[yellow]PyYAML not installed. Install with: pip install pyyaml[/yellow]")
                    output_content = json.dumps(data, indent=2, default=str)
            elif fmt == "csv":
                import io
                output = io.StringIO()
                if isinstance(data, dict):
                    writer = csv.writer(output)
                    writer.writerow(["Field", "Value"])
                    for key, value in data.items():
                        writer.writerow([key, str(value)])
                    output_content = output.getvalue()
            elif fmt == "txt":
                lines = []
                for key, value in data.items():
                    lines.append(f"{key}: {value}")
                output_content = "\n".join(lines)
            else:
                console.print(f"[red]Unsupported format: {fmt}[/red]")
                raise typer.Exit(code=1)
            
            # Output to file or stdout
            if outfile:
                with open(outfile, "w") as f:
                    f.write(output_content)
                console.print(f"[green]Exported to {outfile}[/green]")
            else:
                typer.echo(output_content)
        finally:
            await client.close()
    
    asyncio.run(_export())
