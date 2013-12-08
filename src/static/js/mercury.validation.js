/*
Created on Jul 26, 2012

@author: bratface
 */

$.validation = {
	PASSED: 0,
	WARNING: 1,
	ERROR: 2,
	
	required: function(input) {
		if ($(input).val() == '') {
			$(input).invalidate($.validation.ERROR, 'This field is required.');
			return false;
		}
	},
	positive_decimal: function(input) {
		var currency_re = /^(\d+)\.?\d{0,3}$/
		if ($(input).val().search(currency_re) == -1) {
			$(input).invalidate($.validation.ERROR, 'Please enter a valid decimal number. (####.###)');
			return false;
		}
	},	
	decimal: function(input) {
		var currency_re = /^-?(\d+)\.?\d{0,3}$/
		var value = $(input).val()
		if (value != '' && value.search(currency_re) == -1) {
			$(input).invalidate($.validation.ERROR, 'Please enter a valid decimal number. (####.###)');
			return false;
		}
	},
	date: function(input) {
		var pattern = /^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20|21|22)\d\d$/
		var value = $(input).val();
		if (value != '' && !pattern.test(value)) {
			$(input).invalidate($.validation.ERROR, 'Please enter a valid date (mm/dd/yyyy).');
			return false;
		}
	},
};


(function($) {
	$.fn.invalidate = function(type, msg) {
		this.data('validation-result', {
			result: type,
			message: msg,
		});
	},
	
	$.fn.validate = function() {
		var config = this.data('validation-config');
		this.find(config[0].selector).focus().blur();
		for (var i=0; i<config.length; i++) {
			this.find(config[i].selector).each(function() {
				$(this).focus(); // trigger validation
			});
		}		
	}
	
	$.fn.isValid = function() {
		var config = this.data('validation-config');
		for (var i=0; i<config.length; i++) {
			if ($(this).find(config[i].selector).hasClass('error')) {
				alert('Whoops!  Looks like there are still errors on the form.  Please correct them and try again.  In particular, ' + config[i].selector);
				return false;
			}
		}
		return true;
	}
	
	$.fn.validation = function(config, onSubmit) {
		if (!this.is('form')) {
			alert('jQuery.validation can only be applied to a form');
			return;
		}

		this.data('validation-config', config);
		
		$('body').append("<div id='tip' class='error'><span class='icon iconic x_alt'></span> <span class='message'></span></div>");

		var getTip = function() {
			return $('#tip');
		}

		var hideTip = function() {
			getTip().fadeOut(0);
		};

		var showTip = function(input) {
			if ($(input).is(":visible")) {
				var tip = getTip();
				tip.show();
				var offset = $(input).offset();
				tip.offset({
					top : offset.top + $(input).outerHeight() + 5,
					left : offset.left + ($(input).outerWidth() / 2)
							- (tip.outerWidth() / 2),
				});
			}
		}
		
		var updateTip = function(input) {
			var tip = getTip();
			var validation = $(input).data('validation-result');
			if (validation.result == $.validation.ERROR) {
				tip.children('span.message').html(validation.message); // update message
				tip.children('span.icon').removeClass().addClass('icon iconic x_alt');
				tip.removeClass().addClass('error');
				$(input).removeClass('warning').addClass('error');
				showTip(input);
			} else if (validation.result == $.validation.WARNING) {
				tip.children('span.message').html(validation.message); // update message
				tip.children('span.icon').removeClass().addClass('icon layers');
				tip.removeClass().addClass('warning');
				$(input).removeClass('error').addClass('warning');
				showTip(input);
			} else if (validation.result == $.validation.PASSED) {
				$(input).removeClass('error').removeClass('warning');
				hideTip();
			}
		};

		var validateInput = function(input, validators) {
			$(input).data('validation-result', {
				result: $.validation.PASSED,
			});
			for (var i = 0; i < validators.length; i++) {
				if ($.validation[validators[i]](input)) return;
			}
		}
		
		var TIMEOUT = 250;
		var monitor = function(form, input) {
			form.on('keyup', input.selector, function(e) {
				$(e.target).timeout(function() {
					validateInput(e.target, input.validators);
					updateTip(e.currentTarget);
				}, TIMEOUT, 'validation');
			});
	
			form.on('change', input.selector, function(e) {
				$(e.target).timeout(function() {
					validateInput(e.target, input.validators);
					updateTip(e.currentTarget);
				}, TIMEOUT, 'validation');
			});

			// Add in the event hooks
			form.on('focus', input.selector, function(e) {
				validateInput(e.target, input.validators);
				updateTip(e.target);
			});
	
			form.on('blur', input.selector, function(e) {
				validateInput(e.target, input.validators);
				updateTip(e.target); // this bit is a lazy hack. since we don't update the class of the input unless we update the tip, we call this. lazy.
				hideTip();
			});
		};
		
		// start monitoring inputs based on the config array
		for (var i=0; i<config.length; i++) {
			monitor(this, config[i]);
		}

		// check for validity before submit
		this.on('submit', function(e){
			$(this).validate();
			
			// check all inputs
			for (var i=0; i<config.length; i++) {
				if ($(this).find(config[i].selector).hasClass('error')) {
					alert('Whoops!  Looks like there are still errors on the form.  Please correct them and try again.  In particular, ' + config[i].selector);
					return false;
				}
			}
			
			// check all inputs for warnings
			for (var i=0; i<config.length; i++) {
				if ($(this).find(config[i].selector).hasClass('warning')) {
					var yes = confirm('There are warnings on this form. Are you sure you want to continue? ' + config[i].selector);
					if (yes) {
						break; // no need to go through other warnings. just 1 will do.
					} else {
						return false;
					}
				}
			}
			
			// custom form validation
			var passed = true;
			if (onSubmit) {
				passed = onSubmit();
			}
			
			if (passed != false) {
				// prevent multiple submissions
				if ($(this).data('submitted')) {
					alert('This form has already been submitted. Please wait.');
					return false;
				} else {
					$(this).data('submitted', true);
				}
			}
		});
		
		this.validate();
		
		return this;
	};
})(jQuery);
