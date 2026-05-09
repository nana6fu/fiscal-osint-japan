/* サブメニュー
------------------------------------------------------------------------*/
$(function () {
  $(".has-children a")
    .focus(function () {
      $(this).siblings(".sub-menu").addClass("focused");
    })
    .blur(function () {
      $(this).siblings(".sub-menu").removeClass("focused");
    });

  // サブメニュー用
  $(".sub-menu a")
    .focus(function () {
      $(this).parents(".sub-menu").addClass("focused");
    })
    .blur(function () {
      $(this).parents(".sub-menu").removeClass("focused");
    });
});

// 'Esc'キーが押された場合
document.addEventListener('keydown', function(event) {
  if (event.key === "Escape") {
    // 選択を解除
    document.activeElement.blur();
  }
});
