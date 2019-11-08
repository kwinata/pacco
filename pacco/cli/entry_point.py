import logging
import sys

from pacco.cli.commands.pacco import Pacco
from pacco.cli.commands.utils.output_stream import OutputStream


def run():
    """
    This method is being called by setup.py as the entry point.
    """
    logging.basicConfig(level=logging.INFO)
    Pacco('', OutputStream()).run(*sys.argv[1:])
