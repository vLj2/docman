$(document).ready(function(){
	jQuery.fn.stripTags = function() { return this.replaceWith( this.html().replace(/<\/?[^>]+>/gi, '') ); };
	
	sLoader = function() {
		$('.loader img').show();
	};
	hLoader = function() {
		$('.loader img').hide();
	};	
	
	 $("select#semesterSwitch").sb();
	 $("select#semesterSwitch").change(function() {
	 	$(location).attr('href','/semester/'+$(this).val()+'/');
	 });

	
	$('div.rating').raty({
	  half:  false,
	  cancel: false,
	  hintList:     ['Naja weisste..', 'Geht so', 'Brauchbar', 'Gut', 'SUPER JONGE!'],
	  path: '/media/img/',
	  starOn: 'str_full_lg.gif',
  	  starOff: 'str_none_lg.gif',
  	  number: 5,
  	  size: 17,
  	  start: parseInt($('#documentRating').html()),
	  click: function(score, evt) {
		sLoader();
		$.post("/rate/"+$('#documentId').html()+"/", { rating: score }, function(response) {
          if (!response.success) {
			alert(response.error)
          } else {
			// done rating
          }}, 'json');
		hLoader();
	  }
	});
	
	
	/*$('input[name=star1]').rating();*/
	
	//parseInt($('#documentRating').html())
	
	/*$('input[name=star1]').rating({
		callback: function(value, link){
			sLoader();
			$.post("/rate/"+$('#documentId').html()+"/", { rating: value }, function(response) {
	          if (!response.success) {
				alert(response.error)
	          } else {
				// done rating
	          }}, 'json');					
			hLoader();	
		},
		focus: function(value, link){
			var tip = $('#hover-tooltip');
			tip[0].data = tip[0].data || tip.html();
			tip.html(link.title || 'value: '+value);
		},
		blur: function(value, link){
			var tip = $('#hover-tooltip');
			$('#hover-tooltip').html(tip[0].data || '');
		}		
	});*/
	
	editMode = function() {
		sLoader();
		var desc = $('#documentDesc');
		var originalContent = desc.html();
		if (originalContent.match('Bisher wurde keine Beschreibung gespeichert'))
			var editContent = '';
		else
			var editContent = $('#documentDescClean').html();
		desc.html('<div id="documentDescEdit"><div id="successResponse" class="message" style="display:none"></div><textarea name="desc">'+editContent+'</textarea><br /><input type="submit" id="editSave" value="Speichern" /> <input type="submit" id="editAbort" value="Abbrechen" /></div>');
		hLoader();
		$('#editAbort').click(function() {
			sLoader();
			desc.html(originalContent);
			hLoader();
		});
		$('#editSave').click(function() {
			sLoader();
			$.post("/edit/"+$('#documentId').html()+"/", { doEdit: 'desc', desc: $('div#documentDescEdit textarea[name=desc]').val() }, function(response) {
          if (!response.success) {
		       	$('#successResponse').removeClass('ok');		            
          	$('#successResponse').addClass('error');
          	$('#successResponse').html(response.error);
          	$('#successResponse').show();
          } else {
	       	$('#successResponse').removeClass('error');		            
          	$('#successResponse').addClass('ok');
          	$('#successResponse').html("Gespeichert!");
          	$('#successResponse').show();
          	if (response.desc_clean != '') {
	          	desc.html(response.desc);
	          } else {
	          	desc.html('<p class="info">Bisher wurde keine Beschreibung gespeichert.</p>');
	          }
          	$('#documentDescClean').html(response.desc_clean)
          }
					}, 'json');						
			hLoader();		
		});
	};
	
	$('#updatedFileUpload').uploadify({
	    'uploader'  : '/media/bin/uploadify.swf',
	    'script'    : '/upload/',
	    'cancelImg' : '/media/img/cancel.png',
	    'folder'    : '/media/hdd',
		'auto'      : true,
		'displayData': 'percentage', /*speed*/
		'scriptData': {'documentId': $('span#documentId').html(), 'sessionId': $.cookie('sessionid')},
    	onError 	: function (event,ID,fileObj,errorObj) {
			hLoader();
    	},
    	onComplete	: function uploadifyComplete(evt, queueid, obj, response, data){
    		hLoader();
            response = jQuery.parseJSON(response);
            if (!response.success) {
            	$('#uploadResponse').addClass('error');
            	$('#uploadResponse').html(response.error);
            	$('#uploadResponse').show();
            	$('#fileUpload').uploadifyClearQueue();
            } else {
            	$('#uploadResponse').addClass('ok');
            	$('#uploadResponse').html(response.ok);
            	$('#uploadResponse').show();
            	$('#updatedFileUpload').uploadifyClearQueue();            
            	$('#uploadContainer form').remove();
            	$(location).attr('href','/document/'+$('span#documentId').html()+'/');
            }
        },
        onSelect : function() {
           	$('#uploadResponse').hide();        	
	       	$('#uploadResponse').removeClass('error');
	       	$('#uploadResponse').removeClass('ok');
           	$('#uploadResponse').html('');
        }, 
        onOpen	: function() {
        	sLoader();
        }
	});
	
	$('#fileUpload').uploadify({
	    'uploader'  : '/media/bin/uploadify.swf',
	    'script'    : '/upload/',
	    'cancelImg' : '/media/img/cancel.png',
	    'folder'    : '/media/hdd',
		'auto'      : true,
		'displayData': 'percentage', /*speed*/
		'scriptData': {'courseId': $('input[name=courseId]').val(), 'sessionId': $.cookie('sessionid')},
    	onError 	: function (event,ID,fileObj,errorObj) {
			hLoader();
    	},
    	onComplete	: function uploadifyComplete(evt, queueid, obj, response, data){
    		hLoader();
            response = jQuery.parseJSON(response);
            if (!response.success) {
            	$('#uploadResponse').addClass('error');
            	$('#uploadResponse').html(response.error);
            	$('#uploadResponse').show();
            	$('#fileUpload').uploadifyClearQueue();
            } else {
       			$('.uploadContainers').hide();	
				$('#uploadContainer-tab2').show();				
				$('#uploadContainer-tab2 input[name=tags]').val(response.tags);
				$('input[name=documentId]').val(response.documentId);
				$('input[name=name]').val(response.documentName);
				$('#uploadContainer-tab2 input[name=tags]').focus();
            	$('#successResponse').addClass('ok');
            	$('#successResponse').html(response.ok);
            	$('#successResponse').show();
            	$('#fileUpload').uploadifyClearQueue();            
            }
        },
        onSelect : function() {
           	$('#uploadResponse').hide();        	
	       	$('#uploadResponse').removeClass('error');
	       	$('#uploadResponse').removeClass('ok');
           	$('#uploadResponse').html('');
        }, 
        onOpen	: function() {
        	sLoader();
        }
	});
	$('#uploadContainer .cancelButton').click(function(){
		sLoader();
		$('#uploadContainer').hide();		
		$('.uploadContainers').hide();
		hLoader();		
	});
	$('.uploadLink a.upload').click(function() {
		sLoader();
		$('.uploadContainers').hide();	
		$('#uploadContainer-tab1').show();
		$('#uploadContainer').show();
		hLoader();
	});
	
	uploadNew = function() {
		sLoader();
		$('.uploadContainers').hide();	
		$('#uploadContainer-tab1').show();
		$('#uploadContainer').show();
		hLoader();		
	};
	
	$('form[name=uploadDetails]').submit(function(f) {
		sLoader();	
		$.post("/file-info/", { documentId: $('form[name=uploadDetails] input[name=documentId]').val(), desc: $('form[name=uploadDetails] textarea[name=desc]').val(), name: $('form[name=uploadDetails] input[name=name]').val(), tags: $('form[name=uploadDetails] input[name=tags]').val() }, function(response) {
            if (!response.success) {
		       	$('#successResponse').removeClass('ok');		            
            	$('#successResponse').addClass('error');
            	$('#successResponse').html(response.error);
            	$('#successResponse').show();
            } else {
		       	$('#successResponse').removeClass('error');		            
            	$('#successResponse').addClass('ok');
            	$('#successResponse').html("Gespeichert! Bitte warten..");
            	$('#successResponse').show();            
            	$(location).attr('href','/document/'+$('form[name=uploadDetails] input[name=documentId]').val()+'/');
            }	           		
		}, 'json');
		hLoader();	
	});


});