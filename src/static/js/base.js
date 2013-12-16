/*
Created on Jul 26, 2012

@author: bratface
*/
overlay = function(url) {
	$('#overlay').load(url, function() {
		$('#overlay').overlay().load();
	});
}

function asCurrency(nStr)
{
	nStr = nStr.toFixed(2);
	nStr += '';
	x = nStr.split('.');
	x1 = x[0];
	x2 = x.length > 1 ? '.' + x[1] : '';
	var rgx = /(\d+)(\d{3})/;
	while (rgx.test(x1)) {
		x1 = x1.replace(rgx, '$1' + ',' + '$2');
	}
	return x1 + x2;
}

$(document).ready(function(){ 
	// make page automagically recognize dropdowns html configs
	$('body').dropdown();
	
	// date functionality
	$("input.date").not("[readonly='readonly']").datepicker({
		format: "mm/dd/yyyy",
		buttonText: "...",
		buttonImage: '/static/icons/iconic/black/calendar_8x8.png',
		showOn: "button",
	}).datepicker('hide').change(function(e, date) {
		$(this).blur();
	}).blur(function() {
		//$(this).datepicker("hide");
	});
	
	// make all textareas autoresizing
	$('textarea').autoResize({
	    animate: false,
	    extraSpace: 0,
	});
	
	var suggestions_url = $("input#suggestions-url").val();
	// enable search from the top bar
	$("#search").autocomplete({
		source: suggestions_url,
		minLength: 2,
		select: function(e, ui) {
			window.location.href = ui.item.url;
		},
	}).data("autocomplete")._renderItem = function(ul, item) {
		var li = null;
		if (item.more) {
			li = $("<li class='more suggestion'>").data("item.autocomplete", item)
				.append("<hr><a><span class='name'>" + item.name + "</span></a>")
		} 
		else {
			li = $("<li class='suggestion'>").data("item.autocomplete", item)
				.append("<a><span class='type'>" + item.type + 
						"</span><span class='name'>" + item.name + 
						"</span> <span class='summary'> " + 
						item.summary + "</span></a>") 
		}
        return li.appendTo( ul );
	};
	
	// default 'overlay' or in classical terms, a dialog 
	$('#overlay').overlay({
	    mask: {
		   	color: '#333',
   			loadSpeed: 200,
   			opacity: 0.50
   		},
   		top: "10%",
   		load: false,
   		closeOnClick: true,
   		onClose: function(e) {
   			// make it refresh the page if an input refresh is sent in
   			if ($('#overlay').find('input.refresh').length > 0) {
   				location.reload();
   			}
   		},
	});

	$('#overlay').on('click', 'div.button.close', function() {
		$('#overlay').overlay().close();
	});
	
	// enables .trigger class objects to load a dialog and loading whatever is in the href
	// as its contents
	$('body').on('click', 'a.trigger', function(e){
		$('#overlay').load($(this).attr("href"), function(){
			$('#overlay').overlay().load();
		});
		e.preventDefault();
	});
	
	// enable forms to submit via ajax and load responses onto the form itself
	$('body').on('click', 'form.ajax div.button.submit', function() {
		var form = $(this).closest('form');
		var url = form.attr('action');
		var params = form.serializeArray();
		form.load(url, params);
	});	
	
	var load_a = function(el) {
		$.ajax({
			url: $(el).attr('href'), 
			success: function(data){
				$(el).parent().replaceWith(data);
			},
			context: $(el),
		});
	}
	
	// enables .loader class objects to replace themselves with an ajax page on click
	$('body').on('click', 'li > a.clickloader', function(e) {
		e.preventDefault();
		load_a(this);
	});
	
	$('body').on('click', 'li > a.scrollloader', function(e) {
		e.preventDefault();
		load_a(this);
	});

	$(window).scroll(function(e) {
		$("a.scrollloader").each(function(i) {
			if (elementInViewport(this)) {
				load_a(this);
			}
		});
	});
	
	// autoload sequentially one at a time to avoid server overload.
	var autoload = function(autoloaders, i) {
		if (i >= autoloaders.length) {
			return;
		}
		var a = autoloaders[i]
		$.ajax({
			url: $(a).attr('href'), 
			success: function(data){
				$(a).replaceWith(data);
				autoload(autoloaders, i + 1); //recurse
			},
			context: $(a),
		});
	}
	
	var autoloaders = $.makeArray($('a.autoloader'));
	autoload(autoloaders, 0);
	
	// replace links with class 'autoloader' with whatever is in the href
//	$('a.autoloader').each(function() {
//		$.ajax({
//			url: $(this).attr('href'), 
//			success: function(data){
//				$(this).replaceWith(data);
//			},
//			context: $(this),
//		});
//	});
	
	// toggler links will show or hide target
	$('a.toggler').toggler();
	
	// collapse all and expand all
	$('a.collapse').click(function() {
		$('a.toggler').collapse();	
	});
	$('a.expand').click(function() {
		$('a.toggler').expand();	
	});

	// object archiving
	$('a.archive').click(function() {
		var yes = confirm('Are you sure you want to archive this object? \n WARNING: This operation cannot be undone.');
		return yes;
	});
});