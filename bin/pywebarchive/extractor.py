#!/usr/bin/env python3

"""Command-line webarchive extractor."""

import os
import sys
import optparse

# webbrowser is useful, but we can live without it
try: import webbrowser
except (ImportError): webbrowser = None

import webarchive


def main():
    """Extract the .webarchive file specified on the command line."""

    parser = optparse.OptionParser(
        usage="%prog [options] input_path.webarchive [output_path.html]",
        version="pywebarchive {0}".format(webarchive.__version__)
    )

    opt_group = parser.add_option_group("Extraction mode")
    opt_group.add_option("-s", "--single-file",
                         action="store_true", dest="single_file",
                         help="single file mode; embeds the page's non-HTML "
                              "content using data URIs. "
                              "This is usually slower and less efficient "
                              "than extracting such content to separate "
                              "files, so only use this if you know what "
                              "you're doing!")

    opt_group = parser.add_option_group("Post-processing actions")
    opt_group.add_option("-o", "--open-page",
                         action="store_true", dest="open_page",
                         help="open the extracted webpage when finished")

    options, args = parser.parse_args()
    if len(args) == 1:
        # Get the archive path from the command line
        archive_path = args[0]

        # Derive the output path from the archive path
        base, ext = os.path.splitext(archive_path)
        output_path = "{0}.html".format(base)

    elif len(args) == 2:
        # Get the archive and output paths from the command line
        archive_path, output_path = args

    else:
        # Print the correct usage and exit
        parser.print_usage(file=sys.stderr)
        sys.exit(1)

    # Extract the archive
    with webarchive.open(archive_path) as archive:
        archive.extract(output_path, options.single_file)

    if options.open_page and webbrowser:
        # Open the extracted page
        webbrowser.open(output_path)


if __name__ == "__main__":
    main()
