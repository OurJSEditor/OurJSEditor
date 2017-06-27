var titleLabel;
var titleInput = document.createElement("input");
titleInput.setAttribute("maxlength", "45");
titleInput.setAttribute("id", "program-title");
titleInput.addEventListener("change", removeTitleInput);
titleInput.addEventListener("blur", removeTitleInput);
titleInput.addEventListener("keypress", function (e) {
    //If the enter or return key is pressed.
    if (e.which === 13) {
        //Fires the change event, which normally only fires if the text is different
        titleInput.dispatchEvent(new Event("change"));
    }
});

function removeTitleInput (event) {
    if (titleInput.parentNode === null) return;
    titleLabel.innerText = titleInput.value;
    titleInput.parentNode.insertBefore(titleLabel, titleInput);
    titleInput.parentNode.removeChild(titleInput);
}

function deleteConfirm () {
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

document.addEventListener("DOMContentLoaded", function() {

    // RUN Button
    document.getElementById("btnRun").addEventListener("click", function(event) {
        event.preventDefault();

        var css    = ace.edit("css-editor").getSession().getValue();
        var script = ace.edit("js-editor").getSession().getValue();
        var html   = ace.edit("html-editor").getSession().getValue();

        var combinedCode = "";

        combinedCode += "<!DOCTYPE html>";
        combinedCode += "<html>";
        combinedCode += "<head>";
        combinedCode += "<style type='text/css'>" + css + "</style>";

        var selectJSRun = document.getElementById("selectJSRun").value;

        if (selectJSRun === "onLoad")
            combinedCode += "<script type='text/javascript'>window.onload = function() {" + script + "\n}</script>";
        //else if (selectJSRun === "onDomready")
        //
        else if (selectJSRun === "inHead")
            combinedCode += "<script type='text/javascript'>" + script + "</script>";
        combinedCode += "</head>";
        combinedCode += "<body>";
        combinedCode += html;
        if (selectJSRun === "inBody")
            combinedCode += "<script type='text/javascript'>" + script + "</script>";
        combinedCode += "</body>";
        combinedCode += "</html>";

        document.getElementById("preview").contentWindow.postMessage(combinedCode, "*");
    });

    // Preview code on page load
    document.getElementById("btnRun").click();

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
});
