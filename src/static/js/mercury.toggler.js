(function($) {
	$.fn.toggler = function() {
		this.each(function() {
			$(this).append("<span class='toggler-icon iconic arrow_up_alt1'></span>").click(function() {
				$($(this).attr('href')).slideToggle('fast');
				$(this).children('.toggler-icon').toggleClass('arrow_up_alt1');
				$(this).children('.toggler-icon').toggleClass('arrow_down_alt1');
				return false;
			});
		});
	};

	$.fn.collapse = function() {
		this.each(function() {
			$($(this).attr('href')).slideUp('fast');
			$(this).children('.toggler-icon').removeClass('arrow_up_alt1');
			$(this).children('.toggler-icon').addClass('arrow_down_alt1');
		});
		return false;
	};

	$.fn.expand = function() {
		$(this).each(function() {
			$($(this).attr('href')).slideDown('fast');
			$(this).children('.toggler-icon').addClass('arrow_up_alt1');
			$(this).children('.toggler-icon').removeClass('arrow_down_alt1');
		});
		return false;
	};
	
})(jQuery);
