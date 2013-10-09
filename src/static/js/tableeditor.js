(function($) {
	$.fn.tableeditor = function() {
		var editor = this.find('tr.editor');
		// set the editor to be the full width of the table
		editor.width(this.width());

		// set the widths of each td and input based on the headers
		var ths = this.find('thead th');
		var tds = this.find('tr.editor td');
		var inputs = this.find('tr.editor input');
		ths.each(function(i) {
			$(tds[i]).width($(this).width());
			$(inputs[i]).width($(this).width() - 4) // index out of bounds but fails silently.
		});
		start_editing = function(cell) {
			// save the row to be edited
			editor.data('row', cell.parent())

			// load values into the editor
			cell.parent().children().each(function(i) {
				$(inputs[i]).val($(this).html());
			})
			// focus on the clicked td
			$(inputs[cell.index()]).focus();

			// move the editor to right row
			editor.offset(cell.parent().offset());
			editor.expose({
				closeOnEsc : true,
				closeOnClick : true,
				onBeforeClose : function() {
					editor.hide();
					$('.error').hide();
				}
			});
		};
		stop_editing = function() {
			$.mask.close();
		}

		this.on('click', 'tbody td', function(e) {
			editor.show();
			start_editing($(this));
		});

		inputs.on('keypress', function(e) {
			if(e.keyCode == KEYCODES.ENTER) {
				row = editor.data('row')
				// save values into the edited row
				row.children().each(function(i) {
					$(this).html($(inputs[i]).val());
				})
				if(row.next().size()) {
					start_editing($(row.next().children()[$(this).parent().index()]));
				} else {
					stop_editing();
				}
			}
		});
	};
})(jQuery);
