#!/usr/bin/env python3
from os import path
from datetime import datetime, timezone
import mimetypes
import argparse
import pathlib
import base64
import shutil
import sys
import os

import zipfile

PREAMBLE = '''
<!DOCTYPE html>
<html>
<style>
* {
    margin: 0;
    padding: 0;
    background: lightgrey;
    font-family: Consolas, "Inconsolata", Menlo, Monaco, Lucida Console, Liberation Mono, DejaVu Sans Mono, Bitstream Vera Sans Mono, Courier New, monospace, serif;
}
h1 {
    font-size: 4vw;
    text-align: center;
}
.imgbox {
    display: grid;
    height: 100%;
}
.center-fit {
    max-width: 100%;
    max-height: 99vh;
    margin: auto;
}

.preview-grid {
    display: grid;
    grid-template-columns: 1fr 2fr;
    row-gap: 10px;
}

.image_list > a > img {
    width: 20vw;
    vertical-align: middle;
}

.comic_page {
    font-size: 2.1vw;
    display: flex;
    justify-content: center; /* align horizontal */
    align-items: center; /* align vertical */
}
</style>
'''

INDEX_TEMPLATE = '''
<head>
    <meta charset=utf-8 />
    <title>{description}</title>
</head>
<body>
<h1 style="margin-bottom: 80px;">{description}</h1>
{imagelist}
</body>
</html>
'''

DEFAULT_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']


def dbg_p(*args, **kwargs):
    '''A debug-print function'''
    now = datetime.now().astimezone()
    print(now.isoformat(), *args, **kwargs, file=sys.stderr)


def clean_namelist(namelist, allowed_extensions=None, blocked_names=None):
    '''Cleans garbage files from the namelist returned by ZipFile.namelist().
    Builds a new `namelist` from the provided `namelist`, where each entry in
    the new `namelist` fulfills the following rules:

    1. Each entry must end in one of the suffixes present in the
       `allowed_extensions` parameter.
    2. Each entry must not contain any of the strings present in the
       `blocked_names` parameter.

    Note that all string comparisons are done case-insensitively by
    lowercasing all strings at comparison time.

    :param namelist: List of string names of files in a zipfile. Produced by
        `ZipFile.namelist()`
    :param allowed_extensions: List of strings. The returned list of filenames
        will contain only entries in `namelist` which end in a suffix present in
        `allowed_extensions`. Default is: `['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']`
    :param blocked_names: List of strings. The returned list of filenames will
        only contain entries in `namelist` which do not have any of the strings
        in `blocked_names` present within them. Default is: `['.DS_Store', 'Thumbs.db', '__MACOSX', 'desktop.ini']`
    '''
    if allowed_extensions is None:
        allowed_extensions = DEFAULT_IMAGE_EXTENSIONS
    if blocked_names is None:
        blocked_names = ['.DS_Store', 'Thumbs.db', '__MACOSX', 'desktop.ini']
    newnamelist = list()
    for x in namelist:
        skip = False
        for bad in blocked_names:
            if bad.lower() in x.lower():
                skip = True
        if skip: continue

        skip = True
        for req in allowed_extensions:
            if x.lower().endswith(req.lower()):
                skip = False
        if skip: continue

        newnamelist.append(x)
    return newnamelist


def build_filetree(source_path, suffix_allowlist=None):
    '''Returns a dictionary of strings to lists of strings. Each key is a path
    to a folder (P) on disk within source_path. Each value is a list of files
    within that path P. Each list of files will only contain files with
    suffixes present in the `suffix_allowlist` parameter. By default,
    suffix_allowlist is the following list: ::

        ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']

    Given a directory structure like the following: ::

        /
            a/
                foo.jpg
                b/
                    qux.bmp
            c/
                yah.tiff
                zap.png
            d/
                notfound.txt

    Calling `build_filetree('/')` would return a dictionary of the following: ::

        {
            'a': ['foo.jpg'],
            'a/b': ['qux.bmp'],
            'c': ['yah.tiff', 'zap.png']
        }
    '''
    if suffix_allowlist is None:
        suffix_allowlist = DEFAULT_IMAGE_EXTENSIONS
    desired_files = dict()
    for dirpath, _, files in os.walk(source_path):
        reltpth = dirpath.replace(source_path, '')
        reltpth = reltpth.lstrip('/')
        zfiles = list()
        for fs in files:
            for suffix in suffix_allowlist:
                if fs.lower().endswith(suffix):
                    zfiles.append(fs)
        if not zfiles: continue

        if not reltpth in desired_files:
            desired_files[reltpth] = list()
        desired_files[reltpth].extend(zfiles)
    return desired_files


def create_image_datauri(full_imagepath):
    '''Creates a data URI out of an image suitable to be used in the 'src'
    attribute of an HTML <img> tag, allowing for totally self-contained HTML
    documents. While a normal `<img>` tag would embed an image into an HTML
    page with a "src" param like this `<img src="./path_to_img.png">`, an image
    may be directly embedded into the HTML via a data URI in the "src" param
    containing the binary contents of the image but base64 encoded. This
    function is for creating said "data URIs".'''
    mtype, _ = mimetypes.guess_type(full_imagepath)
    b64data = None
    with open(full_imagepath, 'rb') as img:
        imgdata = img.read()
        b64data = base64.b64encode(imgdata).decode('utf-8')
    datauri = f'data:{mtype};charset=utf-8;base64,{b64data}'
    return datauri


def mirror_unzip_cbz(source_path, dest_path, maintain_existing_images=False, verbose=False):
    ''' Replicates a directory structure with CBZ files in it into a new
    location, but with the CBZ files expanded into directories with only the
    images from each CBZ. So if we have a `source_path` to a folder with the
    following contents: ::

        # source_path is '/foo'
        /foo/
            volume01.cbz
            volume02.zip
        # /foo/volume01.cbz contents
        issue01/img01.png
        issue01/img02.png
        issue02/img01.png
        # /foo/volume02.zip contents
        issue03/img01.png
        issue04/img01.png

    Then calling `mirror_unzip_cbz('/foo', '/bar')` (assuming `/bar` is an
    empty directory) will cause `/bar` to be populated as follows: ::

        # dest_path is '/bar', an empty directory to start with.
        # '/bar' will look as follows after running mirror_unzip_cbz()
        /bar/
            volume01/
                issue01/
                    img01.png
                    img02.png
                issue02/
                    img01.png
            volume02/
                issue03/
                    img01.png
                issue04/
                    img01.png
    '''
    if verbose:
        dbg_p(f"extracting cbz files from '{source_path}' into '{dest_path}'")
    # Get a directory structure of all folders with cbz files in them, as a
    # dictionary of strings, with key being relative path and value being list
    # of cbz files in that directory.
    # "relative path" is relative to the source_path, which will be the root
    # for all these relative paths.
    source_path = path.abspath(source_path)
    dest_path = path.abspath(dest_path)
    cbz_folders = build_filetree(source_path, suffix_allowlist=['.cbz', '.zip'])
    if verbose:
        for pth, files in cbz_folders.items():
            dbg_p(f"{pth}:")
            for f in files:
                dbg_p(f"\t{f}")

    # Actually create the mirrored directory structure, then create directories
    # for each zipfile, then unzip all images into the directory for each
    # zipfile.
    for reltpth, zfiles in cbz_folders.items():
        full_oldpath = path.join(source_path, reltpth)
        full_newpath = path.join(dest_path, reltpth)
        if verbose:
            dbg_p(f"\textracting cbz files from subdir '{full_oldpath}' into '{full_newpath}'")
        pathlib.Path(full_newpath).mkdir(parents=True, exist_ok=True)
        for zfname in zfiles:
            full_path_to_zf = path.join(full_oldpath, zfname)

            # We want the name of the folder where we'll put the images to be
            # the same as the name of the zipped file itself, but without the
            # file extension
            foldername_for_images = '.'.join(path.split(full_path_to_zf)[-1].split('.')[:-1])
            full_new_imgspath = path.join(full_newpath, foldername_for_images)
            if verbose:
                dbg_p(f"\t\tzfname               : {zfname}")
                dbg_p(f"\t\tfull path to zipfile : {full_path_to_zf}")
                dbg_p(f"\t\tfoldername_for_images: {foldername_for_images}")
                dbg_p(f"\t\tfull_new_imgspath    : {full_new_imgspath}")
            pathlib.Path(full_new_imgspath).mkdir(parents=True, exist_ok=True)
            zfp = zipfile.ZipFile(full_path_to_zf)
            for compr_img_path in clean_namelist(zfp.namelist()):
                # Ensure that we maintain the directory structure within the
                # zip file in addition to the files themselves.
                compr_img_dirname = path.dirname(compr_img_path)
                full_new_image_dirname = path.join(full_new_imgspath, compr_img_dirname)
                full_new_image_path = path.join(full_new_imgspath, compr_img_path)
                if verbose:
                    dbg_p(f"\t\t\tcompr_img_path         : {compr_img_path}")
                    dbg_p(f"\t\t\tcompr_img_dirname      : {compr_img_dirname}")
                    dbg_p(f"\t\t\tfull_new_image_dirname : {full_new_image_dirname}")
                    dbg_p(f"\t\t\tfull_new_image_path    : {full_new_image_path}")
                if maintain_existing_images:
                    if path.isfile(full_new_image_path):
                        continue

                pathlib.Path(full_new_image_dirname).mkdir(parents=True, exist_ok=True)
                # Have to manually copy only the file out of it's old location and into the new one.
                source = zfp.open(compr_img_path)
                target = open(full_new_image_path, 'wb')
                with source, target:
                    shutil.copyfileobj(source, target)


def mirror_images_directory(
    source_path,
    dest_path,
    maintain_existing_images=False,
    extensions_allowlist=None,
    verbose=False
):
    ''' Replicate a directory structure with images in it into a new location,
    but with only the images. By default copies files with the following
    extensions (modifiable via the 'extensions_allowlist' param): ::

        .jpg
        .jpeg
        .png
        .gif
        .bmp
        .tiff
    '''
    if verbose:
        dbg_p(f"copying images from '{source_path}' into '{dest_path}'")
    if extensions_allowlist is None:
        extensions_allowlist = DEFAULT_IMAGE_EXTENSIONS
    source_path = path.abspath(source_path)
    dest_path = path.abspath(dest_path)

    image_folders = build_filetree(source_path, suffix_allowlist=extensions_allowlist)

    for reltpth, imgfiles in image_folders.items():
        full_oldpath = path.join(source_path, reltpth)
        full_newpath = path.join(dest_path, reltpth)
        if verbose:
            dbg_p(f"\tcopying images from subdir '{full_oldpath}' into '{full_newpath}'")
        pathlib.Path(full_newpath).mkdir(parents=True, exist_ok=True)
        for imgfname in imgfiles:
            # existing image file
            full_path_to_imgf = path.join(full_oldpath, imgfname)

            full_new_image_path = path.join(full_newpath, imgfname)
            if maintain_existing_images:
                if path.isfile(full_new_image_path):
                    continue
            if full_new_image_path == full_path_to_imgf:
                dbg_p(
                    f"ERR: Cannot copy file {full_path_to_imgf} into itself; skipping copy operation"
                )
                continue
            with open(full_path_to_imgf,
                      'rb') as sourceimg, open(full_new_image_path, 'wb') as destimg:
                shutil.copyfileobj(sourceimg, destimg)


def create_comic_display_htmlfiles(source_path, embed_images=False, verbose=False):
    '''Finds directories with images in them, then creates "index.html" files
    in each directory which embed those images in alphanumeric order. Does not
    create an "overall" HTML file for listing and browsing all the folders of
    images.'''
    if verbose:
        dbg_p(
            "creating index.html files for viewing images like comic books, "
            f"based on image dirs in {source_path}",
        )
    image_folders = build_filetree(source_path, suffix_allowlist=DEFAULT_IMAGE_EXTENSIONS)
    ordered_keys = sorted(image_folders.keys())
    for idx in range(len(ordered_keys)):
        reltpth = ordered_keys[idx]
        imgfiles = image_folders[reltpth]
        full_dir_path = path.join(source_path, reltpth)
        if verbose:
            dbg_p(f"\tcreating index.html in folder '{full_dir_path}'")
        linefmt = '<div style="text-align:center;" class="imgbox"><img src="{}" style="margin-top: 40px;" class="center-fit"><p>{}</p></div>'
        make_image_url = lambda imgpath: imgpath
        if embed_images:
            make_image_url = lambda imgpath, fp=full_dir_path: create_image_datauri(
                path.join(fp, imgpath)
            )
        imghtml = "\n".join([linefmt.format(make_image_url(x), x) for x in imgfiles])
        # Link to the next directory of comics if there are more
        if idx < len(ordered_keys) - 1:
            relative_path_to_next = path.relpath(ordered_keys[idx + 1], reltpth)
            if verbose:
                dbg_p(
                    f"\tLinking from source '{reltpth}' to next '{ordered_keys[idx+1]}' via '{relative_path_to_next}'"
                )
            imghtml += f'\n<h1><a href="{relative_path_to_next}/">NEXT >></a></h1>'
        contents = PREAMBLE + INDEX_TEMPLATE.format(imagelist=imghtml, description=reltpth)
        with open(path.join(full_dir_path, 'index.html'), 'w+') as indexfile:
            indexfile.write(contents)


def create_comic_browse_htmlfiles(source_path, embed_images=False, verbose=False):
    '''Creates a "BROWSE_HERE.html" file at the top of source_path, which
    generates a kind of "overview" or "browsable list" page which links to all
    the other index.html files in subdirectories of source_path. '''
    if verbose:
        dbg_p(f"creating BROWSE_COMIC_HERE.html browsing comic pages at '{source_path}'",)

    outfoldername = path.split(source_path)[-1]
    prvgrid = '<div class="preview-grid">{preview_rows}</div>'
    linefmt = '''
        <a href="{folderpath}/" class="comic_page">
            {foldername}
        </a>
        <div class="image_list">
            <a href="{folderpath}/">{images}</a>
        </div>
    '''
    imgsfmt = '<img src="{}" loading="lazy">'

    def create_folderprev(foldername, imagefiles):
        imgpaths = imagefiles[:3]
        imgpaths = [path.join(foldername, x) for x in imgpaths]
        make_image_url = lambda imgpath: imgpath
        if embed_images:
            make_image_url = lambda imgpath: create_image_datauri(path.join(source_path, imgpath))
        imgshtml = '\n'.join([imgsfmt.format(make_image_url(x)) for x in imgpaths])
        folderpath = foldername
        foldername = foldername.replace('/', '/<br>')
        return linefmt.format(folderpath=folderpath, foldername=foldername, images=imgshtml)

    subdir_imgs = build_filetree(source_path, suffix_allowlist=DEFAULT_IMAGE_EXTENSIONS)

    rendered_rows = list()
    for k in sorted(subdir_imgs.keys()):
        foldername = k
        imagefiles = subdir_imgs[k]
        rendered_rows.append(create_folderprev(foldername, imagefiles))

    preview_rows = "\n".join(rendered_rows)
    preview_grid = prvgrid.format(preview_rows=preview_rows)
    browse_contents = PREAMBLE + INDEX_TEMPLATE.format(
        description=outfoldername, imagelist=preview_grid
    )
    with open(path.join(source_path, "BROWSE_COMIC_HERE.html"), 'w') as browse_file:
        browse_file.write(browse_contents)


def main():
    parser = argparse.ArgumentParser(
        description='''
        Create HTML files for browsing directories of images as though those
        directories represent comic books. Will also automatically expand .cbz
        files.
    '''
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        help='If set, logs additional information to stderr during execution'
    )
    parser.add_argument(
        '--source',
        required=True,
        type=str,
        help='''
            The source directory of images/cbz files, which will be used as the
            basis for the all-new directory with images and HTML files for
            viewing those images.
            '''
    )
    parser.add_argument(
        '--destination',
        required=True,
        type=str,
        help='''
            The destination directory to be filled with images and HTML files
            for viewing those images.
    '''
    )
    parser.add_argument(
        '--embed-images',
        action='count',
        help='''If specified, causes all images to be embedded into the generated
        HTML files as base64 encoded data URIs. Grows page size, but improves
        portability.'''
    )
    parser.add_argument(
        '--maintain-existing-images',
        action='count',
        help='''If provided, then images (in folders and CBZ files) will only
        be copied into the 'destination' directory if there isn't already a
        file with the same name in the destination directory. If an image file
        would be copied from source to destination, but it exists in
        destination already, then it is not copied if this argument is
        provided.
        '''
    )
    args = parser.parse_args()
    verbose = bool(args.verbose)
    source = path.abspath(args.source)
    dest = path.abspath(args.destination)
    embed_images = bool(args.embed_images)
    maintain_existing_images = bool(args.maintain_existing_images)

    mirror_unzip_cbz(
        source, dest, maintain_existing_images=maintain_existing_images, verbose=verbose
    )
    # If source and destination are the same folder, we'd end up opening the
    # same file in both read and write mode, and copying itself, which is bad
    # since it could corrupt or delete the image files.
    if source != dest:
        mirror_images_directory(
            source, dest, maintain_existing_images=maintain_existing_images, verbose=verbose
        )
    create_comic_display_htmlfiles(dest, embed_images=embed_images, verbose=verbose)
    create_comic_browse_htmlfiles(dest, embed_images=embed_images, verbose=verbose)


if __name__ == '__main__':
    main()
