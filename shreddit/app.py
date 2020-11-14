"""This module contains script entrypoints for shreddit.
"""
import argparse
import yaml
import os
import sys
import pkg_resources
from appdirs import user_config_dir
from shreddit import default_config
from shreddit.shredder import Shredder
from shreddit.util import ShredditError


def main():
    parser = argparse.ArgumentParser(description="Command-line frontend to the shreddit library.")
    parser.add_argument("-c", "--config", help="Config file to use instead of the default shreddit.yml")
    parser.add_argument("-g", "--generate-configs", help="Write shreddit and praw config files to current directory.",
                        action="store_true")
    parser.add_argument("-u", "--user", help="User section's name from praw.ini if not default", default="default")
    parser.add_argument(
        "--ask-pass", action="store_true", help=(
            "Ask for the `password` entry interactively "
            "instead of reading it from the file")
    )
    args = parser.parse_args()

    if args.generate_configs:
        if not os.path.isfile("shreddit.yml"):
            print("Writing shreddit.yml file...")
            with open("shreddit.yml", "wb") as fout:
                fout.write(pkg_resources.resource_string("shreddit", "shreddit.yml.example"))
        if not os.path.isfile("praw.ini"):
            print("Writing praw.ini file...")
            with open("praw.ini", "wb") as fout:
                fout.write(pkg_resources.resource_string("shreddit", "praw.ini.example"))
        return

    config_dir = user_config_dir("shreddit/shreddit.yml")

    if args.config:
        config_filename = args.config
    elif os.path.exists(config_dir):
        config_filename = config_dir
    else:
        config_filename = "shreddit.yml"

    if not os.path.isfile(config_filename):
        print("No shreddit configuration file was found or provided. Run this script with -g to generate one.")
        return

    with open(config_filename) as fh:
        # Not doing a simple update() here because it's preferable to only set attributes that are "whitelisted" as
        # configuration options in the form of default values.
        user_config = yaml.safe_load(fh)
        for option in default_config:
            if option in user_config:
                default_config[option] = user_config[option]

    # higher prio than config
    if args.ask_pass:
        default_config['ask_pass'] = True

    try:
        shredder = Shredder(default_config, args.user)
        shredder.shred()
    except ShredditError as ex:
        print("Error - %s" % ex, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Shreddit aborted by user", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
