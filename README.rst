comic_html_view_generator
=========================

comic_html_view_generator is a command-line tool and library for creating
static HTML files for viewing comic books. Given a directory with images or
.cbz files in it, it'll create HTML files which embed those images in order,
and an overall "browse all the comics here" HTML page which will list all the
comics books which have had a readable HTML file generated from them.

Installation
------------

Install this library via Pip: ::

    pip install comic-html-view-generator

Use with: ::

    python -m comic_html_view_generator --source <SOURCE_PATH> --destination <DESTINATION_PATH>

Assumptions
-----------

This tool makes many assumptions about your directory structure. It assumes
that in the directory tree provided, that all the images comprising a single
"comic book" will be collected into a single folder with all the images in it,
with no sub-folders. It's assumed that each image in an "image folder" is a
single "page" of that comic book. Additionally, it further assumes that the
alpha-numeric order (`00` comes before `01` comes before `0a`) of the names of
the images in each folder represent the "order" of each page in the comic book.

Usage
-----
Usage of the script is as follows: ::

    $ python -m comic_html_view_generator
    usage: comic_html_view_generator.py [-h] [-v] --source SOURCE --destination DESTINATION
                                        [--embed-images] [--maintain-existing-images]

    Create HTML files for browsing directories of images as though those directories
    represent comic books. Will also automatically expand .cbz files.

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         If set, logs additional information to stderr during execution
      --source SOURCE       The source directory of images/cbz files, which will be used as
                            the basis for the all-new directory with images and HTML files
                            for viewing those images.
      --destination DESTINATION
                            The destination directory to be filled with images and HTML
                            files for viewing those images.
      --embed-images        If specified, causes all images to be embedded into the
                            generated HTML files as base64 encoded data URIs. Grows page
                            size, but improves portability.
      --maintain-existing-images
                            If provided, then images (in folders and CBZ files) will only be
                            copied into the 'destination' directory if there isn't already a
                            file with the same name in the destination directory. If an
                            image file would be copied from source to destination, but it
                            exists in destination already, then it is not copied if this
                            argument is provided.

