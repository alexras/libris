import utils
import os
import sys
import shutil


def parser(cmd_name, subparsers, config):
    parser = subparsers.add_parser(cmd_name, help='remove a paper')
    parser.add_argument('name', help="the paper's name")


def command(config, name):
    paper_folder = utils.paper_folder(name, config)

    if len(name.strip()) == 0:
        print >>sys.stderr, 'Must provide a paper name to remove'
        return 1

    if not os.path.exists(paper_folder):
        print >>sys.stderr, "No such paper '%s'" % (name)
        return 1

    shutil.rmtree(paper_folder)

    return 0
