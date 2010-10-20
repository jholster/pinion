(function($) {

	$(function() {
		
		$('.admin input[name=url]').live('keyup', function() {
			var url = $(this).val().toLowerCase().replace(/[^0-9a-z\-_\/\.]/g, '-');
			if (url.length < 1 || url[0] != '/') url = '/' + url;
			$(this).val(url);
		});
		
		$('.admin textarea').keyup(function() {
			if (this.scrollHeight > $(this).innerHeight())
				$(this).height(this.scrollHeight);
		}).trigger('keyup');
		
		$('.admin form').submit(function() {
			var f = $(this);
			$.post(f.attr('action'), f.serialize(), function() {
				window.location.href = $('input[name=url]', f).val();
			});
			return false;
		});
		
	});
	
})(jQuery);
