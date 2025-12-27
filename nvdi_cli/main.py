import asyncio
import typer

from nvdi_cli.commands import get as get_cmd
from nvdi_cli.commands import search as search_cmd
from nvdi_cli.commands import analyze as analyze_cmd
from nvdi_cli.commands import monitor as monitor_cmd
from nvdi_cli.commands import export as export_cmd
from nvdi_cli.commands import stats as stats_cmd
from nvdi_cli.commands import compare as compare_cmd
from nvdi_cli.commands import db as db_cmd

app = typer.Typer(help="nvdi — NVD CLI tool")

app.add_typer(get_cmd.app, name="get")
app.add_typer(search_cmd.app, name="search")
app.add_typer(analyze_cmd.app, name="analyze")
app.add_typer(monitor_cmd.app, name="monitor")
app.add_typer(export_cmd.app, name="export")
app.add_typer(stats_cmd.app, name="stats")
app.add_typer(compare_cmd.app, name="compare")
app.add_typer(db_cmd.app, name="db")


def main():
    typer.run(app)


if __name__ == "__main__":
    asyncio.run(app())
