import os, sys, jinja2, yaml, urllib, subprocess, signal, utils
import datetime
import shutil
import time

import bottle

paper_metadata = {}
root_folder = None
notes_renderer = None
notes_extension = None

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

CONF = None

jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(
        os.path.join(SCRIPT_PATH, 'templates')),
    trim_blocks = True)


def migrate_metadata():
    print "Applying any pending metadata migrations ..."

    for paper_name in os.listdir(root_folder):
        paper_dir = os.path.join(root_folder, paper_name)

        # If there are non-directories in the root folder, ignore them
        if not os.path.isdir(paper_dir):
            continue

        metadata_file = os.path.join(paper_dir, 'metadata.yaml')

        # If the directory doesn't have a metadata file, skip it
        if not os.path.exists(metadata_file):
            continue

        with open(metadata_file, 'r') as fp:
            metadata = yaml.load(fp.read())

        metadata_modified = False

        # If the metadata file doesn't have a 'date-added' field, set
        # 'date-added' to the creation date of the directory
        if 'date-added' not in metadata:
            creation_date = datetime.datetime.fromtimestamp(
                os.stat(paper_dir).st_ctime).strftime("%Y-%m-%d")

            metadata_modified = True

            metadata['date-added'] = creation_date

        # Rewrite migrated metadata to file if modifications are needed
        if metadata_modified:
            print 'Migrating ' + paper_name

            shutil.copy(metadata_file, os.path.join(
                paper_dir, 'metadata.yaml.backup' + time.strftime('%Y-%m-%d')))

            with open(metadata_file, 'w') as fp:
                yaml.dump(metadata, fp)

def grab_metadata():
    global paper_metadata

    print "Collecting paper metadata ..."

    paper_metadata = {}

    for dirpath, dirnames, filenames in os.walk(root_folder):
        if "metadata.yaml" in filenames:
            meta_filename = os.path.join(dirpath, "metadata.yaml")
            paper_name = os.path.basename(dirpath)

            with open(meta_filename, 'r') as fp:
                paper_metadata[paper_name] = yaml.load(fp.read())

@bottle.post('/reload')
def reload_metadata():
    grab_metadata()
    bottle.redirect('/')

@bottle.post('/edit_metadata/:paper_name#.+#')
def edit_metadata(paper_name):
    global CONF, paper_metadata

    field_name = bottle.request.forms.get('field_name')
    value = bottle.request.forms.get('new_value')

    # Locate the paper in question
    metadata_path = utils.paper_metadata_path(paper_name, CONF)

    print metadata_path

    if metadata_path is None:
        raise bottle.HTTPError()

    # Load YAML data from the paper's metadata file
    with open(metadata_path, 'r') as fp:
        metadata = yaml.load(fp.read())

    # If you're changing author names, make the new value a comma-delimited
    # list. Otherwise, it can safely be a string

    if field_name == "authors":
        metadata[field_name] = [str(x).strip() for x in value.split(',')]
    else:
        metadata[field_name] = value

    # Re-write the new metadata
    with open(metadata_path, 'w') as fp:
        yaml.safe_dump(metadata, fp, encoding="utf-8")

    # Update the metadata cache
    paper_metadata[paper_name] = metadata

    return value

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
        cmd_name, help="launch the libris web UI")
    parser.add_argument("--port", "-p", help="the port on which the web UI "
                        "should run", default=int(config.get("webui", "port")))
    return parser

def command(config, port):
    global root_folder, notes_renderer, notes_extension, CONF
    CONF = config

    root_folder = os.path.expanduser(config.get("folders", "root"))
    notes_renderer = config.get("notes", "renderer")
    notes_extension = config.get("notes", "extension")

    migrate_metadata()
    grab_metadata()

    bottle.debug(True)
    bottle.run(host='localhost', port=port)
