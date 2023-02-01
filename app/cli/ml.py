"""The `ml` cli
Usage:
    $ ml --help
"""
from pathlib import Path

import typer

from app.utils.log import logger, set_log_level_to_debug


app = typer.Typer(
    help="Run ML Apps",
    no_args_is_help=True,
    invoke_without_command=True,
    # https://typer.tiangolo.com/tutorial/exceptions/#disable-local-variables-for-security
    pretty_exceptions_show_locals=False,
)


@app.command(short_help="Start")
def start(
    app_name: str = typer.Argument(..., help="App Name"),
    port: int = typer.Option(9095, "--port", "-p", help="Port", show_default=True),
    print_debug_log: bool = typer.Option(
        False, "--debug", "-d", help="Print debug logs."
    ),
):
    """
    \b
    Start ML Server

    \b
    Examples:
    * `app start base`    -> Start ml/base.py
    """
    import sys
    import streamlit.web.cli as stcli

    if print_debug_log:
        set_log_level_to_debug()

    app_dir = Path(__file__).parent.parent.resolve()
    app_file = app_dir.joinpath("ml", app_name + ".py")
    if not app_file.exists() and not app_file.is_file():
        raise Exception(f"Invalid file {app_file}")

    logger.info(f"Starting App: {app_file}")
    sys.argv = [
        "streamlit",
        "run",
        str(app_file),
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
        "--server.maxUploadSize",
        "100",
        "--runner.magicEnabled",
        "false",
    ]
    sys.exit(stcli.main())


@app.command(short_help="Status")
def status(
    print_debug_log: bool = typer.Option(
        False, "-d", "--debug", help="Print debug logs."
    ),
):
    if print_debug_log:
        set_log_level_to_debug()

    logger.info("App Status")
