import click

from typing import Optional

from .alerts import send
from .logging import setup as get_logger
from .population import download


@click.group()
@click.option(
    "--db-population",
    help="path to the SQLite database where population data is stored",
    required=True,
)
@click.option(
    "--debug/--no-debug", help="enable debug mode: verbose logging", default=False,
)
@click.pass_context
def cli(
    ctx: Optional[click.Context] = None,
    db_population: str = None,
    debug: bool = False,
    **kw,
):
    if ctx is not None:
        ctx.ensure_object(dict)
        ctx.obj['db_population'] = db_population
        ctx.obj['debug'] = debug


@cli.command()
@click.argument('url', required=True)
@click.pass_context
def download_population(ctx: click.Context, url: str):
    """Download the population data and stores it in a local database

    URL is the URL of the CSV containing the population data (region_id, population).
    The CSV is expected to be comma separated, UTF-8 encoded, and included the header.
    """
    db_population = ctx.obj['db_population']
    debug = ctx.obj['debug']
    logger = get_logger(debug)
    download(db_population, url, logger=logger)


@cli.command()
@click.option(
    "-c",
    "--config",
    type=click.STRING,
    help="configuration file (yaml format), see README.md for the format",
    required=True,
)
@click.option(
    "--dry-run/--no-dry-run",
    help="enable dry-run mode: no notification is sent, only output is produced",
    default=False,
)
@click.pass_context
def send_alerts(ctx: click.Context, config: str, dry_run: bool = False):
    db_population = ctx.obj['db_population']
    debug = ctx.obj['debug']
    logger = get_logger(debug)
    send(db_population, config, logger=logger)


def cli_with_env():  # pragma: no cover
    cli(auto_envvar_prefix="WFP_FOOD_SECURITY_ALERTS")
