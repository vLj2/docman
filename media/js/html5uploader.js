function uploader(place, status, targetPHP) {	
	// Upload image files
	upload = function(file) {
		// Firefox 3.6, Chrome 6, WebKit
		
		// show overlay
		$('div#overlay').show();
		$('div#overlay').removeClass('oSuccess oFailure');  					
		$('div#overlay div.oContent h3').html('Please wait, starting upload.. <img class="loader" style="margin-left: 5px;display:inline;" src="'+MEDIA_URL+'img/new/loader_fafafa.gif" /> ');
		$('div#overlay div.oContent p:first').html('We should be starting soon! (If your browser sucks, we are already uploading. Please give me a second!)');											
		//$('div#overlay').show('scale', 50);		
		//$('div#overlay').show();				
		$('div#overlay').modal('show', {keyboard:true})
		
		if(window.FileReader) { 
			// Once the process of reading file
			this.loadEnd = function() {
				bin = reader.result;
				if (bin == '' || !bin) {

					$('div#overlay').removeClass('oSuccess oFailure');
					$('div#overlay').addClass('oFailure');
					$('div#overlay div.oContent h3').html('An error occurred');
					$('div#overlay div.oContent p:first').html('You tried to upload an invalid file. Most often, your file is empty or not accessible. <a href="javascript:;" onclick="resetUploadWindow()">Cancel</a>');
					$('div#overlay div.oContent div.progressbar').hide();
					$('div#overlay div.oContent div.progress').hide();
					$("div#overlay div.oContent div.progressDetail").hide();

					return false;
				}

				xhr = new XMLHttpRequest();

				xhr.upload.addEventListener('progress', loadProgress, false);
				
				xhr.open('POST', targetPHP+'?up=true&base64=true', true);
				xhr.setRequestHeader('UP-FILENAME', file.name);
				xhr.setRequestHeader('UP-SIZE', file.size);
				xhr.setRequestHeader('UP-TYPE', file.type);
				xhr.setRequestHeader('courseId', jsCourse);
				if (typeof(jsDocument) != 'undefined') {
					xhr.setRequestHeader('documentId', jsDocument);
				}
				//xhr.send(window.btoa(bin));
				xhr.send(file);

				if (status) {
					xhr.onreadystatechange = function(){
						if (xhr.readyState == 4) {
							//console.log(xhr.responseText);
							result = $.parseJSON(xhr.responseText);	
							if (result.success) {
								$('div#overlay').removeClass('oSuccess oFailure');  
								$('div#overlay').addClass('oSuccess');							
								$('div#overlay div.oContent h3').html('Upload complete!');												
								$('div#overlay div.oContent p:first').html(result.ok);
								$('div#overlay div.oContent div.progressbar').hide();
								$('div#overlay div.oContent div.progress').hide();
								$("div#overlay div.oContent div.progressDetail").hide();
								if (result.revision) { 
									$(location).attr('href','/document/'+jsDocument+'/');
								} else {							
									/** show document information form **/
									$('div#overlay form[name=uploadDetails] input[name=tags]').val(result.tags);
									$('div#overlay form[name=uploadDetails] input[name=documentId]').val(result.documentId);
									$('div#overlay form[name=uploadDetails] input[name=name]').val(result.documentName);
									$('div#overlay form[name=uploadDetails] input[name=tags]').focus();	
									$('div#overlay div.uploadDetails').show();							
								}
							} else {
								$('div#overlay').removeClass('oSuccess oFailure');  
								$('div#overlay').addClass('oFailure');							
								$('div#overlay div.oContent h3').html('Upload failed!');												
								$('div#overlay div.oContent p:first').html(result.error);							
								$('div#overlay div.oContent div.progressbar').hide();
								$('div#overlay div.oContent div.progress').hide();
								$("div#overlay div.oContent div.progressDetail").hide();
							}
						} else {
							$('div#overlay').removeClass('oSuccess oFailure');  
							$('div#overlay div.oContent h3').html('Upload in progress..');
							$('div#overlay div.oContent p:first').html('Progressing file..');							
						}
					};
				}
			}

			// Loading errors
			this.loadError = function(event) {
				switch(event.target.error.code) {
					case event.target.error.NOT_FOUND_ERR:
						$('div#overlay').removeClass('oSuccess oFailure');  
						$('div#overlay').addClass('oFailure');
						$('div#overlay div.oContent h3').html('An error occurred');
						$('div#overlay div.oContent p:first').html('File not found!');
						$('div#overlay div.oContent div.progressbar').hide();
						$('div#overlay div.oContent div.progress').hide();						
						$("div#overlay div.oContent div.progressDetail").hide();
					break;
					case event.target.error.NOT_READABLE_ERR:
						$('div#overlay').removeClass('oSuccess oFailure');  
						$('div#overlay').addClass('oFailure');					
						$('div#overlay div.oContent h3').html('An error occurred');
						$('div#overlay div.oContent p:first').html('File not readable!');					
						$('div#overlay div.oContent div.progressbar').hide();
						$('div#overlay div.oContent div.progress').hide();
						$("div#overlay div.oContent div.progressDetail").hide();					
					break;
					case event.target.error.ABORT_ERR:
					break; 
					default:
						$('div#overlay').removeClass('oSuccess oFailure');  
						$('div#overlay').addClass('oFailure');					
						$('div#overlay div.oContent h3').html('An error occurred');
						$('div#overlay div.oContent p:first').html('Read error.');
						$('div#overlay div.oContent div.progressbar').hide();
						$('div#overlay div.oContent div.progress').hide();	
						$("div#overlay div.oContent div.progressDetail").hide();						
				}
			}			
			
			reader = new FileReader();
			// Firefox 3.6, WebKit
			if(reader.addEventListener) { 
				reader.addEventListener('loadend', this.loadEnd, false);
				if (status != null) {
					reader.addEventListener('error', this.loadError, false);
					//reader.addEventListener('progress', this.loadProgress, false);
				}			
			// Chrome 7
			} else { 
				reader.onloadend = this.loadEnd;
				if (status != null) {
					reader.onerror = this.loadError;
					//reader.onprogress = this.loadProgress;
				}
			}

			// The function that starts reading the file as a binary string
			reader.readAsBinaryString(file);
			
		// Safari 5 does not support FileReader
		} else {
			//console.log('Safari upload match!');
			xhr = new XMLHttpRequest();
			xhr.upload.addEventListener('progress', loadProgress, false);				
			xhr.open('POST', targetPHP+'?up=true', true);
			xhr.setRequestHeader('UP-FILENAME', file.name);
			xhr.setRequestHeader('UP-SIZE', file.size);
			xhr.setRequestHeader('UP-TYPE', file.type);
			xhr.setRequestHeader('courseId', jsCourse);
			if (typeof(jsDocument) != 'undefined') {
				xhr.setRequestHeader('documentId', jsDocument);
			}			
			xhr.send(file); 

			if (status) {
			
				xhr.onreadystatechange = function(){
					if (xhr.readyState == 4) {
						//console.log(xhr.responseText);
						result = $.parseJSON(xhr.responseText);	
						if (result.success) {
							$('div#overlay').removeClass('oSuccess oFailure');  
							$('div#overlay').addClass('oSuccess');							
							$('div#overlay div.oContent h3').html('Upload complete!');												
							$('div#overlay div.oContent p:first').html(result.ok);
							$('div#overlay div.oContent div.progressbar').hide();
							$('div#overlay div.oContent div.progress').hide();
							$("div#overlay div.oContent div.progressDetail").hide();
							if (result.revision) { 
								$(location).attr('href','/document/'+jsDocument+'/');
							} else {							
								/** show document information form **/
								$('div#overlay form[name=uploadDetails] input[name=tags]').val(result.tags);
								$('div#overlay form[name=uploadDetails] input[name=documentId]').val(result.documentId);
								$('div#overlay form[name=uploadDetails] input[name=name]').val(result.documentName);
								$('div#overlay form[name=uploadDetails] input[name=tags]').focus();	
								$('div#overlay div.uploadDetails').show();							
							}
						} else {
							$('div#overlay').removeClass('oSuccess oFailure');  
							$('div#overlay').addClass('oFailure');							
							$('div#overlay div.oContent h3').html('Upload failed!');												
							$('div#overlay div.oContent p:first').html(result.error);							
							$('div#overlay div.oContent div.progressbar').hide();
							$('div#overlay div.oContent div.progress').hide();
							$("div#overlay div.oContent div.progressDetail").hide();
						}
					} else {
						$('div#overlay').removeClass('oSuccess oFailure');  
						$('div#overlay div.oContent h3').html('Upload in progress..');
						$('div#overlay div.oContent p:first').html('Progressing file..');							
					}
				};			
			
				/*$('div#overlay').removeClass('oSuccess oFailure');  
				$('div#overlay').addClass('oSucces');			
				$('div#overlay div.oContent h3').html('Upload complete!');
				$('div#overlay div.oContent p:first').html('Loaded 100%');
				$('div#overlay div.oContent div.progressbar').hide();
				$('div#overlay div.oContent div.progress').hide();					
				$("div#overlay div.oContent div.progressDetail").hide();*/
			}
		}				
	}

	// Function drop file
	this.drop = function(event) {
		$('#'+place).removeClass('hover');
		event.preventDefault();
		var dt = event.dataTransfer;
		var files = dt.files;

		if (files.length > 1) {
			alert('Currently, multiple file upload is not yet supported due to a browser issue.');
		}

		$('a#resetUploadWindow').trigger('click');

		upload(files[0]);

		/*for (var i = 0; i<files.length; i++) {
		var file = files[i];
		upload(file);
		}*/
	}

	// The inclusion of the event listeners (DragOver and drop)
	this.uploadPlace =  document.getElementById(place);
	this.uploadPlace.addEventListener("dragover", function(event) {
		$('#'+place).addClass('hover');
		event.stopPropagation(); 
		event.preventDefault();
	}, true);
	this.uploadPlace.addEventListener("dragleave", function(event) {
		$('#'+place).removeClass('hover');
	}, true);	
	this.uploadPlace.addEventListener("drop", this.drop, false); 
}


largeFileWarningBool = false;

// Reading Progress
loadProgress = function(event) {
	$('div#overlay div.oContent div.progressbar').show();
	$('div#overlay div.oContent div.progress').show();					
	$("div#overlay div.oContent div.progressDetail").show();
	var percentage = Math.round((event.loaded * 100) / event.total);
	$('div#overlay').removeClass('oSuccess oFailure');  					
	$('div#overlay div.oContent h3').html('Upload in progress.. <img class="loader" style="margin-left: 5px;display:inline;" src="'+MEDIA_URL+'img/new/loader_fafafa.gif" /> ');
	$('div#overlay div.oContent p:first').html('Please give me a second to upload and analyze the file. <span id="largeFileWarningSpan"></span>');	
	$("div#overlay div.oContent div.progressbar").progressbar({ value: percentage });
	$("div#overlay div.oContent div.progress").html(percentage+'%');
	$("div#overlay div.oContent div.progressDetail").html(Math.round(event.loaded/1024)+' KB / '+Math.round(event.total/1024)+' KB');
	
	if (percentage >= 95 && !largeFileWarningBool) {
		largeFileWarningBool = true;
		setTimeout("largeFileWarning()", 7000);
	}
}

largeFileWarning = function() {
	$('div#overlay div.oContent p:first span#largeFileWarningSpan').append('<p><em>This seems to be a large file. It may take some time to analyze it.</em></p>');
}
