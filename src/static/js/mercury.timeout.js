/*
Created on Jul 26, 2012

@author: bratface
*/
(function($) {
	$.fn.timeout = function(callback, ms, id){
		if (id==null) id = 'timeout';
		var timer = this.data(id);
    	clearTimeout(timer);
    	timer = setTimeout(callback, ms);
    	this.data(id, timer)
	};
})(jQuery);