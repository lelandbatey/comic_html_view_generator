#!/bin/bash

# Downloads all of One Punch Man the images. Requires the "link_grab.py" script here:
#    https://gist.github.com/lelandbatey/207664884c93c4fa7d7c
#
# Additionally, you may have to modify the above script so that it uses a more normal user-agent.

BASEURL="https://readonepunchman.online/manga/one-punch-man-chapter-"
MAX_CHAPTER=150
ORIGINAL_DIR="${PWD}"

for i in $(seq ${MAX_CHAPTER}); do
    cd "${ORIGINAL_DIR}"
    NEW_FOLDER=$(printf "onepunchman-chapter-%03d" "${i}")
    echo "creating directory ${NEW_FOLDER}"
    mkdir -p "${NEW_FOLDER}"
    cd "${NEW_FOLDER}"

    CHAPTER_URL="${BASEURL}${i}/"
    IMGS=$(link_grab "${CHAPTER_URL}" | grep 'jpg')
    if [[ "${IMGS}" == "" ]]; then
        CHAPTER_URL="${BASEURL}${i}-2/"
        IMGS=$(link_grab "${CHAPTER_URL}" | grep 'jpg')
    fi
    for img in ${IMGS}; do
        echo "wget ${img}"
        wget --continue --quiet "${img}"
    done
done
