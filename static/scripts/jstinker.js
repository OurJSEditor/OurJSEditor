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

var dateToString = function (d) {
    d = new Date(d);
    var currentYear = (new Date()).getFullYear();
    var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return months[d.getMonth()] + " " + d.getDate() + (currentYear === d.getFullYear() ? "" : ", " + d.getFullYear());
}

var displayComment = function (comment) {
    var com = document.createElement("div");
    var t = document.createElement("table");
    var content = document.createElement("td");
    var author = document.createElement("td");
    var upperRow = document.createElement("tr");
    var lowerRow = document.createElement("tr");
    var link = document.createElement("a");
    var replies = document.createElement("td");

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

    comment.unfolded = null;
    if (comment.depth === 0) {
        comment.unfolded = false;

        var dropDown = document.createElement("a");
        dropDown.innerText = "Comment" + (comment.replyCount === 1 ? "" : "s (" + comment.replyCount + ")");
        dropDown.setAttribute("href", "#");
        dropDown.addEventListener("click", function (e) {
            e.preventDefault();
            if (comment.unfolded) return;

            var req = new XMLHttpRequest();
            req.open("GET", "/api/program/" + programData.id + "/comment/" + comment.id + "/comments");
            req.addEventListener("load", function () {
                var data = JSON.parse(this.response);
                if (data && data.success) {
                    for (var i = data.comments.length-1; i >= 0; i--) {
                        programData.comments.push(data.comments[i]);
                        //Inserts after the parent comment
                        comment.element.parentElement.insertBefore(displayComment(data.comments[i]), comment.element.nextSibling);
                    }
                    comment.unfolded = true;
                }
            });
            req.send();
        });
        replies.appendChild(dropDown);
    }else {
        com.classList.add("comment-comment");
    }

    upperRow.appendChild(content);
    lowerRow.appendChild(replies);
    lowerRow.appendChild(author).appendChild(link);
    com.appendChild(t).appendChild(upperRow);
    t.appendChild(lowerRow);
    comment.element = com;
    return com;
};

var displayComments = function (comments) {
    programData.comments = comments;

    var base = document.getElementById("comment-wrap");
    for (var i = 0; i < comments.length; i++) {
        base.appendChild(displayComment(comments[i]));
    }

    if (comments.length === 0) {
        base.innerText = "No one's posted any comments yet :("
    }

    var scrollComment = document.getElementById(window.location.hash.slice(1));
    if (scrollComment) {
        scrollComment.scrollIntoView();
    }
}

document.addEventListener("DOMContentLoaded", function() {

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

    var req = new XMLHttpRequest();
    req.open("GET", "/api/program/" + programData.id + "/comments");
    req.addEventListener("load", function () {
        var data = JSON.parse(this.response);
        if (data && data.success) {
            displayComments(data.comments);
        }
    });
    req.send();
});

//Run program on window load. That way Ace is definitely loaded.
window.addEventListener("load", function () {
    runProgram();
});
