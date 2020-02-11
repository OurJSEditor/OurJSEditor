window.initEditorSettings = (function () {

var DEFAULT_SETTINGS = {
    wrap: true,
    useSoftTabs: true,
    tabSize: 4,
    showInvisibles: false,
    indentedSoftWrap: true, // Unimplimented
    highlightActiveLine: true, // Unimplimented
    highlightGutterLine: true, // Unimplimented
    displayIndentGuides: true, // Unimplimented
    useWorker: false,
    enableBasicAutocompletion: false,
    enableLiveAutocompletion: true,
    behavioursEnabled: true,
    wrapBehavioursEnabled: false,
    theme: "ace/theme/textmate",
    fontFamily: "'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace",
};

var POSSIBLE_OPTIONS = {
    wrap: {
        "Wrap": true,
        "Scroll": false
    },
    useSoftTabs: {
        "Tabs": false,
        "Spaces": true
    },
    tabSize: {
        label: "Tab Width",
        values: [2, 4, 8],
        type: "NUM_SELECT",
    },
    //TODO: Make BOOL_SELECT a checkbox?
    showInvisibles: {
        label: "Show Invisibles",
        type: "BOOL_SELECT",
        values: {
            "No": false,
            "Yes" : true
        }
    },

    useWorker: {
        label: "Error checking",
        type: "BOOL_SELECT",
        values: {
            "Off": false,
            "On" : true
        }
    },

    "enableBasicAutocompletion enableLiveAutocompletion": {
        label: "Auto completion",
        type: "BOOL_SELECT_MULTIKEY",
        values: {
            "Off" : [false, false],
            "With ctrl+space": [true, false],
            "Live": [false , true],
        }
    },
    //Double ", (, {, etc. KA screws with this a bit, which is why we create a new edit mode
    //wrapBehaviours are when you select a word, then press " and it puts quotes around the word
    "behavioursEnabled wrapBehavioursEnabled": {
        label: "Character pairs",
        type: "BOOL_SELECT_MULTIKEY",
        values: {
            "Off" : [false, false],
            "Match Pair": [true, false],
            "Pair & Selection": [true, true],
        },
    },

    theme: {
        label: "Theme",
        values: {
            "Textmate": "ace/theme/textmate",
            "Monokai": "ace/theme/monokai",
            "Tomorrow": "ace/theme/tomorrow",
            "Tomorrow Night": "ace/theme/tomorrow_night",
            "Chrome": "ace/theme/chrome",
            "Pastel on Dark": "ace/theme/pastel_on_dark",
            "Idle Fingers": "ace/theme/idle_fingers"
        },
    },
    fontFamily: {
        label: "Font",
        type: "TEXT_INPUT",
        placeholder: "fontFamily css"
    },
};

function parseValue (type, value) {
    switch (type) {
        case "BOOL_SELECT":
            return value === "true";
        case "NUM_SELECT":
            return parseFloat(value);
    }
    return value;
}

function loadOptions () {
    try {
        return JSON.parse(window.localStorage.editorSettings);
    }catch (e) {
        return DEFAULT_SETTINGS;
    }
}

return function (toggleButton, editors) {
    var currentOptions = loadOptions();

    var toggledOn = false;
    var container = createContainer();

    function editorSettingsUpdate () {
        var row = this.parentNode.parentNode;

        var option = row.dataset.editorOption;

        var type = this.dataset.optionType;

        if (type === "BOOL_SELECT_MULTIKEY") {
            var values = this.value.split(" ");
            var options = option.split(" ");

            for (var i = 0; i < values.length; i++) {
                for (var j = 0; j < editors.length; j++) {
                    editors[j].setOption(options[i], values[i] === "true");
                }

                currentOptions[options[i]] = values[i] === "true";
            }
        }else {
            var value = parseValue(type, this.value);

            for (var i = 0; i < editors.length; i++) {
                editors[i].setOption(option, value);
            }

            currentOptions[option] = value;
        }

        window.localStorage.editorSettings = JSON.stringify(currentOptions);
    }

    function createContainer () {
        var container = document.createElement("div");
        container.classList.add("editor-settings-container");
        var table = document.createElement("table");
        for (var option in POSSIBLE_OPTIONS) {
            if (!POSSIBLE_OPTIONS.hasOwnProperty(option)) continue;

            var optionObj = POSSIBLE_OPTIONS[option]
            var rowEl = document.createElement("tr");
            rowEl.dataset.editorOption = option;

            if (optionObj.label) {
                var tdEl = document.createElement("td");
                tdEl.innerHTML = optionObj.label;
                rowEl.appendChild(tdEl);

                if (optionObj.values) {
                    var selectEl = document.createElement("select");
                    selectEl.dataset.optionType = optionObj.type || "TEXT_SELECT";
                    selectEl.addEventListener("change", editorSettingsUpdate);
                    var selectedIndex;
                    if (optionObj.values instanceof Array) {
                        for (var i = 0; i < optionObj.values.length; i++) {
                            var optionEl = document.createElement("option");
                            optionEl.value = optionObj.values[i];
                            optionEl.innerHTML = optionObj.values[i];
                            if (currentOptions[option] === optionObj.values[i]) {
                                selectedIndex = i;
                            }
                            selectEl.appendChild(optionEl);
                        }
                    }else if (typeof optionObj.values === "object") {
                        for (var key in optionObj.values) {
                            if (!optionObj.values.hasOwnProperty(key)) continue;

                            var optionEl = document.createElement("option");
                            optionEl.innerHTML = key;

                            if (optionObj.values[key] instanceof Array) {
                                //Then we're looking at a BOOL_SELECT_MULTIKEY
                                optionEl.value = optionObj.values[key].join(" ");

                                //This reduce handles checking if the current values for the ace options controlled by the multiselect
                                //  match the values for the current possible value for the multiselect
                                if (option.split(" ").reduce((acc, k, i) => acc && currentOptions[k] === optionObj.values[key][i], true)) {
                                    selectedIndex = selectEl.childElementCount;
                                }
                            }else {
                                optionEl.value = optionObj.values[key];
                                if (currentOptions[option] === optionObj.values[key]) {
                                    selectedIndex = selectEl.childElementCount;
                                }
                            }

                            selectEl.appendChild(optionEl);
                        }
                    }
                    selectEl.selectedIndex = selectedIndex;
                    rowEl.appendChild(document.createElement("td")).appendChild(selectEl);
                }else if (optionObj.type === "TEXT_INPUT"){
                    var inputEl = document.createElement("input");
                    inputEl.type = "text";
                    inputEl.placeholder = optionObj.placeholder;
                    inputEl.value = currentOptions[option];
                    inputEl.addEventListener("change", editorSettingsUpdate);
                    rowEl.appendChild(document.createElement("td")).appendChild(inputEl);
                }
            }else {
                for (var key in optionObj) {
                    if (!optionObj.hasOwnProperty(key)) continue;

                    var td = document.createElement("td");
                    var labelEl = document.createElement("label");
                    labelEl.innerHTML = key;
                    labelEl.setAttribute("for", "editor-settings-" + key.toLowerCase());
                    var inputEl = document.createElement("input");
                    inputEl.value = optionObj[key];
                    inputEl.type = "radio";
                    inputEl.id = "editor-settings-" + key.toLowerCase();
                    inputEl.dataset.optionType = "BOOL_SELECT";
                    inputEl.name = "editor-settings-" + option;
                    if (currentOptions[option] === optionObj[key]) {
                        inputEl.checked = true;
                    }
                    inputEl.addEventListener("change", editorSettingsUpdate);
                    td.appendChild(inputEl);
                    rowEl.appendChild(td).appendChild(labelEl);
                }
            }

            container.appendChild(table).appendChild(rowEl);
        }

        //Create a code beautify button:
        var beautify = document.createElement("button");
        beautify.textContent = "Beautify Code";
        beautify.addEventListener("click", function () {
            var beautifiersByMode = {
                "ace/mode/javascript": js_beautify,
                "ace/mode/html": html_beautify,
                "ace/mode/css": css_beautify
            }

            for (var i = 0; i < editors.length; i++) {
                var mode = editors[i].getSession().$modeId;

                var newCode = beautifiersByMode[mode](editors[i].getSession().getValue(), {
                    "indent_size": currentOptions.useSoftTabs ? currentOptions.tabSize : 1,
                    "indent_char": currentOptions.useSoftTabs ? " " : "\t",
                    "selector_separator_newline": false, //CSS only
                    "space_after_named_function": true, //JS only
                    "space_after_anon_function": true, //JS only
                });
                editors[i].getSession().setValue(newCode);
            }
        });
        container.appendChild(beautify);

        return container;
    }

    container.style.display = "none";

    toggleArrow = document.getElementById("editor-settings-arrow");
    toggleButton.addEventListener("click", function () {
        toggledOn = !toggledOn;
        if (toggledOn) {
            container.style.display = "block";
            toggleArrow.innerHTML = "&#x25BC;";
        }else {
            container.style.display = "none";
            toggleArrow.innerHTML = "&#x25B6;";
        }
    });

    for (var i = 0; i < editors.length; i++) {
        editors[i].setOptions(currentOptions);
    }

    return container;
};

})();
