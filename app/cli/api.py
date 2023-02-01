"""The `api` cli
Usage:
    $ api --help
"""

import typer

from app.utils.log import logger, set_log_level_to_debug


app = typer.Typer(
    help="Api CLI",
    no_args_is_help=True,
    invoke_without_command=True,
    # https://typer.tiangolo.com/tutorial/exceptions/#disable-local-variables-for-security
    pretty_exceptions_show_locals=False,
)


@app.command(short_help="Start")
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
    Start api

    \b
    Examples:
    * `api start`    -> Start App
    * `api start -r` -> Start App with reload
    """
    import uvicorn
    from app.main import app_settings

    if print_debug_log:
        set_log_level_to_debug()

    logger.info("Starting App")
    uvicorn.run(
        "app.main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=reload,
    )


@app.command(short_help="Status")
def status(
    print_debug_log: bool = typer.Option(
        False, "-d", "--debug", help="Print debug logs."
    ),
):
    if print_debug_log:
        set_log_level_to_debug()

    logger.info("App Status")
