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
});
