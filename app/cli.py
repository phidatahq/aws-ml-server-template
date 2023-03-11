"""The `app` cli
Usage:
    $ app --help
"""
import typer

from api.utils.log import logger, set_log_level_to_debug


cli = typer.Typer(
    help="Run App commands",
    no_args_is_help=True,
    invoke_without_command=True,
    # https://typer.tiangolo.com/tutorial/exceptions/#disable-local-variables-for-security
    pretty_exceptions_show_locals=False,
)


@cli.command(short_help="Start")
def start(
    name: str = typer.Argument("Home", help="App Name", show_default=True),
    print_debug_log: bool = typer.Option(
        False, "--debug", "-d", help="Print debug logs."
    ),
):
    """
    \b
    Start ML App.

    \b
    Examples:
    * `app start`    -> Start ml/Home.py
    * `app start base`    -> Start ml/base.py
    """
    import sys

    from pathlib import Path
    import streamlit.web.cli as stcli

    if print_debug_log:
        set_log_level_to_debug()

    app_dir = Path(__file__).parent.resolve()
    app_file = app_dir.joinpath(f"{name}.py")
    if not app_file.exists() and not app_file.is_file():
        raise Exception(f"Invalid file {app_file}")

    logger.info(f"Starting App: {app_file}")
    sys.argv = [
        "streamlit",
        "run",
        str(app_file),
        "--server.port",
        "9095",
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
