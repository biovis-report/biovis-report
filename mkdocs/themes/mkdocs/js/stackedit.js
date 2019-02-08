$(document).ready(function() {
    $("#edit-btn").click(function(){
        Loading.open({
            theme: 'sk-rect',
            message: "<h4 class=''>" + "Open Markdown File" +  " </h4> "
        });
        getMarkdownContent(getMarkdownPath(), openStackedit)
    }); 
});

function getMarkdownPath() {
    const regex = /\/[-\w\/_]+\.html/;
    var pathName = window.location.pathname
    var matched = pathName.match(regex);
    if (matched == undefined) {
        pathName = pathName + 'index.md'
    } else {
        pathName = pathName.replace('html', 'md')
    }
    return pathName
}

function baseName(str)
{
    var base = new String(str).substring(str.lastIndexOf('/') + 1); 
    if(base.lastIndexOf(".") != -1) {
        base = base.substring(0, base.lastIndexOf("."));
    }

    return base;
}

function getMarkdownContent(pathName, callback) {
    var host = window.location.host
    var protocol = window.location.protocol
    var baseURL = protocol + '//' + host
    var markdownURL = baseURL + pathName
    // var markdownURL = 'http://kancloud.nordata.cn/2019-02-07-license.md'
    $.get(markdownURL, function(result){
        console.log(result)
        Loading.close();
        callback(baseName(pathName), result)
    });
}

function openStackedit(fileName, content) {
    const stackedit = new Stackedit();

    stackedit.openFile({
        name: fileName,
        content: {
            text: content
        },
    })

    stackedit.on('close', (file) => {

    })

    stackedit.on('fileChange', (file) => {
        $('#notify-btn').notify(
            "File will be saved when you close the editor.", 
            "info",
            { 
                globalPosition: 'top center',
                autoHideDelay: 8000,
                arrowShow: false
            }
        );
    })
}