#!/bin/bash

ace_files=("ace.js" "ext-searchbox.js" "mode-css.js" "mode-javascript.js" "worker-css.js" "worker-javascript.js" "ext-language_tools.js" "mode-html.js" "worker-html.js" "theme-textmate.js" "theme-monokai.js" "theme-tomorrow.js" "theme-tomorrow_night.js" "theme-chrome.js" "theme-pastel_on_dark.js" "theme-idle_fingers.js")

for ace_file in ${ace_files[*]};
do
    curl -o $ace_file https://cdn.jsdelivr.net/npm/ace-builds@1.4.7/src-min-noconflict/$ace_file
done
