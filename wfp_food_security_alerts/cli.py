import click


@click.group()
@click.option(
    "--db-population",
    help="path to the SQLite database where population data is stored",
    required=True,
)
@click.option(
    "--debug/--no-debug", help="enable debug mode: verbose logging", default=False,
)
def cli(
    db_population: str = None, debug: bool = False, **kw,
):
    pass


@cli.command()
def download_population():
    pass


@cli.command()
@click.option(
    "--dry-run/--no-dry-run",
    help="enable dry-run mode: no notification is sent, only output is produced",
    default=False,
)
def send_alerts(dry_run: bool = False,):
    pass


def cli_with_env():  # pragma: no cover
    cli(auto_envvar_prefix="WFP_FOOD_SECURITY_ALERTS")
