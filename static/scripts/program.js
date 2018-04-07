var jsEditor, htmlEditor, cssEditor;

var titleLabel;
var titleInput = document.createElement("input");
titleInput.setAttribute("maxlength", "45");
titleInput.setAttribute("id", "program-title");
titleInput.addEventListener("change", removeTitleInput);
titleInput.addEventListener("blur", removeTitleInput);
titleInput.addEventListener("keypress", function (e) {
    //If the enter or return key is pressed.
    if (e.which === 13) {
        removeTitleInput();
    }
});

function removeTitleInput () {
    if (titleInput.parentNode === null) return;
    titleLabel.innerText = titleInput.value;
    titleInput.parentNode.insertBefore(titleLabel, titleInput);
    titleInput.parentNode.removeChild(titleInput);
    if (programData.title !== titleLabel.innerText && !programData.new) {
        var req = new XMLHttpRequest();
        req.addEventListener("load", function (a) {
            //Something went wrong:
            if (this.status >= 400) {
                var contentType = this.getResponseHeader("content-type").toLowerCase();
                var outputMessage = "Program title updating failed";
                if (contentType.indexOf("json") > -1) {
                    console.log(JSON.parse(this.response));
                    outputMessage += " with the error message:\n\n" + JSON.parse(this.response).error;
                }else if (contentType.indexOf("html") > -1) {
                    outputMessage += "; a new window/tab with more information has been opened.";
                    window.open("data:text/html," + this.response, "_blank");
                }else {
                    outputMessage += ".";
                }
                alert(outputMessage);
            }
        });
        req.open("PATCH", "/api/program/" + programData.id)
        req.setRequestHeader("X-CSRFToken", csrf_token)
        req.send(JSON.stringify({ "title" : titleInput.value }))
    }
    programData.title = document.getElementById("program-title").innerText;
}

function deleteConfirm (event) {
    event.preventDefault();
    document.getElementById("backCover").style.display = "block";
    document.getElementById("deleteConfirm").style.display = "block";
    document.getElementById("backCover").addEventListener("click", closeConfirm);
}

function closeConfirm () {
    document.getElementById("backCover").style.display = "none";
    document.getElementById("deleteConfirm").style.display = "none";
    document.getElementById("backCover").removeEventListener("click", closeConfirm);
}

function deleteProgram () {
    var req = new XMLHttpRequest();
    req.addEventListener("load", function (a) {
        //Something went wrong:
        if (this.status >= 400) {
            var contentType = this.getResponseHeader("content-type").toLowerCase();
            var outputMessage = "Program deleting failed";
            if (contentType.indexOf("json") > -1) {
                console.log(JSON.parse(this.response));
                outputMessage += " with the error message:\n\n" + JSON.parse(this.response).error;
            }else if (contentType.indexOf("html") > -1) {
                outputMessage += "; a new window/tab with more information has been opened.";
                window.open("data:text/html," + this.response, "_blank");
            }else {
                outputMessage += ".";
            }
            alert(outputMessage);
        }else {
            window.location.href = "/user/" + programData.author.username;
        }
    })
    req.open("DELETE", "/api/program/" + programData.id);
    req.setRequestHeader("X-CSRFToken", csrf_token)
    req.send()
}

function runProgram (event) {
    if (event) {
        event.preventDefault();
    }

    //Insert JS
    var html = ace.edit("html-editor").getSession().getValue();
    html = html.replace(/\/\*\[OurJSEditor insert:(js|css)\]\*\//gi, function (comment, language, position, code) {
        return ace.edit(language.toLowerCase() + "-editor").getSession().getValue();
    })

    document.getElementById("preview").contentWindow.postMessage(html, "*");
}

function dateToString (d) {
    d = new Date(d);
    var currentYear = (new Date()).getFullYear();
    var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return months[d.getMonth()] + " " + d.getDate() + (currentYear === d.getFullYear() ? "" : ", " + d.getFullYear());
}

function createCommentTextbox (parent) {
    var com = document.createElement("div");
    var t = document.createElement("table");
    var textbox = document.createElement("textarea");
    var row = document.createElement("tr");
    var content = document.createElement("td");
    var buttons = document.createElement("td");
    var submit = document.createElement("a");

    submit.innerText = "Post";

    submit.addEventListener("click", function (e) {
        e.preventDefault();

        var req = new XMLHttpRequest();
        req.open("POST", "/api/program/" + programData.id + "/comment/new");
        req.setRequestHeader("X-CSRFToken", csrf_token)
        req.setRequestHeader("Content-Type", "application/json");
        req.addEventListener("load", function () {
            var data = JSON.parse(this.response);
            if (data && data.success) {
                if (parent) {
                    parent = {
                        "id": parent,
                    }
                }
                var commentObj = {
                    "content": textbox.value,
                    "replyCount": 0,
                    "depth": parent ? 1 : 0,
                    "program": {
                        "id": programData.id,
                    },
                    "originalContent": textbox.value,
                    "parent": parent,
                    "author": userData,
                    "edited": null,
                    "created": (new Date()).toISOString().replace(/\.\d\d\dZ/, "Z"),
                    "id": data.id,
                }

                if (parent) {
                    for (var i = 0; i < programData.comments.length; i++) {
                        if (programData.comments[i].id === parent.id) {
                            programData.comments[i].comments.push(commentObj);
                            programData.comments[i].replyCount ++;
                            var el = programData.comments[i].element.getElementsByClassName("show-hide-comments")[0];
                            el.innerText = el.innerText.replace(/\(\d+\)/, "(" + programData.comments[i].replyCount + ")")
                            break;
                        }
                    }
                }else {
                    programData.comments.push(commentObj);
                }


                var textBoxWrapper = textbox.parentElement.parentElement.parentElement.parentElement;

                //If we're adding a comment on a comment, and not a top-level comment
                if (textBoxWrapper.classList.contains("comment-comment")) {
                    //Insert the new comment before the textbox
                    document.getElementById("comment-wrap").insertBefore(displayComment(commentObj), textBoxWrapper);
                }else {
                    document.getElementById("comment-wrap").insertBefore(displayComment(commentObj), textBoxWrapper.nextSibling);
                }

                textbox.value = "";
            }else if (data && !data.success) {
                alert('Failed with error: ' + data.error);
            }
        });
        req.send(JSON.stringify({
            parent: parent,
            content: textbox.value,
        }));
    });

    buttons.appendChild(submit);

    com.classList.add("comment", "comment-adding");
    if (parent) {
        com.classList.add("comment-comment");
    }

    textbox.classList.add("comment-content")

    content.appendChild(textbox);
    com.appendChild(t).appendChild(row);
    row.appendChild(content);
    row.appendChild(buttons);
    return com;
};

//comment is a comment object
function unfoldComment (comment) {
    comment.element.parentElement.insertBefore(createCommentTextbox(comment.id), comment.element.nextSibling)
    for (var i = comment.comments.length-1; i >= 0; i--) {
        comment.element.parentElement.insertBefore(displayComment(comment.comments[i]), comment.element.nextSibling);
    }
    comment.unfolded = true;
    var el = comment.element.getElementsByClassName("show-hide-comments")[0];
    el.innerText = el.innerText.replace(/^Show/, "Hide");
};

function displayComment (comment) {
    var com = document.createElement("div");
    var t = document.createElement("table");
    var content = document.createElement("td");
    var author = document.createElement("td");
    var upperRow = document.createElement("tr");
    var lowerRow = document.createElement("tr");
    var link = document.createElement("a");
    var lowerRowLeft = document.createElement("td");

    com.classList.add("comment");
    com.setAttribute("id", "comment-" + comment.id);
    link.setAttribute("href", "/user/" + comment.author.username);
    author.classList.add("comment-author");

    content.classList.add("comment-content");
    content.setAttribute("colspan", 2);
    author.innerText = "Posted " + dateToString(comment.created) + " by ";
    link.innerText = comment.author.displayName;
    content.innerText = comment.content;

    lowerRow.classList.add("lower-row");

    if (comment.depth === 0) {
        comment.unfolded = false;

        var dropDown = document.createElement("a");
        dropDown.classList.add("show-hide-comments");
        dropDown.innerText = "Show Comment" + (comment.replyCount === 1 ? " (" : "s (") + comment.replyCount + ")";
        dropDown.addEventListener("click", function (e) {
            e.preventDefault();

            // If we're unfolded, fold back up
            if (comment.unfolded) {
                while (comment.element.nextElementSibling.classList.contains("comment-comment")) {
                    comment.element.parentElement.removeChild(comment.element.nextElementSibling);
                }
                comment.unfolded = false;
                var el = comment.element.getElementsByClassName("show-hide-comments")[0];
                el.innerText = el.innerText.replace(/^Hide/, "Show");
            //If we've already loaded comments
            }else if (comment.comments) {
                unfoldComment(comment);
            }else {
                var req = new XMLHttpRequest();
                req.open("GET", "/api/program/" + programData.id + "/comment/" + comment.id + "/comments");
                req.addEventListener("load", function () {
                    var data = JSON.parse(this.response);
                    if (data && data.success) {
                        comment.comments = data.comments;
                        comment.replyCount = data.comments.length; //Reset local value to the correct number
                        var el = comment.element.getElementsByClassName("show-hide-comments")[0];
                        el.innerText = el.innerText.replace(/\(\d+\)/, "(" + comment.replyCount + ")")

                        unfoldComment(comment);
                    }
                });
                req.send();
            }
        });
        lowerRowLeft.appendChild(dropDown);
        var spacer = document.createElement("span");
        spacer.style.width = "10px";
        spacer.style.display = "inline-block";
        lowerRowLeft.appendChild(spacer);
    }else {
        com.classList.add("comment-comment");
    }

    if (comment.author.id === userData.id) {
        var deleteButton = document.createElement("a");
        var deleteText = document.createElement("span");
        deleteText.innerText = "Delete";
        deleteButton.appendChild(deleteText);
        deleteButton.classList.add("comment-delete-button");
        deleteButton.addEventListener("click", function () {
            var commentDeleteConfirm = document.createElement("div");

            var commentDeleteCancel = document.createElement("a");
            commentDeleteCancel.innerText = "Cancel";
            commentDeleteCancel.addEventListener("click", function (e) {
                e.stopPropagation();
                commentDeleteConfirm.parentElement.removeChild(commentDeleteConfirm);
            });
            commentDeleteConfirm.appendChild(commentDeleteCancel);

            var spacer = document.createElement("span");
            spacer.style.width = "20px";
            spacer.style.display = "inline-block";
            commentDeleteConfirm.appendChild(spacer);

            var commentDeleteDelete = document.createElement("a");
            commentDeleteDelete.innerText = "Delete";
            commentDeleteDelete.addEventListener("click", function (e) {
                e.stopPropagation();
                var req = new XMLHttpRequest();
                req.open("DELETE", "/api/program/" + programData.id + "/comment/" + comment.id);
                req.addEventListener("load", function () {
                    var data = JSON.parse(this.response);
                    if (data && data.success) {

                        //If it has a parent we need to decrement the number of replies the parent has
                        if (comment.parent) {
                            for (var i = 0; i < programData.comments.length; i++) {
                                var parentComment = programData.comments[i];
                                if (parentComment.id === comment.parent.id) {
                                    parentComment.replyCount --;

                                    for (var j = 0; j < parentComment.comments.length; j++) {
                                        if (parentComment.comments[j].id === comment.id) {
                                            parentComment.comments.splice(j, 1);
                                        }
                                    }

                                    var el = parentComment.element.getElementsByClassName("show-hide-comments")[0];
                                    el.innerText = el.innerText.replace(/\(\d+\)/, "(" + parentComment.replyCount + ")")
                                    break;
                                }
                            }
                        }else {
                            while (comment.element.nextElementSibling.classList.contains("comment-comment")) {
                                comment.element.parentElement.removeChild(comment.element.nextElementSibling);
                            }

                            for (var i = 0; i < programData.comments.length; i++) {
                                if (programData.comments[i].id === comment.id) {
                                    programData.comments.splice(i, 1);
                                    break;
                                }
                            }
                        }

                        com.parentElement.removeChild(com);
                    }else if (data && !data.success) {
                        alert("Failed with error: " + data.error);
                    }
                });
                req.setRequestHeader("X-CSRFToken", csrf_token)
                req.send();
            });
            commentDeleteConfirm.appendChild(commentDeleteDelete);

            commentDeleteConfirm.classList.add("comment-delete-confirm");
            deleteButton.appendChild(commentDeleteConfirm);
        });
        lowerRowLeft.appendChild(deleteButton);
    }

    upperRow.appendChild(content);
    lowerRow.appendChild(lowerRowLeft);
    lowerRow.appendChild(author).appendChild(link);
    com.appendChild(t).appendChild(upperRow);
    t.appendChild(lowerRow);

    comment.element = com;
    comment.unfolded = null;

    return com;
};

function displayComments (comments) {
    programData.comments = comments;

    var base = document.getElementById("comment-wrap");

    base.appendChild(createCommentTextbox(null));

    for (var i = 0; i < comments.length; i++) {
        base.appendChild(displayComment(comments[i]));
    }

    if (comments.length === 0) {
        base.appendChild(document.createTextNode("No one's posted any comments yet :("))
    }

    var scrollComment = document.getElementById(window.location.hash.slice(1));
    if (scrollComment) {
        scrollComment.scrollIntoView();
    }
}

function vote () {
    var el = this;
    var voteType = el.id.substring(0, el.id.indexOf("-"));

    el.classList.toggle("voted");
    programData.hasVoted[voteType] = !programData.hasVoted[voteType];

    var req = new XMLHttpRequest();
    req.open(programData.hasVoted[voteType] ? "POST" : "DELETE", "/api/program/" + programData.id + "/vote?type=" + voteType);
    req.setRequestHeader("X-CSRFToken", csrf_token);
    req.addEventListener("load", function () {
        var d = JSON.parse(this.response);
        if (!d.success) {
            alert("Failed with error:\n\n" + d.error);

            //Oops, didn't actually vote:
            programData.hasVoted[voteType] = !programData.hasVoted[voteType];
            el.classList.toggle("voted");
        }else {
            if (programData.hasVoted[voteType]) {
                programData.votes[voteType]++;
            }else {
                programData.votes[voteType]--;
            }
            document.getElementById(voteType + "-vote-count").innerHTML = programData.votes[voteType];
        }
    });
    req.send();
};

function save (event) {
    event.preventDefault();

    if (runningLocal) return;

    //Update programData with the lastest textbox code
    programData.js = jsEditor.getValue();
    programData.css = cssEditor.getValue();
    programData.html = htmlEditor.getValue();

    var req = new XMLHttpRequest();
    req.addEventListener("load", function (a) {
        //Something went wrong:
        if (this.status >= 400) {
            var contentType = this.getResponseHeader("content-type").toLowerCase();
            var outputMessage = "Program " + (programData.new ? "creating" : "editing") + " failed";
            if (contentType.indexOf("json") > -1) {
                console.log(JSON.parse(this.response));
                outputMessage += " with the error message:\n\n" + JSON.parse(this.response).error;
            }else if (contentType.indexOf("html") > -1) {
                outputMessage += "; a new window/tab with more information has been opened.";
                window.open("data:text/html," + this.response, "_blank");
            }else {
                outputMessage += ".";
            }
            alert(outputMessage);
        }else if (programData.new) {
            window.location.href = this.getResponseHeader("Location")
        }
    })
    if (programData.id) {
        req.open("PATCH", "/api/program/" + programData.id)
    }else {
        req.open("POST", "/api/program/new");
    }
    req.setRequestHeader("X-CSRFToken", csrf_token)
    req.setRequestHeader("Content-Type", "application/json");
    req.send(JSON.stringify({
        "title" : programData.title,
        "js" : programData.js,
        "css" : programData.css,
        "html" : programData.html,
    }))
}

document.addEventListener("DOMContentLoaded", function() {

    ace.require("ace/ext/language_tools");

    var htmlEditor = ace.edit("html-editor");
    htmlEditor.setTheme("ace/theme/textmate");
    htmlEditor.$blockScrolling = Infinity;
    htmlEditor.getSession().setMode("ace/mode/html");
    htmlEditor.setOptions({
        enableBasicAutocompletion: true
    });

    var cssEditor = ace.edit("css-editor");
    cssEditor.setTheme("ace/theme/textmate");
    cssEditor.$blockScrolling = Infinity;
    cssEditor.getSession().setMode("ace/mode/css");
    cssEditor.setOptions({
        enableBasicAutocompletion: true
    });

    var jsEditor = ace.edit("js-editor");
    jsEditor.setTheme("ace/theme/textmate");
    jsEditor.$blockScrolling = Infinity;
    jsEditor.getSession().setMode("ace/mode/javascript");
    jsEditor.setOptions({
        enableBasicAutocompletion: true
    });

    // TIDYUP Button
    document.getElementById("btnTidyUp").addEventListener("click", function(event) {
        event.preventDefault();

        var html = ace.edit("html-editor").getSession().getValue();
        var html2 = style_html(html);

        ace.edit("html-editor").getSession().setValue(html2);

        var css = ace.edit("css-editor").getSession().getValue();
        var css2 = css_beautify(css);

        ace.edit("css-editor").getSession().setValue(css2);

        var js = ace.edit("js-editor").getSession().getValue();
        var js2 = js_beautify(js);

        ace.edit("js-editor").getSession().setValue(js2);
    });

    // Together Button
    document.getElementById("btnTogether").addEventListener("click", function(event) {
      event.preventDefault();

      TogetherJS(this);
      return false;
    });

    document.getElementById("btnRun").addEventListener("click", runProgram);
    document.getElementById("btnSave").addEventListener("click", save);
    document.getElementById("btnDelete").addEventListener("click", deleteConfirm);

    if (!runningLocal) {
        if (!programData.new) {
            document.getElementById("program-author").innerText = programData.author.displayName;
            document.getElementById("program-author").setAttribute("href", "/user/" + programData.author.username);

            document.getElementById("title-tag").innerText = programData.title + " \u2014 OurJSEditor";
        }

        jsEditor.setValue(programData.js, -1);
        cssEditor.setValue(programData.css, -1);
        htmlEditor.setValue(programData.html, -1);
        document.getElementById("program-title").innerText = programData.title

        if (programData.canEditProgram) {
            document.getElementById("btnSave").style.display = "block"
            if (!programData.new) {
                document.getElementById("btnDelete").style.display = "block"
            }
        }
    }

    titleLabel = document.getElementById("program-title");
    if (!runningLocal && programData.canEditProgram) {
        titleLabel.classList.add("editable");
        titleLabel.addEventListener("click", function (event) {
            event.preventDefault();

            titleInput.value = this.innerText;
            titleLabel.parentNode.insertBefore(titleInput, titleLabel);
            titleLabel.parentNode.removeChild(titleLabel);
            titleInput.focus();
        });
    }

    if (!runningLocal && !programData.new) {
        var voteTypes = ["informative", "artistic", "entertaining"];

        voteTypes.forEach(function (s) {
            document.getElementById(s + "-vote-count").innerHTML = programData.votes[s];
        });

        voteTypes.forEach(function (s) {
            var el = document.getElementById(s + "-vote-button");

            if (programData.hasVoted[s]) {
                el.classList.add("voted")
            }

            el.addEventListener("click", vote);
        });

        //Only bring in comments if it's not a new program
        var req = new XMLHttpRequest();
        req.open("GET", "/api/program/" + programData.id + "/comments");
        req.addEventListener("load", function () {
            var data = JSON.parse(this.response);
            if (data && data.success) {
                displayComments(data.comments);
            }
        });
        req.send();
    }else {
        var t = document.getElementById("vote-table");
        t.parentNode.removeChild(t);

        var c = document.getElementById("comment-wrap");
        c.parentNode.removeChild(c);
    }
});

//Run program on window load. That way Ace is definitely loaded.
window.addEventListener("load", function () {
    runProgram();
});
