"""The `api` cli
Usage:
    $ api --help
"""

import typer

from api.utils.log import logger, set_log_level_to_debug


cli = typer.Typer(
    help="Run Api commands",
    no_args_is_help=True,
    invoke_without_command=True,
    # https://typer.tiangolo.com/tutorial/exceptions/#disable-local-variables-for-security
    pretty_exceptions_show_locals=False,
)


@cli.command(short_help="Start")
def start(
    reload: bool = typer.Option(
        False, "--reload", "-r", help="Reload", show_default=True
    ),
    print_debug_log: bool = typer.Option(
        False, "--debug", "-d", help="Print debug logs."
    ),
):
    """
    \b
    Start Api server.

    \b
    Examples:
    * `api start`    -> Start App
    * `api start -r` -> Start App with reload
    """
    import uvicorn
    from api.settings import api_settings

    if print_debug_log:
        set_log_level_to_debug()

    logger.info("Starting Api")
    uvicorn.run(
        "api.app:app",
        host=api_settings.host,
        port=api_settings.port,
        reload=reload,
    )


@cli.command(short_help="Print Settings")
def settings(
    print_debug_log: bool = typer.Option(
        False, "-d", "--debug", help="Print debug logs."
    ),
):
    """
    \b
    Print Api settings.

    \b
    Examples:
    * `api settings`    -> Print Api settings
    * `api settings -d` -> Print Api settings with debug logs
    """
    from api.settings import api_settings

    if print_debug_log:
        set_log_level_to_debug()

    logger.info("Api Settings:")
    logger.info(api_settings.json(indent=2))
