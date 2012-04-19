paper-pile - Dead simple research paper organization
==========

I needed a simple way of taking notes on research papers, where I could store
papers in my existing Dropbox space, take formatted notes in a full-featured
text editor, and retrieve BibTeX references for papers easily. paper-pile is the
result.

Its functionality is pretty basic at this point, and will grow as my
requirements grow.

## Architecture

Your paper pile lives in a folder, called the _root_ folder. This folder
doesn't have to have any special properties, though I store my papers on
Dropbox currently.

Each paper is stored in a folder within the root folder along with its notes
and metadata. An empty notes and metadata file are created when the paper is
added to the paper pile. The name of the paper's folder (which defaults to the
paper's filename but can be any unique name you want) is used as an identifier
for the paper during all subsequent operations on that paper.

## Configuration

All configuration is specified in a config file, `~/.paperpilerc`.

Here's an example configuration file:

```ini
[folders]
root: ~/Dropbox/Papers

[notes]
renderer: redcarpet
extension: md

[webui]
port: 9494
```

* `folders/root`: the root folder in which your papers will be stored
* `notes/renderer`: the application that the web UI will use to render your
notes
* `notes/extension`: the file extension that will be given to the file
containing your notes
* `webui/port`: the port number that paper-pile's web UI will run in

## How to Use

Add papers to your paper pile with `paper-pile add <file>`; optionally, specify
the paper's name within the pile with the `--folder_name`/`-n` flag. The
paper's name defaults to the name of its file, and must be unique.

To generate BibTeX based on a paper's metadata, run
`paper-pile bibtex <paper name>`

**More commands coming soon**

## Requirements

A relatively recent version of Python and the following packages (all available
from PyPi):

* [argparse](http://pypi.python.org/pypi/argparse)
* [bottle](http://pypi.python.org/pypi/bottle/)
* [Jinja2](http://pypi.python.org/pypi/Jinja2/)
* [PyYAML](http://pypi.python.org/pypi/PyYAML/)
