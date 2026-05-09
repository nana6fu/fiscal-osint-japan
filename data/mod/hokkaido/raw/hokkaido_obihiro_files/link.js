window.addEventListener('load',function(){
	var headerHeight = $('.header').outerHeight();
	var urlHash = location.hash;
	if(urlHash){
	$('html,body').stop().scrollTop(0);
	setTimeout(function(){
	var position = $(urlHash).offset().top - headerHeight;
	$('html,body').animate({scrollTop: position},1);
	},100);
	}
})
