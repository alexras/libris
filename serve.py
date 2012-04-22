import os, sys, jinja2, yaml, urllib, subprocess
import bottle

paper_metadata = {}
root_folder = None
notes_renderer = None
notes_extension = None

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(
        os.path.join(SCRIPT_PATH, 'templates')),
    trim_blocks = True)

@bottle.route("/")
def list_papers():
    template = jinja_env.get_template("list_papers.jinja2")
    return template.render(paper_metadata = paper_metadata)

@bottle.route("/view/:paper_name#.+#")
def view(paper_name):
    paper_name = paper_name.strip('/')
    if paper_name not in paper_metadata:
        return bottle.error(404)

    template = jinja_env.get_template("view_paper.jinja2")

    render_cmd = "%s %s" % (notes_renderer, os.path.join(
            root_folder, paper_name, "notes." + notes_extension))

    render_subproc = subprocess.Popen(render_cmd, shell=True,
                                      stdout=subprocess.PIPE)
    rendered_notes = render_subproc.communicate()[0].strip()

    return template.render(paper_info = paper_metadata[paper_name],
                           paper_name = paper_name,
                           rendered_notes = rendered_notes)

@bottle.route('/static/:path#.+#', name='static')
def static(path):
    return bottle.static_file(path, root=os.path.join(
            SCRIPT_PATH, "templates", "static"))

@bottle.route('/papers/:paper_name#.+#')
def papers(paper_name):
    paper_name = paper_name.strip('/')
    paper_pdf = "%s.pdf" % (paper_name)
    paper_path = os.path.join(paper_name, paper_pdf)
    print paper_pdf, paper_path, root_folder
    return bottle.static_file(paper_path, root=root_folder)

def parser(cmd_name, subparsers, config):
    parser = subparsers.add_parser(
        cmd_name, help="launch the paper-pile web UI")
    parser.add_argument("--port", "-p", help="the port on which the web UI "
                        "should run", default=int(config.get("webui", "port")))
    return parser

def command(config, port):
    global root_folder, notes_renderer, notes_extension

    root_folder = os.path.expanduser(config.get("folders", "root"))
    notes_renderer = config.get("notes", "renderer")
    notes_extension = config.get("notes", "extension")

    print "Collecting paper metadata ..."

    for dirpath, dirnames, filenames in os.walk(root_folder):
        if "metadata.yaml" in filenames:
            meta_filename = os.path.join(dirpath, "metadata.yaml")
            paper_name = os.path.basename(dirpath)

            with open(meta_filename, 'r') as fp:
                paper_metadata[paper_name] = yaml.load(fp.read())

    bottle.debug(True)
    bottle.run(host='localhost', port=port)
