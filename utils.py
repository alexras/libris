import os, sys

def paper_folder(paper_name, config):
    root_folder = os.path.expanduser(config.get("folders", "root"))

    return os.path.join(root_folder, paper_name)

def folder_exists(folder):
    return os.path.exists(folder) and os.path.isdir(folder)

def paper_metadata_path(paper_name, config):
    this_paper_folder = paper_folder(paper_name, config)

    if not folder_exists(this_paper_folder):
        print("Invalid paper name '%s'" % (paper_name), file=sys.stderr)
        return None

    metadata_path = os.path.join(this_paper_folder, "metadata.yaml")

    if not os.path.exists(metadata_path):
        print("Can't find paper metadata file '%s'" % (
            metadata_path), file=sys.stderr)
        return None
    else:
        return metadata_path

def paper_notes_path(paper_name, config):
    this_paper_folder = paper_folder(paper_name, config)

    if not folder_exists(this_paper_folder):
        print("Invalid paper name '%s'" % (paper_name), file=sys.stderr)
        return None

    notes_path = os.path.join(this_paper_folder, "notes." + config.get(
            "notes", "extension"))

    if not os.path.exists(notes_path):
        print("Can't find paper notes file '%s'" % (
            notes_path), file=sys.stderr)
        return None
    else:
        return notes_path

def paper_path(paper_name, config, allow_nonexistent = False):
    this_paper_folder = paper_folder(paper_name, config)

    if not folder_exists(this_paper_folder) and not allow_nonexistent:
        print("Invalid paper name '%s'" % (paper_name), file=sys.stderr)
        return None

    paper_path = os.path.join(this_paper_folder, "%s.pdf" % (paper_name))

    if not os.path.exists(paper_path) and not allow_nonexistent:
        print("Can't find paper file '%s'" % (paper_path), file=sys.stderr)
        return None
    else:
        return paper_path

def forbidden_chars(paper_name):
    """
    Returns the first forbidden character that appears in the paper name, or
    None if no forbidden characters are encountered
    """

    # So that bash completion doesn't get sad, paper names can't contain a
    # quote, an ampersand or a pipe
    forbidden_characters = ["'", '"', "&", "<", ">", "|"]

    for character in forbidden_characters:
        if paper_name.find(character) != -1:
            return character

    return None




