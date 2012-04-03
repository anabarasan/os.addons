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
        This reads the external css & images and makes it as inline, 
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

function imageType(img){
    /*
     * Find the mime-type of image using extension.
     * This is ugly.  
     * Need to find a way to read file header.
    */
    var ext = img.src.split('.');
    ext = ext[ext.length - 1]
    switch (ext.toLowerCase()){
        case 'png':
            return 'image/png';
        case 'gif':
            return 'image/gif';
        case 'bmp':
            return 'image/bmp';
        case 'jpg':
            return 'image/jpeg';
        case 'jpeg':
            return 'image/jpeg';
    }
}

function encodeImage(img){
	/* Get Image Data 
	 * http://usejquery.com/posts/encode-images-for-offline-usage-with-html5-canvas 
	*/
    canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    context = canvas.getContext('2d');
    context.drawImage(img, 0, 0);
    return canvas.toDataURL(imageType(img));    
}

function convertInput2Image(src){
	var ip2img = document.createElement('img');
	ip2img.src = src;
	return ip2img;
}

function getImages(){
	var images = document.images;
	for (var i=0; i< images.length; i++){
		mimetype = imageType(images[i]);
		imagedata = encodeImage(images[i]);
		imgsrc = images[i].src;
	}
	//data to be added to query params
}

function getInputImages(){
	/* http://stackoverflow.com/questions/5351617/swap-all-images-on-page-via-one-link-jquery */
	$('input').attr('src',function(i, src){
		var img = convertInput2Image()
		mimetype = imageType(img);
		imagedata = encodeImage(img);
		imgsrc = src;
		});
	// data to be added to query params
}
