/**
 * a.custom.js
 */
function printer(content){
    /*
        Print for reports & Forms.  Tested in Chrome, Firefox & IE9
        load the screen content without header & footer in a new window
    */
	var baseURL = document.location.href.split("?")[0];
	baseURL = baseURL + "?theme=off&mimetype=text/html";
    if (content.toLowerCase() == 'report'){
        var baseArguments = $(window).data('Report001').baseArguments;
        for(cellName in baseArguments){
            baseURL = baseURL + "&" + cellName + "=" + baseArguments[cellName];
        }
    }
	window.open(baseURL, 'windowname1', 'width=600, height=770'); 
	return false;
}

function wait_for_jst(){
    /*
        delays the calling of browser print action by a second.
		the delay is to make it work properly in Firefox & IE
    */
	setTimeout("window.print()",1000);
}

function export2PDF(){
    /*
        Convert HTML to PDF using the GAE's experimental Conversion API
        This reads the external css and makes it as inline, 
        and sends the HTML for conversion to PDF.
    */
    var applicationCss = ''
    var globalcss = ''
    var themecss = ''

    $.ajax({ url: "/static/css/theme.css",
    async:false,
    success: function(data){
            globalcss = data
    }});
    
    $.ajax({ url: "/static/css/Application.css",
    async:false,
    success: function(data){
            applicationCss = data
         }});

	var pdfButton = document.getElementById('pdfdownload');
	pdfButton.parentElement.removeChild(pdfButton);
	
    var headStr = "<head> <style type='text/css'>"+applicationCss+" "+globalcss+" </style></head>"
    var htmlContent = $(".portlet .content").html();

    document.forms["pdfForm"].src.value = headStr + htmlContent;
    document.forms["pdfForm"].submit();
}