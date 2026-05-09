$(function(){
	$('a[href]').each(function(){
//	$('a.pdfsize').each(function(){
		const targetObj = $(this);
		const g = targetObj.attr('href');
		const mytext = targetObj.html();
		const checkA = {
			'pdf': 'PDF', 
			'xlsm': 'EXCEL', 
			'xlsx': 'EXCEL', 
			'xls': 'EXCEL', 
			'docx': 'WORD', 
			'doc': 'WORD', 
			'zip': 'ZIP', 
			'ppt': 'POWERPOINT', 
		}
		$.each(checkA,
			function(key, val) {
				if(g.split('.').pop()==key && !targetObj.hasClass('nocheckpdf')){
					let setText = mytext;
					$.ajax({
						type: 'HEAD',
						url: g,
						dataType: 'text', 
					}).done(function(data, status, xhr){
						let i = xhr.getResponseHeader('Content-Length');
						setText += '<span class="pdfsize txt_m">('+val+':' + b(i)+ ')</span>';
						targetObj.html(setText);
					}).fail(function(data, status, xhr){
					})
				}
			}
		);
	});
	function b(d) {
		if (d < 1024) {
			return d + 'B';
		} else {
			d = a(d)
		}
		if (d < 1024) {
			return d + 'KB';
		} else {
			d = a(d)
		}
		if (d < 1024) {
			return d + 'MB';
		} else {
			return a(d) + 'GB';
		}
	}
	
	function a(d) {
		return (Math.ceil((d * 10) / 1024)) / 10;
	}
});