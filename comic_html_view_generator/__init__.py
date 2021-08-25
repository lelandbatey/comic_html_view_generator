'''
comic_html_view_generator is a command-line tool and library for creating
static HTML files for viewing comic books. Given a directory with images or
.cbz files in it, it'll create HTML files which embed those images in order,
and an overall "browse all the comics here" HTML page which will list all the
comics books which have had a readable HTML file generated from them.
'''

from .chvg import (
    create_comic_display_htmlfiles,
    create_comic_browse_htmlfiles,
    build_filetree,
    clean_namelist,
    create_image_datauri,
    mirror_unzip_cbz,
    mirror_images_directory,
)
