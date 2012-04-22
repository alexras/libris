import os, sys, yaml, jinja2

def parser(cmd_name, subparsers, config):
    parser = subparsers.add_parser(
        cmd_name, help="generate BibTeX from a paper's metadata")
    parser.add_argument(
        "paper_folder_name",
        help="the target paper's folder within your paper pile")

    return parser

def command(config, paper_folder_name):
    papers_folder_root = os.path.expanduser(config.get("folders", "root"))

    metadata_path = os.path.join(papers_folder_root, paper_folder_name,
                                 "metadata.yaml")

    if not os.path.exists(metadata_path):
        print >>sys.stderr, "Can't find metadata file '%s'" % (metadata_path)
        return 1

    with open(metadata_path, 'r') as fp:
        metadata_file_contents = fp.read()

        try:
            metadata = yaml.load(metadata_file_contents)
        except yaml.scanner.ScannerError, e:
            print "Error loading metadata: %s" % (e)
            return 1

    jinja_env = jinja2.Environment(
        loader = jinja2.FileSystemLoader('templates'),
        trim_blocks = True,
        variable_start_string="<<",
        variable_end_string=">>")

    bibtex_template = jinja_env.get_template("bibtex.jinja2")

    print bibtex_template.render(
        paper_name = paper_folder_name,
        **metadata)

    return 0
