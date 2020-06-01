#!/usr/bin/python


# run python -m main.py

import sys
import logging
from logging.handlers import RotatingFileHandler
from engine import ApplicationEngine
from controllers import OpencvImageController, ConsoleController, HeadlessController, SqliteController, FilesystemController
import argparse


TEST_FRAMES = [300, 1200, 1800, 2200, 2700, 3000, 3600, 4000, 4500]
# TEST_PLATES = ["WAX081", "XFG774", "1HG9TF", "WCW856", "ZPR916", "1FL2KF", "1JQ7RG","unknown", "AXZ074"]  # the last second is unknown

LOGFILE_NAME = 'rushdigital.log'

def main():
    logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)  # too many boto3 debug print
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(LOGFILE_NAME, maxBytes=512000, backupCount=20)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    message = "Rush Digital Programming Challenge"

    logger.info(message)

    parser = argparse.ArgumentParser(description=message)

    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run without the GUI image preview')

    args = parser.parse_args()

    run_headless = args.headless

    application_engine = ApplicationEngine()
    filesystem_controller = FilesystemController()
    sqlite_controller = SqliteController()

    if not run_headless:
        console_controller = ConsoleController()
        # interface_controller = OpencvImageController()
        # application_engine.register_controller(interface_controller)
    else:
        console_controller = HeadlessController()

    application_engine.register_controller(filesystem_controller)
    application_engine.register_controller(sqlite_controller)
    application_engine.register_controller(console_controller)
    application_engine.start()

    console_controller.run_main_loop()
    try:
        application_engine.join(10)
    except KeyboardInterrupt:
        pass

    if application_engine.dirty_exit:
        sys.exit(1)


if __name__ == "__main__":
    main()
