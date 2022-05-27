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
    return '/markdown' + pathName
}

function baseName(str)
{
    var base = new String(str).substring(str.lastIndexOf('/') + 1); 
    if(base.lastIndexOf(".") != -1) {
        base = base.substring(0, base.lastIndexOf("."));
    }

    return base;
}

function getMarkdownUrl() {
    var host = window.location.host
    var protocol = window.location.protocol
    var baseURL = protocol + '//' + host
    var markdownURL = baseURL + getMarkdownPath()
    return markdownURL
}

function getMarkdownContent(pathName, callback) {
    var markdownURL = getMarkdownUrl()
    // var markdownURL = 'http://kancloud.nordata.cn/2019-02-07-license.md'
    $.get(markdownURL, function(result){
        console.log(result)
        Loading.close();
        callback(baseName(pathName), result)
    });
}

function confirmSave(markdownStr, successAction, failAction) {
    $.confirm({  
        'title': 'Save Confirmation',  
        'content': 'Do you want to save these changes?',  
        'buttons': {  
            'Yes': {  
                'class': 'blue',  
                'action': function() {
                    successAction(markdownStr);
                }, 
            },  
            'No': {  
                'class': 'gray',  
                'action': failAction
            }  
        }  
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

    stackedit.on('close', () => {
        var markdownStr = window.sessionStorage.getItem(getMarkdownPath())
        confirmSave(
            markdownStr, 
            function(markdownStr){
                var markdownBlob = new Blob([markdownStr], {
                    type: 'text/plain'
                });
                var formData = new FormData();                
                formData.append('markdown', markdownBlob);
                if (markdownStr) {
                    $.ajax({
                        type: 'PUT',
                        url: getMarkdownUrl(),
                        data: formData,
                        processData: false,
                        contentType: false
                    }).done(function () {
                        Loading.open({
                            theme: 'sk-circle',
                            message: "<h4 class=''>" + "Rendering Your Markdown..." +  " </h4> "
                        });
                        console.log('SUCCESS');
                    }).fail(function (msg) {
                        console.log(msg);
                    });
                }
            },
            function() {
                console.log('Cancel')
            }
        )
    })

    stackedit.on('fileChange', (file) => {
        var markdownStr = file.content.text
        window.sessionStorage.setItem(getMarkdownPath(), markdownStr)
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