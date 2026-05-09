	window.addEventListener("DOMContentLoaded", function() {

		const pageTopBtn = document.querySelector("#return-page-top");

		pageTopBtn.addEventListener("click", function (event) {

			event.preventDefault();

    			window.scrollTo({ top: 0, behavior: "smooth" });

  		});

  		window.addEventListener("scroll", function() {

    			if (window.pageYOffset > 200) {

      			pageTopBtn.classList.add("is-visible");

    			} else {

      			pageTopBtn.classList.remove("is-visible");

    			}
  		});
	});

