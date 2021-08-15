#!/usr/bin/env python3

'''Creates index.html files for subfolders in the current directory. Works when run in the same directory as 
'''

from os import listdir, getcwd
from os.path import isfile, join


index_template = '''
<!DOCTYPE html>
<html>
<body>
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
            linefmt = '<div style="text-align:center";><img src="{}" style="width:100%; margin-top: 40px;"><p>{}</p></div>'
            imghtml = "\n".join([linefmt.format(x, x) for x in imgfiles])
            contents = index_template.format(imagelist=imghtml, description=thing)
            with open(join(full_path, "index.html"), 'w+') as indexfile:
                indexfile.write(contents)
            print('writing index file:', join(full_path, "index.html"))



if __name__ == '__main__':
    main()