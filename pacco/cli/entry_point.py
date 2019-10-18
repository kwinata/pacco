import sys

from pacco.cli.command_manager import main


def run():
    """
    This method is being called by setup.py as the entry point.
    """
    main(sys.argv[1:])
