import subprocess, shlex, utils

def parser(cmd_name, subparsers, config):
    parser = subparsers.add_parser(
        cmd_name, help="open a paper")
    parser.add_argument("paper_name", help="a valid paper name")

    return parser

def command(config, paper_name):
    """
    Open a paper in the user's configured viewer
    """

    paper_path = utils.paper_path(paper_name, config)

    if paper_path is None:
        return 1

    open_command = config.get("general", "viewer") + " %s" % (
        paper_path)

    subproc = subprocess.Popen(shlex.split(open_command))
    subproc.communicate()
