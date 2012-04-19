paper-pile - Dead simple research paper organization
==========

I needed a simple way of taking notes on research papers, where I could store
papers in my existing Dropbox space, take formatted notes in a full-featured
text editor, and retrieve BibTeX references for papers easily. paper-pile is the
result.

Its functionality is pretty basic at this point, and will grow as my
requirements grow.

## Configuration

All configuration is specified in a config file, `~/.paperpilerc`.

Papers live in a folder. The folder doesn't have to have any special
properties, though I store my papers on Dropbox currently.

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

Add papers to your paper folder with `paper-pile add <file>`

## Requirements

A relatively recent version of Python and the following packages (all available
from PyPi):

* [argparse](http://pypi.python.org/pypi/argparse)
* [bottle](http://pypi.python.org/pypi/bottle/)
* [Jinja2](http://pypi.python.org/pypi/Jinja2/)
* [PyYAML](http://pypi.python.org/pypi/PyYAML/)
