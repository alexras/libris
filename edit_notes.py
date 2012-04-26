import subprocess, utils, shlex, os, sys

def parser(cmd_name, subparsers, config):
    parser = subparsers.add_parser(cmd_name, help="edit the notes for a paper")
    parser.add_argument("paper_name", help="a valid paper name")

    return parser

def command(config, paper_name):
    """
    Edits the notes for a paper with the user's configured editor
    """

    paper_notes_path = utils.paper_notes_path(paper_name, config)

    if paper_notes_path is None:
        return 1

    edit_command = config.get("general", "editor") + " %s" % (
        paper_notes_path)

    subproc = subprocess.Popen(shlex.split(edit_command))
    subproc.communicate()

