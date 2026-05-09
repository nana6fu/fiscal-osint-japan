function newschk(targetobj, level, category, height){
	if($(targetobj).length){
		const myid = 'newsbox'+new Date().getTime().toString();
		$(targetobj).after('<div id="'+myid+'">');
		$(targetobj).hide();
		$.ajax({
			url: $(targetobj).attr('src')
		})
		.then(
			// 通信成功時の処理
			function(html){
				if(
					level !== undefined &&
					level !== 0
				){
					let leveltext = '';
					if(level > 0){
						for(let i=0; i<level; i++){
							leveltext += '../';
						}
					}else{
						leveltext = level;
					}
					html = html.replace(/href=\"(?!(http|https))|href=\"\.\//g, 'href="'+leveltext);
				}
				$('#'+myid).html(html);
				if(
					category !== undefined &&
					category !== ''
				){
					$('tr, li', '#'+myid).hide();
					$('#'+myid).find('.'+category).show();
				}
				if(
					height !== undefined &&
					height !== ''
				){
					$('#'+myid).css({
						'max-height': height, 
						'overflow-y': 'scroll', 
					});
				}

				if($('#'+myid+' .backnumber').length){
					$('#'+myid+' .backnumber').each(function(){
						let targetObj = $(this);
						let limit = parseInt($(this).attr('data-limit'));
						$('> *:eq('+(limit-1)+')', targetObj).after('<li><a class="backnumbermorebtn" href="javascript:void(0);">バックナンバーをもっと見る');
						$('> *:last-child', targetObj).after('<li><a class="backnumberclosebtn" href="javascript:void(0);">バックナンバーを閉じる');
						$('.backnumberclosebtn', targetObj).on('click', function(){
							$('> *', targetObj).hide();
							for(let i=0; i<=limit; i++){
								$('> *:eq('+i+')', targetObj).show();
							}
							$('.backnumbermorebtn', targetObj).show();
						});
						$('.backnumbermorebtn', targetObj).on('click', function(){
							$('> *', targetObj).show();
							$(this).hide();
						});
						$('.backnumberclosebtn', targetObj).click();
					});
				}
			}
		);
	}
}
window.globalFunction = {};
window.globalFunction.newschk = newschk;