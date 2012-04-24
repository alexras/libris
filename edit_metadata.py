import subprocess, utils, shlex, os, sys

def parser(cmd_name, subparsers, config):
    parser = subparsers.add_parser(cmd_name, help="edit a paper's metadata")
    parser.add_argument("paper_name", help="a valid paper name")

    return parser

def command(config, paper_name):
    """
    Edits a paper's metadata with the user's configured editor
    """

    paper_metadata_path = utils.paper_metadata_path(paper_name, config)

    if paper_metadata_path is None:
        return 1

    edit_command = config.get("general", "editor") + " %s" % (
        paper_metadata_path)

    subproc = subprocess.Popen(shlex.split(edit_command))
    subproc.communicate()

