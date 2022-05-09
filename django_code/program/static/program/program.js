var sandboxOrigin;
var jsEditor, htmlEditor, cssEditor;

function makeRequest(method, url, listener, options) {
    //This function is not ready to be used everywhere, yet
    //Method is a string, GET/POST, etc
    //url is a string, url
    //listener is a function to be called after the request has returned without errors. The one parameter will be the parsed object returned from the server
    //options is an object with additional settings
        //options.data is an object to be JSON-stringified and sent
        //options.action is the action that was attempting to be preformed. In the case of an error, the user will see `${options.action} failed with the error ${/*The error message from the server*/}.`
        //options.onfail will be called if the request fails
    if (typeof options === "undefined") {
        options = {};
    }
    var req = new XMLHttpRequest();
    req.addEventListener("load", function (evt) {
        //Something went wrong:
        if (this.status >= 400) {
            var contentType = this.getResponseHeader("content-type").toLowerCase();

            console.log(this.responseText);
            if (typeof options.onfail === "function") {
                options.onfail();
            }

            if (typeof options.action === "undefined") {
                options.action = "Something";
            }

            if (contentType.indexOf("json") > -1) {
                try {
                    var response = JSON.parse(this.responseText);
                    if (typeof response.success === "boolean" && !response.success) {
                        alert(options.action + " failed with the error \"" + response.error + "\"");
                    }else {
                        throw new TypeError("Incorrect `response.success`.");
                    }
                }catch (e) {
                    //This means something returned JSON, but it wasn't us. As far as I know, we never return a status >= 400 without a success: false
                    alert(options.action + " failed. And then the error handling code failed. Please report this, thanks.\n\n" + this.responseText);
                }
            }else if (contentType.indexOf("html") > -1) { //This is a server internal error
                alert(options.action + " failed with an internal server error. Please report this. If popups are enabled, an error page will be opened.");
                var errorWindow = window.open();
                errorWindow.document.open();
                errorWindow.document.write(this.responseText);
                errorWindow.document.close();
            }else {
                alert(options.action + " failed without an error message. Please report this.");
            }
        }else {
            var data = JSON.parse(this.responseText);
            console.assert(data.success, "Data returned successfully without success: true.\n" + this.responseText);
            listener(data);
        }
    });
    req.open(method, url);
    req.setRequestHeader("X-CSRFToken", csrf_token);
    req.setRequestHeader("Accept", "application/json");
    if (typeof options.data === "object") {
        req.setRequestHeader("Content-Type", "application/json");
        req.send(JSON.stringify(options.data))
    }else {
        req.send();
    }
}

var titleLabel;
var titleInput = document.createElement("input");
titleInput.setAttribute("maxlength", "45");
titleInput.setAttribute("id", "program-title");
titleInput.addEventListener("change", removeTitleInput);
titleInput.addEventListener("blur", removeTitleInput);
titleInput.addEventListener("keypress", function (e) {
    //If the enter or return key is pressed. keyCode for older browser compatibility
    if (e.key === "Enter" || e.keyCode === 13) {
        removeTitleInput();
    }
});

function removeTitleInput () {
    if (titleInput.parentNode === null) return;
    if (titleInput.value.trim() === "") { //Only white-space titles
        titleInput.focus(); //Make sure it stays focused
        return;
    }
    titleLabel.innerText = titleInput.value;
    titleInput.parentNode.insertBefore(titleLabel, titleInput);
    titleInput.parentNode.removeChild(titleInput);
    if (programData.title !== titleLabel.innerText && !programData.unsaved) {
        var req = new XMLHttpRequest();
        req.addEventListener("load", function (evt) {
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
        req.open("PATCH", "/api/program/" + programData.id);
        req.setRequestHeader("X-CSRFToken", csrf_token);
        req.send(JSON.stringify({ "title" : titleInput.value }))
    }
    programData.title = document.getElementById("program-title").innerText;
}

function openConfirm (event, confirmBoxId) {
    event.preventDefault();
    document.getElementById("back-cover").style.display = "block";
    document.getElementById(confirmBoxId).style.display = "block";
}

function closeConfirm () {
    document.getElementById("back-cover").style.display = "none";
    document.getElementById("delete-confirm").style.display = "none";
    document.getElementById("publish-confirm").style.display = "none";

    document.getElementById("publish-confirm-button").removeEventListener("click", publishProgram);
}

function deleteProgram () {
    var req = new XMLHttpRequest();
    req.addEventListener("load", function (evt) {
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
            // Make sure onbeforeunload doesn't fire
            programData.deleted = true;
            // Redirect back to the user profile
            window.location.href = "/user/" + programData.author.username;
        }
    });
    req.open("DELETE", "/api/program/" + programData.id);
    req.setRequestHeader("X-CSRFToken", csrf_token);
    req.send();
}

function imageReceived (event) {
    var data = JSON.parse(event.data);

    //Frame is potentially insecure.
    if (data.imageData.indexOf("data:image/png;base64,") !== 0) {
        throw new Error("Image received from iframe is not base64 png data.");
    }

    programData.thumbnailData = data.imageData;

    document.getElementById("thumbnail-preview").src = programData.thumbnailData;

    document.getElementById("publish-confirm-button").addEventListener("click", publishProgram);
}

//Runs after the publish confirm button is clicked
function publishProgram () {
    save();

    var req = new XMLHttpRequest();
    req.addEventListener("load", function () {
        var d = JSON.parse(this.responseText);
        if (d.success) {
            //Re-hide confirm box
            document.getElementById("publish-confirm").style.display = "none";
            //Re-hide background
            document.getElementById("back-cover").style.display = "none";
            //Make sure published time is visible
            document.getElementById("published").style.display = "block";
            //Update published time in the sidebar
            document.getElementById("published-date").innerHTML = dateToString(d.lastPublished);
            //Update published time in programData
            programData.lastPublished = d.lastPublished;
        }else {
            alert("Failed with error: " + d.error);
        }
    });
    req.open("PATCH", "/api/program/" + programData.id);
    req.setRequestHeader("X-CSRFToken", csrf_token);
    req.send(JSON.stringify({
        "publishedMessage": document.getElementById("publish-message").value,
        "imageData": programData.thumbnailData
    }));

    document.getElementById("publish-confirm-button").removeEventListener("click", publishProgram);
}

//Defined as a string instead of a regex literal because regex objects remember state when used with .exec
//Also lets us change flags
var INSERT_REGEX = "/\\*\\[OurJSEditor insert:(js|css)]\\*/";
function runProgram (event) {
    if (event) {
        event.preventDefault();
    }

    //Insert JS
    var pageCode = htmlEditor.getSession().getValue();
    pageCode = pageCode.replace(new RegExp(INSERT_REGEX, "gi"), function (comment, language, position, code) {
        return ace.edit(language.toLowerCase() + "-editor").getSession().getValue();
    });

    programData.lastRunCode = {
        js: jsEditor.getSession().getValue(),
        css: cssEditor.getSession().getValue(),
        html: htmlEditor.getSession().getValue(),
        pageCode: pageCode,
    };

    clearConsole();

    document.getElementById("preview").contentWindow.postMessage(JSON.stringify({
        type: "execute",
        code: pageCode
    }), "*");
}

function dateToString (d) {
    d = new Date(d);
    var currentYear = (new Date()).getFullYear();
    var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return d.getTime() ? months[d.getMonth()] + " " + d.getDate() + (currentYear === d.getFullYear() ? "" : ", " + d.getFullYear()) : "Never";
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
    submit.classList.add("comment-submit");

    submit.addEventListener("click", function (e) {
        e.preventDefault();

        var req = new XMLHttpRequest();
        req.open("POST", "/api/program/" + programData.id + "/comment/new");
        req.setRequestHeader("X-CSRFToken", csrf_token);
        req.setRequestHeader("Content-Type", "application/json");
        req.addEventListener("load", function () {
            var data = JSON.parse(this.response);
            if (data && data.success) {
                var commentObj = {
                    "content": textbox.value,
                    "replyCount": 0,
                    "depth": parent ? 1 : 0,
                    "program": {
                        "id": programData.id,
                    },
                    "originalContent": textbox.value,
                    "parent": parent ? {"id": parent} : null,
                    "author": userData,
                    "edited": null,
                    "created": (new Date()).toISOString().replace(/\.\d\d\dZ/, "Z"),
                    "id": data.id,
                };

                if (parent) {
                    for (var i = 0; i < programData.comments.length; i++) {
                        if (programData.comments[i].id === parent) {
                            programData.comments[i].comments.push(commentObj);
                            programData.comments[i].replyCount ++;
                            var el = programData.comments[i].element.getElementsByClassName("show-hide-comments")[0];
                            el.innerText = el.innerText.replace(/\(\d+\)/, "(" + programData.comments[i].replyCount + ")");
                            break;
                        }
                    }
                }else {
                    programData.comments.push(commentObj);

                    if (programData.comments.length === 1) {
                        document.getElementById("no-comments-message").style.display = "none";
                    }
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

    textbox.classList.add("comment-content");

    content.appendChild(textbox);
    com.appendChild(t).appendChild(row);
    row.appendChild(content);
    row.appendChild(buttons);
    return com;
}

function jumpToComment(commentEl) {
    if (commentEl) {
        commentEl.scrollIntoView();
        var permalinked = document.getElementsByClassName("permalinked");
        if (permalinked.length) {
            permalinked[0].classList.remove("permalinked");
        }
        commentEl.classList.add("permalinked");
    }
}

//comment is a comment object; scrollTarget is the id of the comment that we're going to try to scroll to once things load
function unfoldComment (comment, scrollTarget) {
    //If we've already loaded
    if (comment.comments) {
        comment.element.parentElement.insertBefore(createCommentTextbox(comment.id), comment.element.nextSibling);
        for (var i = comment.comments.length-1; i >= 0; i--) {
            comment.element.parentElement.insertBefore(displayComment(comment.comments[i]), comment.element.nextSibling);
        }
        comment.unfolded = true;
        var el = comment.element.getElementsByClassName("show-hide-comments")[0];
        el.innerText = el.innerText.replace(/^Show/, "Hide");
    }else {
        var req = new XMLHttpRequest();
        req.open("GET", "/api/program/" + programData.id + "/comment/" + comment.id + "/comments");
        req.addEventListener("load", function () {
            var data = JSON.parse(this.response);
            if (data && data.success) {
                comment.comments = data.comments;
                comment.replyCount = data.comments.length; //Reset local value to the correct number
                var el = comment.element.getElementsByClassName("show-hide-comments")[0];
                el.innerText = el.innerText.replace(/\(\d+\)/, "(" + comment.replyCount + ")");

                unfoldComment(comment);

                if (scrollTarget) {
                    var scrollComment = document.getElementById(scrollTarget);
                    jumpToComment(scrollComment);
                }
            }
        });
        req.send();
    }
}

function initMd () {
    window.md = new Remarkable({
        html: false, breaks: true, linkify: true, typographer: true,
        highlight: function (str, lang) {
            if (lang && hljs.getLanguage(lang)) {
                return hljs.highlight(lang, str).value;
            }
            return hljs.highlightAuto(str).value;
        }
    });
    md.block.ruler.disable([ 'table', 'footnote' ]);
    md.inline.ruler.disable([ 'footnote_ref' ]);
    //Images are parsed as inline links, so we can't turn off parsing,
    //but we can overwrite the renderer so they never get displayed. Not ideal
    md.renderer.rules.image = function () {
        return "";
    };

    var lenientLinkValidator = md.inline.validateLink;

    //We only want to allow masked links if they're to the same origin, which we do by forbidding anything with a protocol.
    //Adapted from https://github.com/jonschlinkert/remarkable/blob/fa88dcac16832ab26f068c30f0c070c3fec0d9da/lib/parser_inline.js#L146
    function strictLinkValidator (url) {
        var str = url.trim().toLowerCase();
        //If it includes a protocol, stop it.
        return !(/^[a-z][a-z0-9+.-]*:/.test(str));
    }

    //Definitely hacky, but we add a rule before parsing non-masked links that loosens the requirements of the validator
    md.core.ruler.before("linkify", "lenientLinkValidation", function () {
        md.inline.validateLink = lenientLinkValidator;
    }, {});
    //And then before parsing masked links, make it strict again
    md.inline.ruler.before("links", "strictLinkValidation", function () {
        md.inline.validateLink = strictLinkValidator;
    }, {});
}

function displayComment (comment) {
    var com = document.createElement("div");
    var t = document.createElement("table");
    var contentCell = document.createElement("td");
    var content = document.createElement("div");
    var lowerRowRight = document.createElement("td");
    var upperRow = document.createElement("tr");
    var lowerRow = document.createElement("tr");
    var link = document.createElement("a");
    var lowerRowLeft = document.createElement("td");
    var permalink = document.createElement("a");

    com.classList.add("comment");
    com.setAttribute("id", "comment-" + comment.id);
    link.setAttribute("href", "/user/" + comment.author.username);
    lowerRowRight.classList.add("lower-right");

    contentCell.setAttribute("colspan", 2);
    content.classList.add("comment-content");
    content.innerHTML = md.render(comment.content);

    permalink.href = window.location.origin + window.location.pathname + "#comment-" + comment.id;
    permalink.innerText = "(Permalink)";
    permalink.classList.add("permalink");
    lowerRowRight.appendChild(permalink);
    lowerRowRight.appendChild(document.createTextNode("Posted " + dateToString(comment.created) + " by"));
    link.innerText = comment.author.displayName;
    lowerRowRight.appendChild(link);

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
                while (comment.element.nextElementSibling && comment.element.nextElementSibling.classList.contains("comment-comment")) {
                    comment.element.parentElement.removeChild(comment.element.nextElementSibling);
                }
                comment.unfolded = false;
                var el = comment.element.getElementsByClassName("show-hide-comments")[0];
                el.innerText = el.innerText.replace(/^Hide/, "Show");
            }else {
                unfoldComment(comment);
            }
        });
        lowerRowLeft.appendChild(dropDown);
    }else {
        com.classList.add("comment-comment");
    }

    if (comment.author.id === userData.id) {
        //Edit button
        var editButton = document.createElement("a");
        editButton.addEventListener("click", function () {
            var commentObj;

            for (var i = 0; i < programData.comments.length; i++) {
                if (programData.comments[i].element === com) {
                    commentObj = programData.comments[i];
                    break;
                }
                for (var j = 0; programData.comments[i].comments && j < programData.comments[i].comments.length; j++) {
                    if (programData.comments[i].comments[j].element === com) {
                        commentObj = programData.comments[i].comments[j];
                        break;
                    }
                }
            }

            //Remove old content
            var contentEl = com.getElementsByClassName("comment-content")[0];
            contentEl.parentNode.removeChild(contentEl);

            /* -- Create new content -- */
            //Textbox
            var textbox = document.createElement("textarea");
            textbox.value = commentObj.content;
            textbox.classList.add("comment-content");

            var textboxWrapper = document.createElement("div");
            textboxWrapper.classList.add("textbox-wrapper");

            //Create submit button
            var submit = document.createElement("a");
            submit.innerText = "Save";
            submit.classList.add("comment-submit");
            submit.addEventListener("click", function () {
                var req = new XMLHttpRequest();
                req.open("PATCH", "/api/program/" + programData.id + "/comment/" + commentObj.id);
                req.addEventListener("load", function () {
                    var d = JSON.parse(this.responseText);
                    if (d.success) {
                        //Remove textbox and buttons
                        com.classList.remove("comment-editing");
                        contentCell.removeChild(textboxWrapper);
                        contentCell.removeChild(buttonWrapper);

                        //Over write the content of the old element
                        contentEl.innerHTML = md.render(textbox.value);

                        //Insert the content element again
                        contentCell.appendChild(contentEl);

                        //Save it into ProgramData
                        commentObj.content = textbox.value;
                    }else {
                        alert("Failed with error: " + d.error);
                    }
                });
                req.setRequestHeader("X-CSRFToken", csrf_token);
                req.send(JSON.stringify({
                    "content": textbox.value
                }));
            });

            //Create cancel button:
            var cancel = document.createElement("a");
            cancel.innerText = "Cancel";
            cancel.classList.add("comment-cancel");
            cancel.addEventListener("click", function () {
                //Remove new content
                com.classList.remove("comment-editing");
                contentCell.removeChild(textboxWrapper);
                contentCell.removeChild(buttonWrapper);

                //Add back old content
                contentCell.appendChild(contentEl);
            });

            //Add buttons
            var buttonWrapper = document.createElement("div");
            buttonWrapper.classList.add("buttons-wrapper");
            buttonWrapper.appendChild(submit);
            buttonWrapper.appendChild(cancel);

            //Add new content
            com.classList.add("comment-editing");
            contentCell.appendChild(textboxWrapper).appendChild(textbox);
            contentCell.appendChild(buttonWrapper);
        });
        editButton.classList.add("comment-edit-button");
        editButton.innerText = "Edit";
        lowerRowLeft.appendChild(editButton);

        //Delete button
        var deleteButton = document.createElement("a");
        var deleteText = document.createElement("span");
        deleteText.innerText = "Delete";
        deleteButton.appendChild(deleteText);
        deleteButton.classList.add("comment-delete-button");
        deleteButton.addEventListener("click", function () {
            //Return if there's already a confirm thing open under this.
            if (deleteButton.getElementsByClassName("comment-delete-confirm").length) return;

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
                                    el.innerText = el.innerText.replace(/\(\d+\)/, "(" + parentComment.replyCount + ")");
                                    break;
                                }
                            }
                        }else {
                            while (comment.element.nextElementSibling && comment.element.nextElementSibling.classList.contains("comment-comment")) {
                                comment.element.parentElement.removeChild(comment.element.nextElementSibling);
                            }

                            for (var i = 0; i < programData.comments.length; i++) {
                                if (programData.comments[i].id === comment.id) {
                                    programData.comments.splice(i, 1);
                                    break;
                                }
                            }

                            if (programData.comments.length === 0) {
                                document.getElementById("no-comments-message").style.display = "block";
                            }
                        }

                        com.parentElement.removeChild(com);
                    }else if (data && !data.success) {
                        alert("Failed with error: " + data.error);
                    }
                });
                req.setRequestHeader("X-CSRFToken", csrf_token);
                req.send();
            });
            commentDeleteConfirm.appendChild(commentDeleteDelete);

            commentDeleteConfirm.classList.add("comment-delete-confirm");
            deleteButton.appendChild(commentDeleteConfirm);
        });
        lowerRowLeft.appendChild(deleteButton);
    }

    upperRow.appendChild(contentCell).appendChild(content);
    lowerRow.appendChild(lowerRowLeft);
    lowerRow.appendChild(lowerRowRight);
    com.appendChild(t).appendChild(upperRow);
    t.appendChild(lowerRow);

    comment.element = com;
    comment.unfolded = null;

    var scrollCommentId = window.location.hash.match(/^#comment-(\w{10})$/);
    if (scrollCommentId && scrollCommentId[1] === comment.id) {
        jumpToComment(com);
    }

    return com;
}

function displayComments (comments) {
    programData.comments = comments;

    var base = document.getElementById("comment-wrap");

    base.appendChild(createCommentTextbox(null));

    for (var i = 0; i < comments.length; i++) {
        base.appendChild(displayComment(comments[i]));
    }


    var noCommentsMessage = document.createElement("div");
    noCommentsMessage.setAttribute("id", "no-comments-message");
    noCommentsMessage.classList.add("comment-content");
    noCommentsMessage.appendChild(document.createTextNode("No one's posted any comments yet :("));
    base.appendChild(noCommentsMessage);

    if (comments.length !== 0) {
        noCommentsMessage.style.display = "none";
    }

    hashUpdated();
}

function hashUpdated() {
    var scrollCommentId = window.location.hash.slice(1);
    var scrollComment = document.getElementById(scrollCommentId);
    if (scrollComment && scrollCommentId) {
        jumpToComment(scrollComment);
    }else if (scrollCommentId.search(/^comment-\w{10}$/) > -1) {
        var req = new XMLHttpRequest();
        req.open("GET", "/api/comment/" + scrollCommentId.slice(8));
        req.addEventListener("load", function () {
            if (this.status === 200) {
                var data = JSON.parse(this.response);
                for (var i = 0; i < programData.comments.length; i++) {
                    if (programData.comments[i].id === data.parent.id) {
                        break;
                    }
                }

                unfoldComment(programData.comments[i], scrollCommentId);
            }
        });
        req.send();
    }
}

//Creates and returns a DOM element representing a row in the collaborator popup, with buttons and stuff
function makeCollaboratorRow(identifier) {
    var item = document.createElement("li");

    //Create the remove icon/button if we can edit the program
    if (programData.canEditProgram ) {
        var removeIcon = document.createElement("span");
        removeIcon.classList.add("icon", "icon-delete", "clickable");
        removeIcon.addEventListener("click", function () {
            //Double check if they're about to remove themselves
            if (userData.id === item.dataset.userId) {
                if (!confirm("You're about to remove yourself from the collaborators on this program.\nYou can't undo this action.")) {
                    return;
                }
            }

            //Make a request to remove the user
            makeRequest("DELETE", "/api/program/" + programData.id + "/collaborators", function (data) {
                //Mutate programData
                for (var i = 0; i < programData.collaborators.length; i++) {
                    if (programData.collaborators[i] === item.dataset.userId) {
                        programData.collaborators.splice(i, 1);
                    }
                }
                //If you just removed yourself, refresh everything
                if (userData.id === item.dataset.userId) {
                    window.location.reload();
                }else {
                    //Remove from the DOM
                    item.parentElement.removeChild(item);
                }
            }, {action: "Removing collaborator " + identifier, data: {user: {id: item.dataset.userId}}});
        });
        item.appendChild(removeIcon);
    }

    makeRequest("GET", "/api/user/" + identifier, function (data) {
        item.appendChild(document.createTextNode("@" + data.username));
        item.dataset.userId = data.id;
    }, {action: "Displaying collaborator " + identifier});
    return item;
}

function addCollaborator(username) {
    //Silently ignore empty textbox/input
    if (username.length === 0) {
        return;
    }
    //Make a request to add the user (backend verifies user)
    makeRequest("POST", "/api/program/" + programData.id + "/collaborators", function (data) {
        var collaboratorsList = document.getElementById("collaborators");
        collaboratorsList.insertBefore(makeCollaboratorRow(username), collaboratorsList.firstElementChild.nextElementSibling);

        //Add the new collaborator to the local list
        programData.collaborators.push(data.id);
    }, {
        data: {user: {username: username}},
        action: "Adding collaborator \"" + username + "\"",
    });
}

function createCollaboratePopup() {
    var collaboratePopup = document.getElementById("collaborate-popup");

    //If we're not the program owner or a collaborator, remove the textbox to add collaborators
    //Collaborators can add or remove any other collaborators
    if (!programData.canEditProgram || programData.unsaved) {
        var addCollaboratorLi = document.getElementById("add-collaborator");
        addCollaboratorLi.parentElement.removeChild(addCollaboratorLi);
    }else {
        var collaboratorTextbox = document.getElementById("add-collaborator-textbox");
        collaboratorTextbox.addEventListener("keypress", function (e) {
            if (e.key === "Enter" || e.keyCode === 13) {
                addCollaborator(collaboratorTextbox.value);
                collaboratorTextbox.value = "";
            }
        });

        var addCollaboratorButton = document.getElementById("add-collaborator-button");
        addCollaboratorButton.addEventListener("click", function () {
            addCollaborator(collaboratorTextbox.value);
            collaboratorTextbox.value = "";
        });
    }

    document.getElementById("close-button-wrap").addEventListener("click", function () {
        collaboratePopup.style.display = "none";
    });

    //The popup actually lives inside the button in the DOM tree. This stops clicks on the popup from propagating up to the button
    collaboratePopup.addEventListener("click", function (e) { e.stopImmediatePropagation(); });

    var collaboratorsList = document.getElementById("collaborators");
    var collaborators = programData.collaborators;
    for (var i = 0; i < collaborators.length; i++) {
        collaboratorsList.appendChild(makeCollaboratorRow(collaborators[i]));
    }
}

//Takes a string, either `tabbed` or `split`
function switchEditorLayout (newLayout) {
    // If the layout matches, do nothing (console.warn?)
    var editorWrap = document.getElementById("editors");
    if (editorWrap.classList.contains(newLayout)) {
        return;
    }

    var bottomWrap = document.getElementsByClassName("bottom")[0];

    if (newLayout === "tabbed") {
        editorWrap.classList.replace("split", "tabbed");

        //Move things from place to other place
        var mainEditor = document.getElementById("main-editor");
        var bottomEditors = bottomWrap.children;
        while (bottomEditors.length) {
            var removedEditor = bottomWrap.removeChild(bottomEditors[0]);

            mainEditor.parentElement.insertBefore(removedEditor, mainEditor);
        }
    }else if (newLayout === "split") {
        editorWrap.classList.replace("tabbed", "split");

        //Move things from place to other place
        var topWrap = document.getElementsByClassName("top")[0];
        var htmlEditorElmt = document.getElementById("html-editor").parentElement;
        var cssEditorElmt = document.getElementById("css-editor").parentElement;

        topWrap.removeChild(htmlEditorElmt);
        topWrap.removeChild(cssEditorElmt);
        bottomWrap.appendChild(htmlEditorElmt);
        bottomWrap.appendChild(cssEditorElmt);

        var bottomRow = document.querySelector("#editors tr.bottom");
        //Fix styles in Firefox
        if (document.getElementById("html-editor").getBoundingClientRect().height < 5) { //Something's probably wrong
            var bottomConts = bottomRow.querySelectorAll(".editor-container");
            for (var i = 0; i < bottomConts.length; i++) {
                bottomConts[i].style.height = "100%"; //Go get em!
            }
        }
    }else {
        throw new Error("Invalid layout");
    }

    //Add or remove the rowspan attribute
    var conts = document.querySelectorAll(".editor-container:not(#preview-container)");
    for (var i = 0; i < conts.length; i++) {
        conts[i].setAttribute("rowspan", (newLayout === "tabbed" ? "2" : "1"));
    }

    //Resize everything
    jsEditor.resize();
    htmlEditor.resize();
    cssEditor.resize();
}

function switchEditorTabs (event) {
    var clickedButton = event.target;
    if (clickedButton.classList.contains("selected")) {
        return; //Do nothing if clicking a selected tab
    }

    var tabRow = document.getElementById("tab-row");
    var tabButtons = tabRow.children;
    for (var i = 0; i < tabButtons.length; i++) {
        //Find the associated element
        var editor = document.getElementById(tabButtons[i].dataset.tabId + "-editor").parentElement;

        //Add the selected class to the button that we clicked, and remove it from the others
        var addSelected = tabButtons[i] === clickedButton;
        tabButtons[i].classList.toggle("selected", addSelected);
        editor.classList.toggle("selected", addSelected);
        if (addSelected) { //If this is the thing we're switching to
            //Move the tab row inside of it
            tabRow.parentElement.removeChild(tabRow);
            editor.insertBefore(tabRow, editor.firstElementChild);
        }
    }

    //Resize everything (ideally we just need to resize the new tab, but we don't know what editor that is
    jsEditor.resize();
    htmlEditor.resize();
    cssEditor.resize();
}

function clearConsole () {
    var consoleEl = document.getElementById("console-el");

    while (consoleEl.firstChild) {
        consoleEl.removeChild(consoleEl.firstChild);
    }
}

// Finds a position in the 3 editors.
function findLine (lineNum, colNum) {
    var blocks = [];
    var html = programData.lastRunCode.html;

    //While we have html left
    while (html.length) {
        // If we have an insert regex
        var match = html.match(new RegExp(INSERT_REGEX, "i"));
        if (match) {
            //Find where INSERT_REGEX is
            var matchPos = html.search(new RegExp(INSERT_REGEX, "i"));
            //Push a block from the start of html to the start of INSERT_REGEX
            blocks.push({
                content: html.slice(0, matchPos),
                lang: "html",
            });

            //Push a block corresponding to the INSERT_REGEX
            blocks.push({
                content: programData.lastRunCode[match[1].toLowerCase()],
                match: match[0],
                lang: match[1]
            });

            //Remove both bits from html
            html = html.slice(matchPos + match[0].length);
        } else {
            // Push a block from the start of html to the end of html
            blocks.push({
                content: html,
                lang: "html",
            });
            // That means we have nothing left
            html = "";
        }
    }

    //Everything is 1-indexed
    var codeStartLine = 1; //The line at the beginning of the current block, in code
    var codeStartCol = 1; //The col of the first char of the current block , in code
    var htmlStartLine = 1; //The line, in html, where this block/match starts
    var htmlStartCol = 1; //The col, in html, where this block/match starts
    while (blocks.length) {
        var block = blocks.shift();
        var lines = block.content.split("\n");
        //The number of lines this block spans across
        var numLinesSpanning = lines.length;

        //Calculate where this block ends in the code
        var codeEndLine = codeStartLine + numLinesSpanning - 1; //Starting at 1, moving down lines - 1
        var codeEndCol; //The col of the last char of this block
        if (numLinesSpanning > 1) {
            codeEndCol = lines[lines.length - 1].length; //Possibly 0, if the last char of this block is a newline
        }else {
            codeEndCol = codeStartCol + lines[0].length;
        }

        //Calculate where this block ends in HTML
        var htmlEndLine;
        var htmlEndCol;
        if (block.lang === "html") {
            htmlEndLine = htmlStartLine + numLinesSpanning - 1;
            if (numLinesSpanning > 1) {
                htmlEndCol = lines[lines.length - 1].length; //Possibly 0, if the last char of this block is a newline
            }else {
                htmlEndCol = htmlStartCol + lines[0].length - 1; //e.g. start at 1, add 8, end at 8
            }
        }else {
            htmlEndLine = htmlStartLine; //Doesn't change, no line breaks in match
            htmlEndCol = htmlStartCol + block.match.length - 1;
        }

        // Are we in this block?
        if (lineNum < codeEndLine || (lineNum === codeEndLine && colNum < codeEndCol)) {
            //Then we're in this block

            var col;
            if (lineNum === codeStartLine) { // If we're on the first line of this block
                col = colNum - codeStartCol + (block.lang === "html" ? htmlStartCol : 1);
            }else {
                //If we're not on the first line, then code col is the same as the block col
                col = colNum;
            }

            return {
                lang: block.lang,
                lineNum: lineNum - codeStartLine + (block.lang === "html" ? htmlStartLine : 1),
                colNum: col
            };
        }

        // Then we're not in this block, move on
        codeStartLine = codeEndLine; //Update code line
        codeStartCol = codeEndCol + 1; //Update code col

        htmlStartLine = htmlEndLine; //Update html line
        htmlStartCol = htmlEndCol + 1; //Update HTML col
    }

    //If we get here, error
    throw new Error("Error when attempting to resolve local error location.");
}

function logToConsole (type, data) {
    var consoleEl = document.getElementById("console-el");

    var newMessage = document.createElement("div");
    var messageContents = document.createElement("pre");
    var messageRight = document.createElement("span");
    messageRight.classList.add("message-right");
    newMessage.classList.add("message");
    newMessage.appendChild(messageContents);
    if (type === "error") {
        var blobOrigin = "blob:" + sandboxOrigin + "/";
        var errorLine;
        //Check if the error was in one of our files
        if (data.fileName.slice(0, blobOrigin.length) === blobOrigin) {
            if (data.colNum === 0) {
                //In the case of a syntax error, colNum could be 0 (since columns are 1-indexed, this is a problem)
                //We can't determine where the error occurred, so there's really no "right" way of handling it.
                //We bring colNum back into the code to prevent errors later on, and let findLine have a guess at it.
                data.colNum += 1;
            }
            errorLine = findLine(data.lineNum, data.colNum);
            errorLine.file = errorLine.lang.toUpperCase();
        }else { //Okay, this wasn't us, pass through
            errorLine = data;
            //Extract URL parts after the last /, the file name
            var fileNameMatch = data.fileName.match(/\/([^/]+?)(?:\?.*)?$/);
            errorLine.file = fileNameMatch && fileNameMatch[1];
        }

        newMessage.classList.add("error");
        messageContents.appendChild(document.createTextNode(data.name + ": " + data.message));
        var errorLocation = errorLine.file + ":" + errorLine.lineNum + ":" + errorLine.colNum;
        messageRight.appendChild(document.createTextNode(errorLocation));
        newMessage.appendChild(messageRight);
    }else {
        newMessage.classList.add("message", type === "console.log" ? "log" : "error", "lang-js");
        messageContents.appendChild(document.createTextNode(data));
        if (type === "console.log") { //Don't highlight console.error blocks
            hljs.highlightBlock(messageContents);
        }
    }
    consoleEl.appendChild(newMessage);
}

function vote () {
    var el = this;
    var voteType = el.id.substring(0, el.id.indexOf("-"));

    el.classList.toggle("voted");
    programData.hasVoted[voteType] = !programData.hasVoted[voteType];
    var hasVoted = programData.hasVoted[voteType];

    var req = new XMLHttpRequest();
    req.open(hasVoted ? "POST" : "DELETE", "/api/program/" + programData.id + "/vote");
    req.setRequestHeader("X-CSRFToken", csrf_token);
    req.addEventListener("load", function () {
        var d = JSON.parse(this.response);
        if (!d.success) {
            alert("Failed with error:\n\n" + d.error);

            //Oops, didn't actually vote:
            programData.hasVoted[voteType] = !programData.hasVoted[voteType];
            el.classList.toggle("voted");
        }else {
            if (hasVoted) {
                programData.votes[voteType]++;
            }else {
                programData.votes[voteType]--;
            }
            document.getElementById(voteType + "-vote-count").innerHTML = programData.votes[voteType];
        }
    });
    req.send(JSON.stringify({
        type: voteType
    }));
}

function save (fork) {
    //Update programData with the latest textbox code
    programData.js = jsEditor.getValue();
    programData.css = cssEditor.getValue();
    programData.html = htmlEditor.getValue();

    var req = new XMLHttpRequest();
    req.addEventListener("load", function (evt) {
        //Something went wrong:
        if (this.status >= 400) {
            var contentType = this.getResponseHeader("content-type").toLowerCase();
            var outputMessage = "Program " + (programData.unsaved ? "creating" : "editing") + " failed";
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
        }else if (programData.unsaved || fork) {
            window.location.href = this.getResponseHeader("Location")
        }
    });
    if (fork) {
        req.open("POST", "/api/program/" + programData.id + "/forks");
    }else if (programData.id) {
        req.open("PATCH", "/api/program/" + programData.id);
    }else {
        req.open("POST", "/api/program/new");
    }
    req.setRequestHeader("X-CSRFToken", csrf_token);
    req.setRequestHeader("Content-Type", "application/json");
    req.send(JSON.stringify({
        "title" : programData.title,
        "js" : programData.js,
        "css" : programData.css,
        "html" : programData.html,
    }));
}

document.addEventListener("DOMContentLoaded", function() {
    sandboxOrigin = new URL(document.getElementById("preview").src).origin;

    window.addEventListener("message", function (evt) {
        if (evt.origin !== sandboxOrigin) {
            return;
        }

        var data = JSON.parse(evt.data);
        // Errors are sent 1 at a time
        if (data.type === "error") {
            logToConsole(data.type, data.data);
        }else {
            // But console. messages come in lists
            for (var i = 0; i < data.messages.length; i++) {
                logToConsole(data.type, data.messages[i]);
            }
        }
    });

    ace.config.set("basePath", "/static/program/ace");

    ace.require("ace/ext/language_tools");

    htmlEditor = ace.edit("html-editor");
    htmlEditor.getSession().setMode("ace/mode/html");

    cssEditor = ace.edit("css-editor");
    cssEditor.getSession().setMode("ace/mode/css");

    jsEditor = ace.edit("js-editor");
    jsEditor.getSession().setMode("ace/mode/javascript");

    document.addEventListener("keydown", function (e) {
        //cmd/ctrl/shift + enter to run
        if (e.key ? (e.key === "Enter") : (e.keyCode === 13)) {
            if (e.metaKey || e.ctrlKey || e.shiftKey) {
                runProgram();
                e.preventDefault() && e.stopPropagation();
            }
        }else if (e.key ? (e.key === "s") : (e.keyCode === 83)) {
            //cmd/ctrl + s to save
            if (e.metaKey || e.ctrlKey) {
                save(false);
                e.preventDefault() && e.stopPropagation();
            }
        }
    });

    //Make the bottom row draggable/resizeable
    //Dragging far enough that the page gets resized is wonky :(
    var bottomDragger = document.getElementById("bottom-dragger");
    var bottomRow = document.querySelector("#editors tr.bottom");

    var bottomDraggingState = {
        isDragging: false,
        lastY: undefined,
        currentHeight: bottomRow.getBoundingClientRect().height
    };
    bottomDragger.addEventListener("mousedown", function (event) {
        bottomDraggingState.isDragging = true;
        bottomDraggingState.lastY = event.clientY;
    });
    window.addEventListener("mouseup", function () {
        bottomDraggingState.isDragging = false;
    });
    document.addEventListener("mousemove", function (event) {
        if (bottomDraggingState.isDragging) {
            if (event.buttons === 0) {
                //Prevent the dragger from ever being stuck down
                bottomDraggingState.isDragging = false;
                return;
            }
            bottomDraggingState.currentHeight += event.clientY - bottomDraggingState.lastY;
            bottomRow.style.height = bottomDraggingState.currentHeight + "px";
            bottomDraggingState.lastY = event.clientY;

            //Resize everything
            jsEditor.resize();
            htmlEditor.resize();
            cssEditor.resize();
        }
    });

    //Add event listeners to the editor tab buttons
    var tabButtons = document.getElementById("tab-row").children;
    for (var i = 0; i < tabButtons.length; i++) {
        tabButtons[i].addEventListener("click", switchEditorTabs);
    }

    document.getElementById("editor-settings").appendChild(
        initEditorSettings(
            document.getElementById("editor-settings-button"), // The element to make the toggle button
            [jsEditor, cssEditor, htmlEditor], // The editors to control
            function(settingKey, newValue) { // A callback to run whenever a setting is changed
                if (settingKey === "editorLayout") {
                    // switchEditorLayout(newValue);
                }
            }
        )
    );

    document.getElementById("run-button").addEventListener("click", runProgram);
    document.getElementById("save-button").addEventListener("click", function (e) {
        e.preventDefault();
        save(false);
    });
    document.getElementById("fork-button").addEventListener("click", function (e) {
        e.preventDefault();
        save(true);
    });
    document.getElementById("delete-button").addEventListener("click", function (e) {
        openConfirm(e, "delete-confirm");
    });
    document.getElementById("publish-button").addEventListener("click", function (e) {
        document.getElementById("preview").contentWindow.postMessage(JSON.stringify({
            type: "thumbnail-request"
        }), "*");

        window.addEventListener("message", imageReceived, false);

        openConfirm(e, "publish-confirm");
    });

    document.getElementById("delete-cancel-button").addEventListener("click", closeConfirm);
    document.getElementById("publish-cancel-button").addEventListener("click", closeConfirm);

    document.getElementById("delete-confirm-button").addEventListener("click", deleteProgram);

    document.getElementById("back-cover").addEventListener("click", closeConfirm);

    //Before unload listener
    window.addEventListener("beforeunload", function (e) {
        var hasChanged = !programData.deleted &&
                programData.js !== jsEditor.getValue() ||
                programData.css !== cssEditor.getValue() ||
                programData.html !== htmlEditor.getValue();

        if (hasChanged) {
            e.preventDefault();
            e.returnValue = "You have unsaved code changes.";
        }else {
            return undefined;
        }
    });

    jsEditor.setValue(programData.js, -1);
    cssEditor.setValue(programData.css, -1);
    htmlEditor.setValue(programData.html, -1);
    document.getElementById("program-title").innerText = programData.title;

    //TODO: Maybe add a login check/pop-up here
    if (programData.canEditProgram) {
        document.getElementById("save-button").style.display = "block";
    }

    titleLabel = document.getElementById("program-title");
    if (programData.canEditProgram) {
        titleLabel.classList.add("editable");
        titleLabel.addEventListener("click", function (event) {
            event.preventDefault();

            titleInput.value = this.innerText;
            titleLabel.parentNode.insertBefore(titleInput, titleLabel);
            titleLabel.parentNode.removeChild(titleLabel);
            titleInput.focus();
        });
    }

    //Dynamically update sections of the page if it's not an unsaved program
    if (!programData.unsaved) {
        //Set program author data
        document.getElementById("program-author-link").innerText = programData.author.displayName;
        document.getElementById("program-author-link").setAttribute("href", "/user/" + programData.author.username);

        //Show buttons that need to be dynamically shown
        if (programData.canEditProgram) {
            document.getElementById("publish-button").style.display = "block";
        }
        if (programData.author.id === userData.id) {
            document.getElementById("delete-button").style.display = "block";
        }

        //Set vote count and event listeners.
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

        //Set "Based on" link
        if (programData.parent) {
            document.getElementById("parent-program-link").href = "/program/" + programData.parent.id;
            document.getElementById("parent-program-link").innerText = programData.parent.title;
        }

        //Set created and published dates
        document.getElementById("created-date").innerHTML = dateToString(programData.created);
        if (programData.lastPublished) {
            document.getElementById("published-date").innerHTML = dateToString(programData.lastPublished);
        }else {
            document.getElementById("published").style.display = "none";
        }

        //Set View Fullscreen link
        document.getElementById("view-fullscreen-link").href = "/program/" + programData.id + "/fullscreen";

        //Create the collaborator popup and button
        createCollaboratePopup();
        document.getElementById("collaborate-button").addEventListener("click", function(e) {
            e.preventDefault();

            var collaboratePopup = document.getElementById("collaborate-popup");
            if (collaboratePopup.style.display === "block") {
                collaboratePopup.style.display = "none";
            }else {
                collaboratePopup.style.display = "block";
            }
        });
    }else {
        //Page elements that get removed on a new program page
        var toRemove = ["vote-table", "comment-wrap", "updated-date", "view-fullscreen", "program-author", "fork-button", "collaborate-button"];

        for (var i = 0; i < toRemove.length; i++) {
            var el = document.getElementById(toRemove[i]);
            el.parentNode.removeChild(el);
        }
    }

    if (programData.unsaved || !programData.parent) {
        var p = document.getElementById("parent-program");
        p.parentNode.removeChild(p);
    }
});

window.addEventListener("load", function () {
    initMd();

    //Only bring in comments if it's not an unsaved program
    if (!programData.unsaved) {
        var req = new XMLHttpRequest();
        req.open("GET", "/api/program/" + programData.id + "/comments");
        req.addEventListener("load", function () {
            var data = JSON.parse(this.response);
            if (data && data.success) {
                displayComments(data.comments);
            }
        });
        req.send();
    }

    window.addEventListener("hashchange", hashUpdated);

    //Run program on window load. That way Ace is definitely loaded.
    runProgram();
});
