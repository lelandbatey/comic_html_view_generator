#!/usr/bin/env python3


from os import listdir, getcwd
from os.path import isfile, join


preamble= '''
<!DOCTYPE html>
<html>
<style>
* {
    margin: 0;
    padding: 0;
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

    for thing in files:
        full_path = join(present_dir, thing)
        if not isfile(full_path):
            imgfiles = sorted(listdir(full_path))
            imgfiles = [x for x in imgfiles if '.jp' in x]
            linefmt = '<div style="text-align:center;" class="imgbox"><img src="{}" style="margin-top: 40px;" class="center-fit"><p>{}</p></div>'
            imghtml = "\n".join([linefmt.format(x, x) for x in imgfiles])
            contents = preamble+index_template.format(imagelist=imghtml, description=thing)
            with open(join(full_path, "index.html"), 'w+') as indexfile:
                indexfile.write(contents)
            print('writing index file:', join(full_path, "index.html"))



if __name__ == '__main__':
    main()
