import utils, os, sys, shutil

def parser(cmd_name, subparsers, config):
    parser = subparsers.add_parser(cmd_name, help="change a paper's name")
    parser.add_argument("old_name", help="the paper's old name")
    parser.add_argument("new_name", help="the paper's new name "
                        "(must not be an existing name)")

    return parser

def command(config, old_name, new_name):
    root_folder = os.path.expanduser(config.get("folders", "root"))

    forbidden_char = utils.forbidden_chars(new_name)

    if forbidden_char is not None:
        print >>sys.stderr, "New paper name cannot contain %s" % (
            forbidden_char)
        return 1

    old_folder = utils.paper_folder(old_name, config)
    new_folder = utils.paper_folder(new_name, config)

    old_paper_path = utils.paper_path(old_name, config)
    new_paper_path = utils.paper_path(new_name, config,
                                      allow_nonexistent = True)

    if not os.path.exists(old_folder):
        return 1

    if os.path.exists(new_folder):
        print >>sys.stderr, "Paper '%s' already exists" % (new_name)
        return 1

    if old_paper_path is None:
        print >>sys.stderr, "Can't find a paper PDF within '%s'" % (old_folder)
        return 1

    shutil.move(old_folder, new_folder)
    shutil.move(os.path.join(new_folder, old_name + ".pdf"), new_paper_path)

    return 0
