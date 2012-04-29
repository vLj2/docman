$(document).ready(function(){
	jQuery.fn.stripTags = function() { return this.replaceWith( this.html().replace(/<\/?[^>]+>/gi, '') ); };
	
	if ($('div#dropZone').height() > 0 ) {
		if (!$.browser.msie) {
			new uploader('dropZone', true, '/test-upload/', 'list');
		}
	}

	if ($('div#IEdropZone').height() > 0 ) {
		$('div#IEdropZone').click(function() {
			$('div#IEoverlay, div.uploadDetails').show();
		});
	}
	
	uiMessage = function(type, text) {
		$('body').prepend('<div class="message '+type+'">'+text+'</div>');
		setTimeout(function(){$('div.message').hide('blind');}, 2500);
	}
	
	$("select#semesterSwitch").sb();
	$("select#semesterSwitch").change(function() {
		$(location).attr('href','/semester/'+$(this).val()+'/');
	});
	
	$('span.rating').raty({
		half:  false,
		cancel: false,
		hintList: ['Naja weisste..', 'Geht so', 'Brauchbar', 'Gut', 'SUPER JONGE!'],
		path: '/media/img/new/',
		starOn: 'star_full.png',
		starOff: 'star_empty.png',
		number: 5,
		size: 16,
		start: parseInt($('#documentRating').html()),
		click: function(score, evt) {
			$.post("/rate/"+$('#documentId').html()+"/", { rating: score }, function(response) {
				if (!response.success) {
					uiMessage('error', response.error);
				}
			}, 'json');
		}
	});
	
	resetUploadWindow = function() {
		$(':input', 'form[name=uploadDetails]').not(':button, :submit, :reset, :hidden').val('');
		$('div#overlay div.uploadDetails, div#overlay').hide();
		$('div#overlay h3, div#overlay p').html('');
	};

	$('a#resetUploadWindow').click(function(){
		resetUploadWindow();
	});

	$('a#resetIEUploadWindow').click(function(){
		$(':input', 'form[name=uploadDetails]').not(':button, :submit, :reset, :hidden').val('');
		$('div#IEoverlay div.uploadDetails, div#IEoverlay').hide();
		$('div#IEoverlay h3, div#IEoverlay p').html('');
	});		
	
	$('a#resetEditWindow').click(function(){
		//$('div#editOverlay').hide();
		$('div#editOverlay').modal('hide')
	});	

	$('a#resetPadWindow').click(function(){
		$('div#padOverlay').hide();
	});		

	showCreatePadWindow = function() {
		$('div#padOverlay form :input[type=text]').val("");
		$('div#padOverlay').show();
	}
	
	editMode = function() {
		//$('div#editOverlay').show();
		$('div#editOverlay').modal('show', {keyboard:true})
	}	
		
	$('form[name=uploadDetails]').submit(function(f) {
		$('form[name=uploadDetails] img.loader').show();
		$.post("/file-info/", { is_lecturer_visible: $('form[name=uploadDetails] input[name=is_lecturer_visible]:checked').val(),documentId: $('form[name=uploadDetails] input[name=documentId]').val(), desc: $('form[name=uploadDetails] textarea[name=desc]').val(), name: $('form[name=uploadDetails] input[name=name]').val(), tags: $('form[name=uploadDetails] input[name=tags]').val() }, 
			function(response) {
				if (!response.success) {
					$('form[name=uploadDetails] img.loader').hide();
					uiMessage('error', response.error);
				} else {
					// we will display this after forwarding to the document.
					//uiMessage('success', response.ok);
					$('form[name=uploadDetails] img.loader').hide();
					$(location).attr('href','/document/'+$('form[name=uploadDetails] input[name=documentId]').val()+'/');
				}
			}, 'json');
	});

	$('img#closeLatestUploads').click(function(){
		$.post("/account-ajax/", { show_latest_uploads: 'no' }, function(response) {
			if (response.success) {
				$('div#latestUploadsBox').hide('blind');
			} else {
				uiMessage('error', 'An error occured! Please try again later.');
			}
		}, 'json');
	});
	
	// evaluation
	$('form[name=evaluation]').submit(function(f) {
		$('form[name=evaluation] img.loader').show();
		$.post("/survey/", { grade: $('form[name=evaluation] select[name=grade]').val(), upload: $('form[name=evaluation] select[name=upload]').val(), layout: $('form[name=evaluation] select[name=layout]').val(), zip: $('form[name=evaluation] select[name=zip]').val(), text: $('form[name=evaluation] textarea[name=text]').val()}, 
			function(response) {
				if (!response.success) {
					$('form[name=evaluation] img.loader').hide();
					uiMessage('error', response.error);
				} else {
					// we will display this after forwarding to the document.
					uiMessage('success', response.ok);
					$('form[name=evaluation] img.loader').hide();
					$('#surveyOverlay').hide();;
				}
			}, 'json');
	});	
	
});
