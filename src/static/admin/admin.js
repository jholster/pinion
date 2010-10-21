(function($) {

	$(function() {
		
		$('.admin #form-edit textarea').keyup(function() {
			if (this.scrollHeight > $(this).innerHeight())
				$(this).height(this.scrollHeight);
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
		
		
	});
	
})(jQuery);
