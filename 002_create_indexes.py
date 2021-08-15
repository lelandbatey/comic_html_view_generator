#!/usr/bin/env python3


from os import listdir, getcwd
from os.path import isfile, join, split


preamble= '''
<!DOCTYPE html>
<html>
<style>
* {
    margin: 0;
    padding: 0;
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
    max-height: 100vh;
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

def main():
    present_dir = getcwd()
    files = listdir(present_dir)
    print(files)

    subdir_imgs = dict()

    # Generate an index file for each directory, with that index file showing
    # the images in the folder in alphanumeric order (001.jpg then 002.jpg then
    # 003.png, etc).
    print("Writing index files: ", end="")
    for thing in files:
        if thing[0] == '.': continue
        full_path = join(present_dir, thing)
        if not isfile(full_path):
            imgfiles = sorted(listdir(full_path))
            imgfiles = [x for x in imgfiles if '.jp' in x]
            linefmt = '<div style="text-align:center;" class="imgbox"><img src="{}" style="margin-top: 40px;" class="center-fit"><p>{}</p></div>'
            imghtml = "\n".join([linefmt.format(x, x) for x in imgfiles])
            contents = preamble+index_template.format(imagelist=imghtml, description=thing)
            with open(join(full_path, "index.html"), 'w+') as indexfile:
                indexfile.write(contents)
            print(join(thing, "index.html")+' ', end='')
            subdir_imgs[thing] = imgfiles
    print()

    # Generate an HTML file in the current directory which will show a kind of
    # "preview" of all the directories. Makes for nicer browsing.

    curfoldername = split(present_dir)[-1]
    prvgrid = '<div class="preview-grid">{preview_rows}</div>'
    linefmt = '<div class="comic_page"><a href="{foldername}">{foldername}</a></div><div class="image_list"><a href="{foldername}">{images}</a></div>'
    imgsfmt = '<img src="{}">'

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
    browse_contents = preamble+index_template.format(description=curfoldername, imagelist=preview_grid)
    with open(join(present_dir, "BROWSE_COMIC_HERE.html"), 'w') as browse_file:
        browse_file.write(browse_contents)
    print("Writing browsing file: BROWSE_COMIC_HERE.html")



if __name__ == '__main__':
    main()
