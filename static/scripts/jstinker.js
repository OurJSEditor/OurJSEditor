document.addEventListener("DOMContentLoaded", function() {

    // RUN Button
    document.getElementById("btnRun").addEventListener("click", function(event) {
        event.preventDefault();

        var previewDoc = window.frames[0].document;

        var css    = ace.edit("css-editor").getSession().getValue();
        var script = ace.edit("js-editor").getSession().getValue();
        var html   = ace.edit("html-editor").getSession().getValue();

        previewDoc.write("<!DOCTYPE html>");
        previewDoc.write("<html>");
        previewDoc.write("<head>");
        previewDoc.write("<style type='text/css'>" + css + "</style>");

        var selectJSRun = document.getElementById("selectJSRun").value;

        if (selectJSRun === "onLoad")
            previewDoc.write("<script type='text/javascript'>window.onload = function() {" + script + "\n}</script>");
        //else if (selectJSRun === "onDomready")
        //
        else if (selectJSRun === "inHead")
            previewDoc.write("<script type='text/javascript'>" + script + "</script>");
        previewDoc.write("</head>");
        previewDoc.write("<body>");
        previewDoc.write(html);
        if (selectJSRun === "inBody")
            previewDoc.write("<script type='text/javascript'>" + script + "</script>");
        previewDoc.write("</body>");
        previewDoc.write("</html>");
        previewDoc.close();
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
