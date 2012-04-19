import os, sys, shutil

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

def parser(cmd_name, subparsers):
    parser = subparsers.add_parser(
        cmd_name, help="add a paper to the papers folder")
    parser.add_argument("paper_path", help="a valid path to the paper")
    parser.add_argument(
        "--folder_name", "-n",
        help="the name of the paper's folder within the papers folder "
        "(default: <name of paper>)", default=None)

    return parser

def command(config, paper_path, folder_name):
    """
    Adds a paper to the paper-pile folder by creating a directory for the paper
    and adding a copy of the paper, an empty notes file, and a default metadata
    file to that directory
    """

    if not os.path.exists(paper_path):
        print >>sys.stderr, "Can't find paper '%s'" % (paper_path)
        return 1

    if folder_name is None:
        folder_name = os.path.basename(os.path.splitext(paper_path)[0])

    papers_folder_root = os.path.expanduser(config.get("folders", "root"))

    new_folder_path = os.path.join(papers_folder_root, folder_name)

    try:
        os.makedirs(new_folder_path)
    except os.error, e:
        print >>sys.stderr, "Can't create '%s': %s" % (new_folder_path, e)
        return 1

    shutil.copyfile(
        os.path.join(SCRIPT_PATH, "templates", "metadata.yaml"),
        os.path.join(new_folder_path, "metadata.yaml"))
    shutil.copyfile(
        paper_path, os.path.join(new_folder_path, os.path.basename(paper_path)))

    notes_path = os.path.join(new_folder_path, "notes.%s" %
                              (config.get("notes", "extension")))

    open(notes_path, 'w').close()
