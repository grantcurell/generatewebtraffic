__author__ = "Grant Curell"
__copyright__ = "Do what you want with it"
__license__ = "GPLv3"

from argparse import ArgumentParser
from time import time, sleep
from random import randint
from selenium import webdriver
import logging
import yaml
import os
from multiprocessing.pool import Pool


def run(refresh_rate, jitter, duration, url_list, job_number):
    """
    Runs an instance of Selenium webdriver and browses to a URL.

    :param refresh_rate: int - See help text
    :param jitter: int - See help text.
    :param duration: int - See help text
    :param url_list: str - See help text
    :param job_number: str - Used in console output to differentiate between multiple threads.
    """

    browser = webdriver.Chrome()

    stop_time = time() + duration

    index = 0

    while time() + refresh_rate < stop_time:

        browser.get(url_list[index])

        next_jitter = randint(0, jitter)

        # If less than 50 we will make the jitter negative, otherwise it will be positive.
        plus_minus = randint(0, 100)

        if plus_minus < 50:
            if refresh_rate - next_jitter < 1:
                logging.debug("Jitter would be less than 1. Setting the jitter to 1.")
                next_refresh = 1
            else:
                next_refresh = refresh_rate - next_jitter
        else:
            if time() + refresh_rate + next_jitter > stop_time:
                logging.debug("Refresh rate plus jitter would exceed the stop time. Truncating jitter to launch "
                              "next refresh at stop time.")
                next_jitter = stop_time - time() - refresh_rate
            next_refresh = refresh_rate + next_jitter

        logging.debug("Next refresh will be in " + str(next_refresh) + " seconds.")

        sleep(next_refresh)

        browser.refresh()

        if index == len(url_list):
            index = 0

    browser.quit()


def main():
    parser = ArgumentParser(description="Uses Selenium to simulate users connecting to websites.")
    parser.add_argument('--url', metavar='URL', dest="url", type=str, required=False,
                        help='The url you would like the worker threads to browse to.')
    parser.add_argument('--yml', metavar='YML', dest="yml", type=str, required=False,
                        help='A YAML file with a configuration you would like to use. Defaults to config.yml.')
    parser.add_argument('--browsers', metavar='num_browsers', dest="number_of_browsers", type=int, required=False,
                        default=10, help='The number of browsers you want to use to test the Kibana dashboard.')
    parser.add_argument('--refresh-rate', metavar='seconds', dest="refresh_rate", type=int, required=False, default=20,
                        help='How often the browsers will refresh themselves after being opened.')
    parser.add_argument('--jitter', metavar='seconds', dest="jitter", type=int, required=False, default=10,
                        help='Controls randomness in the refresh rate up or down. For example if your refresh rate is '
                             '20 seconds and jitter is five, the refreshes will happen in between 15 and 25 seconds at '
                             'random. The default is 10 seconds. Set to 0 to remove jitter.')
    parser.add_argument('--duration', metavar='seconds', dest="duration", type=int, required=False, default=60,
                        help='The test duration measured in seconds. The default is 60.')
    parser.add_argument('--log-level', metavar='log_level', dest="log_level", required=False, type=str, default="info",
                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                        help='Set the log level used by the program. Options are debug, info, warning, error, and '
                             'critical.')
    parser.add_argument('--print-usage', dest="print_usage", required=False, action='store_true',
                        help='Show example usage.')

    args = parser.parse_args()

    usage = 'python run.py --url http://192.168.65.129:5601 --browsers 3 ' \
            '--refresh-rate 5 --jitter 1 --duration 20'
    yaml_config = None

    if args.yml and args.url:
        logging.error("You cannot use --url and --yml. You must use one or the other.")
        exit(0)

    if not args.url and not args.yml and not args.print_usage and not os.path.isfile("config.yml"):
        parser.print_help()
        print("\nEx: " + usage)
        exit(0)

    if args.yml:
        if not os.path.isfile(args.yml):
            logging.error(args.yml + " is not a valid file path. Are you sure you spelled everything correctly?")
        with open(args.yml, "r") as yaml_file:
            yaml_config = yaml.load(yaml_file, Loader=yaml.FullLoader)
    elif not args.url:
        if os.path.isfile("config.yml"):
            with open("config.yml", "r") as yaml_file:
                yaml_config = yaml.load(yaml_file, Loader=yaml.FullLoader)
        else:
            logging.error("You have not provided the arguments --url or --yml and the default configuration file"
                          " \'config.yml\' does not exist. Exiting.")

    if yaml_config and ("urls" not in yaml_config or len(yaml_config["urls"]) < 1):
        logging.error("Your YML file is missing the \'urls\' list. This is a required field.")
        exit(0)

    if args.print_usage:
        print(usage)
        exit(0)

    if args.refresh_rate <= 0:
        logging.critical("Refresh rate must be set to a positive value.")
        exit(0)

    if args.jitter < 0:
        logging.critical("Jitter cannot be less than 0.")
        exit(0)

    if args.duration <= 0:
        logging.critical("Duration must be set to a positive value.")
        exit(0)

    if args.log_level:
        if args.log_level == "debug":
            logging.basicConfig(level=logging.DEBUG)
        elif args.log_level == "info":
            logging.basicConfig(level=logging.INFO)
        elif args.log_level == "warning":
            logging.basicConfig(level=logging.WARNING)
        elif args.log_level == "error":
            logging.basicConfig(level=logging.ERROR)
        elif args.log_level == "critical":
            logging.basicConfig(level=logging.CRITICAL)
    else:
        logging.basicConfig(level=logging.INFO)

    # Begin main program execution

    logging.info("Beginning test.")
    logging.debug("Creating multithreaded pool to which we will issue jobs.")
    with Pool(processes=args.number_of_browsers) as pool:
        for i in range(args.number_of_browsers):
            logging.info("Starting job on browser #" + str(i))
            pool.apply_async(run, args=(args.refresh_rate, args.jitter, args.duration, args.url, str(i)))

        # This line is required. If you do not have this wait in place, apply_async will immediately issue all the
        # threads and then continue. The only thing after this is the end of the program which will cause
        # python to forcefully terminate the threads it just created without doing anything.
        sleep(args.duration + 10)


if __name__ == '__main__':
    main()
