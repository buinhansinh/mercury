(function($){
  	$.fn.dropdown = function(options) {
		this.on('click', '.dropdown > .button', function(e) {
			var button = $(this);
			var menu = button.next('.menu').first();

			$('.dropdown .menu').not(menu).hide();
			$('.dropdown .button').not(button).removeClass('depressed');

			menu.toggle();
			button.toggleClass('depressed');
			e.stopPropagation(); // keeps the dropdown from hiding 
		});

		this.click(function() {
			$('.dropdown .menu').hide();
			$('.dropdown .button').removeClass('depressed');			
		});
		
		return this;
	};
})(jQuery);
