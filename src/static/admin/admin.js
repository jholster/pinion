(function($) {

	$(function() {
	
		var edited = false;
		var prev_content;
		
		$('.admin #form-edit textarea').keyup(function() {
			edited = edited || (prev_content != null && $(this).val() != prev_content);
			if (this.scrollHeight > $(this).innerHeight())
				$(this).height(this.scrollHeight);
			prev_content = $(this).val();
		}).trigger('keyup');
		
		$('.admin #form-edit').submit(function() {
			var f = $(this);
			$.post(f.attr('action'), f.serialize(), function() {
				window.location.href = $('[name=url]', f).val();
			});
			return false;
		});

		$('.admin #form-edit [name=version]').change(function() {
			$('.admin #form-version [name=version]').val($(this).val());
			$('.admin #form-version').submit();
		});

		$('.admin #form-edit button.cancel').click(function(e) {
			e.preventDefault();
			if (edited && ! confirm('Discard changes?')) return;
			window.location.href = $('.admin #form-edit [name=url]').val();
		});		
		
	});
	
})(jQuery);
