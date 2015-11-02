import os
import requests
import shutil
import sys
import utils
import xml.etree.ElementTree as ET
import yaml

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

XML_NAMESPACES = {
    'tei': 'http://www.tei-c.org/ns/1.0'
}


def parser(cmd_name, subparsers, config):
    parser = subparsers.add_parser(
        cmd_name, help="add a paper to the papers folder")
    parser.add_argument("paper_path", help="a valid path to the paper")
    parser.add_argument(
        "--paper_name", "-n",
        help="the name of the paper's folder within the papers folder "
        "(default: <name of paper file>)", default=None)
    parser.add_argument('-d', '--doi', help="the document's DOI ID")

    return parser


def construct_name_from_xml(name_xml):
    first_name = name_xml.find("./tei:forename[@type='first']", XML_NAMESPACES)
    middle_name = name_xml.find("./tei:forename[@type='middle']", XML_NAMESPACES)
    last_name = name_xml.find("./tei:surname", XML_NAMESPACES)

    full_name = first_name.text

    if middle_name is not None:
        full_name += ' ' + middle_name.text

    full_name += ' ' + last_name.text

    return full_name


def construct_name_from_json(name_json):
    first_name = name_json.get('given', '')
    last_name = name_json.get('family', '')

    return first_name + ' ' + last_name


def get_metadata_from_doi(doi):
    print 'Retrieving metadata for DOI %s ...' % (doi)

    response = requests.get('http://api.crossref.org/works/%s' % (doi))

    if response.status_code != 200:
        print >>sys.stderr, 'Failed to retrieve metadata for DOI %s: %s' % (
            doi, response.text)
        return None

    doi_metadata = response.json()

    if doi_metadata['message-version'] != '1.0.0':
        print >>sys.stderr, 'Unable to parse CrossRef metadata version %s' % (
            doi_metadata['message-version'])
        return None

    metadata = {}

    try:
        metadata['title'] = ''.join(doi_metadata['message']['title'])

        if 'subtitle' in doi_metadata['message']:
            metadata['title'] += ': ' + ''.join(doi_metadata['message']['subtitle'])

        metadata['authors'] = map(construct_name_from_json, doi_metadata['message']['author'])

        # Pick the shortest available venue name
        venues = doi_metadata['message']['container-title']
        venues.sort(key=len)
        metadata['venue'] = venues[0]

        metadata['year'] = doi_metadata['message']['issued']['date-parts'][0][0]

        return metadata
    except KeyError:
        print >>sys.stderr, 'Unable to retrieve metadata for DOI %s' % (doi)
        return None


def get_metadata_from_grobid(paper_file, doi, config):
    # Attempt to extract metadata from GROBID
    host = config.get('grobid', 'host')
    port = config.get('grobid', 'port')

    header_process_response = requests.post(
        'http://%(host)s:%(port)s/processHeaderDocument' % {
            'host': host,
            'port': port
        },
        files={
            'input': open(paper_file, 'rb')
        })

    if header_process_response.status_code != 200:
        print >>sys.stderr, \
            'GROBID metadata lookup failed: error %d' % (header_process_response.status_code)
        return

    processed_headers_root = ET.fromstring(header_process_response.content)

    # If the document has a DOI ID, do a lookup based on that
    if doi is None:

        doi_node = processed_headers_root.find(
            "./tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:idno[@type='DOI']",
            XML_NAMESPACES)

        if doi_node is not None:
            doi = doi_node.text

    doi_metadata = None

    if doi is not None:
        doi_metadata = get_metadata_from_doi(doi)

    if doi_metadata is not None:
        return doi_metadata
    else:
        # Couldn't retrieve metadata via DOI, so we'll construct what we can
        # from the TEI content itself
        title_xpath = './tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title'
        authors_xpath = './tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/' + \
                        'tei:analytic/tei:author/tei:persName'

        title_node = processed_headers_root.find(title_xpath, XML_NAMESPACES)
        author_nodes = processed_headers_root.findall(authors_xpath, XML_NAMESPACES)

        metadata = {}

        if title_node is not None:
            metadata['title'] = title_node.text

        if author_nodes is not None:
            metadata['authors'] = map(construct_name_from_xml, author_nodes)

        return metadata


def command(config, paper_path, paper_name, doi):
    """
    Adds a paper to the libris folder by creating a directory for the paper
    and adding a copy of the paper, an empty notes file, and a default metadata
    file to that directory
    """

    if not os.path.exists(paper_path):
        print >>sys.stderr, "Can't find paper '%s'" % (paper_path)
        return 1

    if not os.path.isfile(paper_path):
        print >>sys.stderr, "'%s' is not a file" % (paper_path)
        return 1

    # Set paper name to the name of the file if unspecified
    if paper_name is None:
        paper_name = os.path.splitext(os.path.basename(paper_path))[0]

    # Convert spaces in paper name to underscores
    if paper_name.find(' ') != -1:
        paper_name = paper_name.replace(' ', '_')
        print >>sys.stderr, ("Converting spaces in paper name to underscores; "
                             "paper name is now '%s'" % (paper_name))

    forbidden_char = utils.forbidden_chars(paper_name)

    if forbidden_char is not None:
        print >>sys.stderr, "Paper name cannot contain %s" % (forbidden_char)
        return 1

    paper_basename = os.path.basename(paper_path)

    if paper_name is None:
        paper_name = os.path.splitext(paper_basename)[0]

    new_folder_path = utils.paper_folder(paper_name, config)

    if new_folder_path is None:
        return 1

    try:
        os.makedirs(new_folder_path)
    except os.error, e:
        print >>sys.stderr, "Can't create '%s': %s" % (new_folder_path, e)
        return 1

    new_paper_path = os.path.join(
        new_folder_path, "%s%s" %
        (paper_name, os.path.splitext(paper_basename)[1]))

    shutil.copyfile(paper_path, new_paper_path)

    notes_path = os.path.join(new_folder_path, "notes.%s" %
                              (config.get("notes", "extension")))

    with open(os.path.join(SCRIPT_PATH, "templates", "metadata.yaml"), 'r') as fp:
        metadata = yaml.load(fp.read())

    if config.has_section('grobid'):
        retrieved_metadata = get_metadata_from_grobid(new_paper_path, doi, config)

        print ''
        print 'Retrieved the following metadata:'
        print ''

        for key, value in retrieved_metadata.items():
            if type(value) == list:
                print key + ': ' + ', '.join(map(lambda x: '"' + unicode(x) + '"', value))
            else:
                print key + ': "' + str(value) + '"'

        metadata.update(retrieved_metadata)

    metadata_path = os.path.join(new_folder_path, "metadata.yaml")

    with open(metadata_path, 'w+') as fp:
        fp.write(yaml.safe_dump(metadata))

    open(notes_path, 'w').close()
    print '\nPaper added.'
    return 0
