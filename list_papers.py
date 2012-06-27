import os, sys

def parser(cmd_name, subparsers, config):
    parser = subparsers.add_parser(cmd_name, help="list all paper names "
                                   "(useful for shell completion)")

    return parser

def command(config):
    root_folder = os.path.expanduser(config.get("folders", "root"))

    print ' '.join((x for x in os.listdir(root_folder) if x[0] != '.'))

    return 0
