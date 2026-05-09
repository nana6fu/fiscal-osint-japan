$(function() {

  $('ul.ddmenu li > a').focus( function () {
    $(this).siblings('.sub-menu').addClass('focused');
  }).blur(function(){
    $(this).siblings('.sub-menu').removeClass('focused');
  });

// For children
  $('.sub-menu a').focus( function () {
    $(this).parents('.sub-menu').addClass('focused');
  }).blur(function(){
    $(this).parents('.sub-menu').removeClass('focused');
  });
});