#!/usr/bin/env python3

from os import listdir, getcwd, walk
from os.path import isfile, join, split, abspath, relpath
from pathlib import Path
import shutil
import sys

import zipfile

preamble = '''
<!DOCTYPE html>
<html>
<style>
* {
    margin: 0;
    padding: 0;
    background: lightgrey;
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

.preview-grid  * {
    /* border: 1px solid red; */
}

.image_list > a > img {
    width: 20vw;
    vertical-align: middle;
}

.comic_page {
    font-size: 3vw;
    display: flex;
    justify-content: center; /* align horizontal */
    align-items: center; /* align vertical */
}
.comic_page > a {
    vertical-align: middle;
}
</style>
<body>
'''

index_template = '''
<h1 style="margin-bottom: 80px;">{description}</h1>
{imagelist}
</body>
</html>
'''


def clean_namelist(namelist, allowed_extensions=None, blocked_names=None):
    '''Cleans garbage files from the namelist returned by ZipFile.namelist()'''
    if allowed_extensions is None:
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    if blocked_names is None:
        blocked_names = ['.DS_Store', 'Thumbs.db', '__MACOSX', 'desktop.ini']
    namelist = [x for x in namelist if not '__MACOSX' in x]
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
    if suffix_allowlist is None:
        suffix_allowlist = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    desired_files = dict()
    for dirpath, _, files in walk(source_path):
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


def mirror_unzip_cbz(source_path, dest_path):
    ''' Replicates a directory structure with CBZ files in it into a new
    location, but with the cbz files expanded into directories with images. '''
    # Get a directory structure of all folders with cbz files in them, as a
    # dictionary of strings, with key being relative path and value being list
    # of cbz files in that directory.
    # "relative path" is relative to the source_path, which will be the root
    # for all these relative paths.
    source_path = abspath(source_path)
    dest_path = abspath(dest_path)
    print(source_path, dest_path)
    cbz_folders = build_filetree(source_path, suffix_allowlist=['.cbz', '.zip'])
    #cbz_folders = dict()
    #for dirpath, _, files in walk(source_path):
    #    reltpth = dirpath.replace(source_path, '')
    #    reltpth = reltpth.lstrip('/')
    #    zfiles = list()
    #    for fs in files:
    #        for suffix in ['.cbz', '.zip']:
    #            if fs.lower().endswith(suffix):
    #                zfiles.append(fs)
    #    if not zfiles: continue

    #    if not reltpth in cbz_folders:
    #        cbz_folders[reltpth] = list()
    #    cbz_folders[reltpth].extend(zfiles)

    # Actually create the mirrored directory structure, then create directories
    # for each zipfile, then unzip all images into the directory for each
    # zipfile.
    for reltpth, zfiles in cbz_folders.items():
        full_oldpath = join(source_path, reltpth)
        full_newpath = join(dest_path, reltpth)
        # print('source_path', source_path)
        # print('dest_path', dest_path)
        # print('reltpth', reltpth)
        # print('full_oldpath', full_oldpath)
        # print('full_newpath', full_newpath)
        # print("creating folder for expanded chapters:", full_newpath, "from", full_oldpath)
        # print()
        Path(full_newpath).mkdir(parents=True, exist_ok=True)
        for zfname in zfiles:
            full_path_to_zf = join(full_oldpath, zfname)
            # print("\tfor compressed file:", zfname)
            # print("\tat:", full_path_to_zf)

            # We want the name of the folder where we'll put the images to be
            # the same as the name of the zipped file itself, but without the
            # file extension
            foldername_for_images = '.'.join(split(full_path_to_zf)[-1].split('.')[:-1])
            full_new_imgspath = join(full_newpath, foldername_for_images)
            # print("\tcreating folder to house comic images:", full_new_imgspath)
            Path(full_new_imgspath).mkdir(parents=True, exist_ok=True)
            zfp = zipfile.ZipFile(full_path_to_zf)
            for compr_img_path in clean_namelist(zfp.namelist()):
                compr_img_name = split(compr_img_path)[-1]
                full_new_image_path = join(full_new_imgspath, compr_img_name)
                # print('\t\textracting', compr_img_name, 'to directory', full_new_imgspath)
                # print('\t\tnew file at', full_new_image_path)

                # Have to manually copy only the file out of it's old location and into the new one.
                source = zfp.open(compr_img_path)
                target = open(full_new_image_path, 'wb')
                with source, target:
                    shutil.copyfileobj(source, target)


def create_comic_display_htmlfiles(source_path):
    '''Finds directories with images in them, then creates "index.html" files
    in each directory which embed those images in alphanumeric order. Does not
    create an "overall" HTML file for listing and browsing all the folders of
    images.'''
    image_folders = build_filetree(source_path, suffix_allowlist=['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'])
    ordered_keys = sorted(image_folders.keys())
    print(ordered_keys)
    for idx in range(len(ordered_keys)):
        reltpth = ordered_keys[idx]
        print(reltpth)
        imgfiles = image_folders[reltpth]
        full_path = join(source_path, reltpth)
        linefmt = '<div style="text-align:center;" class="imgbox"><img src="{}" style="margin-top: 40px;" class="center-fit"><p>{}</p></div>'
        imghtml = "\n".join([linefmt.format(x, x) for x in imgfiles])
        # Link to the next directory of comics if there are more
        if idx < len(ordered_keys) - 1:
            relative_path_to_next = relpath(reltpth, ordered_keys[idx])
            imghtml += f'\n<h1><a href="../{relative_path_to_next}/">NEXT >></a></h1>'
        contents = preamble + index_template.format(imagelist=imghtml, description=reltpth)
        print(join(full_path, "index.html"))
        with open(join(full_path, 'index.html'), 'w+') as indexfile:
            indexfile.write(contents)


def create_comic_browse_htmlfiles(source_path):
    '''Creates a "BROWSE_HERE.html" file at the top of source_path, which
    generates a kind of "overview" or "browsable list" page which links to all
    the other index.html files in subdirectories of source_path. '''

    outfoldername = split(source_path)[-1]
    prvgrid = '<div class="preview-grid">{preview_rows}</div>'
    linefmt = '<div class="comic_page"><a href="{foldername}/">{foldername}</a></div><div class="image_list"><a href="{foldername}/">{images}</a></div>'
    imgsfmt = '<img src="{}" loading="lazy">'

    def create_folderprev(foldername, imagefiles):
        imgpaths = imagefiles[:3]
        imgpaths = [join(foldername, x) for x in imgpaths]
        imgshtml = '\n'.join([imgsfmt.format(x) for x in imgpaths])
        return linefmt.format(foldername=foldername, images=imgshtml)

    subdir_imgs = build_filetree(source_path, suffix_allowlist=['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'])

    rendered_rows = list()
    for k in sorted(subdir_imgs.keys(), key=lambda x: split(x)[-1]):
        foldername = k
        imagefiles = subdir_imgs[k]
        rendered_rows.append(create_folderprev(foldername, imagefiles))

    preview_rows = "\n".join(rendered_rows)
    preview_grid = prvgrid.format(preview_rows=preview_rows)
    browse_contents = preamble + index_template.format(description=outfoldername, imagelist=preview_grid)
    with open(join(source_path, "BROWSE_COMIC_HERE.html"), 'w') as browse_file:
        browse_file.write(browse_contents)
    print("Writing browsing file: BROWSE_COMIC_HERE.html")


def main():
    present_dir = getcwd()
    files = sorted(listdir(present_dir))
    files = [x for x in files if x[0] != '.']
    print(files)

    subdir_imgs = dict()

    # Generate an index file for each directory, with that index file showing
    # the images in the folder in alphanumeric order (001.jpg then 002.jpg then
    # 003.png, etc).
    print("Writing index files: ", end="")
    for idx in range(len(files)):
        thing = files[idx]
        full_path = join(present_dir, thing)
        if not isfile(full_path):
            imgfiles = sorted(listdir(full_path))
            imgfiles = [x for x in imgfiles if '.jp' in x]
            linefmt = '<div style="text-align:center;" class="imgbox"><img src="{}" style="margin-top: 40px;" class="center-fit"><p>{}</p></div>'
            imghtml = "\n".join([linefmt.format(x, x) for x in imgfiles])
            if idx < len(files) - 1:
                imghtml += f'\n<h1><a href="../{files[idx+1]}/">NEXT >></a></h1>'
            contents = preamble + index_template.format(imagelist=imghtml, description=thing)
            with open(join(full_path, "index.html"), 'w+') as indexfile:
                indexfile.write(contents)
            print(join(thing, "index.html") + ' ', end='')
            subdir_imgs[thing] = imgfiles
    print()

    # Generate an HTML file in the current directory which will show a kind of
    # "preview" of all the directories. Makes for nicer browsing.

    curfoldername = split(present_dir)[-1]
    prvgrid = '<div class="preview-grid">{preview_rows}</div>'
    linefmt = '<div class="comic_page"><a href="{foldername}/">{foldername}</a></div><div class="image_list"><a href="{foldername}/">{images}</a></div>'
    imgsfmt = '<img src="{}" loading="lazy">'

    def create_folderprev(foldername, imagefiles):
        imgpaths = imagefiles[:3]
        imgpaths = [join(foldername, x) for x in imgpaths]
        imgshtml = '\n'.join([imgsfmt.format(x) for x in imgpaths])
        return linefmt.format(foldername=foldername, images=imgshtml)

    rendered_rows = list()
    for k in sorted(subdir_imgs.keys()):
        foldername = k
        imagefiles = subdir_imgs[k]
        rendered_rows.append(create_folderprev(foldername, imagefiles))

    preview_rows = "\n".join(rendered_rows)
    preview_grid = prvgrid.format(preview_rows=preview_rows)
    browse_contents = preamble + index_template.format(description=curfoldername, imagelist=preview_grid)
    with open(join(present_dir, "BROWSE_COMIC_HERE.html"), 'w') as browse_file:
        browse_file.write(browse_contents)
    print("Writing browsing file: BROWSE_COMIC_HERE.html")


if __name__ == '__main__':
    # main()
    source_path = "./comic_html_view_generator/JoJo_manga"
    dest_path = "./comic_html_view_generator/DELETEPLS"
    mirror_unzip_cbz(source_path, dest_path)
    create_comic_display_htmlfiles(dest_path)
    create_comic_browse_htmlfiles(dest_path)
