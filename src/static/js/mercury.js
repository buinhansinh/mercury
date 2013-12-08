KEYCODES = {
	ENTER: 13,
	ESCAPE: 27,
}

// similar to python string format function
String.prototype.format = function () {
	var i = 0, args = arguments;
	return this.replace(/{}/g, function () {
		return typeof args[i] != 'undefined' ? args[i++] : '';
	});
};

mercury_form_submitted = false;
submit = function(form) {
	if (!mercury_form_submitted) {
		form.submit();
		mercury_form_submitted = true;
	}
} 

function elementInViewport(el) {
    var rect = el.getBoundingClientRect();

    return (
        ((rect.top >= 0 && rect.top <= $(window).height()) ||
        (rect.bottom >= 0 && rect.top <= $(window).height())) &&
        ((rect.left >= 0 && rect.top <= $(window).width()) ||
        (rect.right >= 0 && rect.top <= $(window).width()))
    );
}

function intcomma(x) {
    return x.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Neeeded for ajax to work with Django CSRF
$(document)
	.ajaxSend(
		function(event, xhr, settings) {
			function getCookie(name) {
				var cookieValue = null;
				if (document.cookie && document.cookie != '') {
					var cookies = document.cookie.split(';');
					for ( var i = 0; i < cookies.length; i++) {
						var cookie = jQuery.trim(cookies[i]);
						// Does this cookie string begin with the name
						// we want?
						if (cookie.substring(0, name.length + 1) == (name + '=')) {
							cookieValue = decodeURIComponent(cookie
									.substring(name.length + 1));
							break;
						}
					}
				}
				return cookieValue;
			}
			function sameOrigin(url) {
				// url could be relative or scheme relative or absolute
				var host = document.location.host; // host + port
				var protocol = document.location.protocol;
				var sr_origin = '//' + host;
				var origin = protocol + sr_origin;
				// Allow absolute or scheme relative URLs to same origin
				return (url == origin || url
						.slice(0, origin.length + 1) == origin + '/')
						|| (url == sr_origin || url.slice(0,
								sr_origin.length + 1) == sr_origin
								+ '/') ||
						// or any other URL that isn't scheme relative
						// or absolute i.e relative.
						!(/^(\/\/|http:|https:).*/.test(url));
			}
			function safeMethod(method) {
				return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
			}

			if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
				xhr.setRequestHeader("X-CSRFToken",
						getCookie('csrftoken'));
			}
		});