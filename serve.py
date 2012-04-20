import os, sys, jinja2, yaml
import bottle

paper_metadata = {}

jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader('templates'),
                               trim_blocks = True)

@bottle.route("/")
def list_papers():
    template = jinja_env.get_template("list_papers.jinja2")
    return template.render(paper_metadata = paper_metadata)

@bottle.route('/static/:path#.+#', name='static')
def static(path):
    return bottle.static_file(path, root=os.path.join("templates", "static"))

def parser(cmd_name, subparsers):
    parser = subparsers.add_parser(cmd_name, help="launch the paper-pile web UI")
    parser.add_argument("--port", "-p", help="the port on which the web UI "
                        "should run", default=8080)
    return parser

def command(config, port):
    root_folder = os.path.expanduser(config.get("folders", "root"))

    print "Collecting paper metadata ..."

    for dirpath, dirnames, filenames in os.walk(root_folder):
        if "metadata.yaml" in filenames:
            meta_filename = os.path.join(dirpath, "metadata.yaml")
            paper_name = os.path.basename(dirpath)

            with open(meta_filename, 'r') as fp:
                paper_metadata[paper_name] = yaml.load(fp.read())
                paper_metadata[paper_name]["filename"] = os.path.join(
                    dirpath, "%s.pdf" % (paper_name))

    bottle.run(host='localhost', port=port)
