	// details_top open/close

	$(document).on('click','details.details_top',function(e){

		let table = $(this).closest('table');

		for ( i = 0; i < table.length; i++) {

			const tableRows = table[i].querySelectorAll('details');

			if (this.open) {
		
				for (let j = 1 ; j < tableRows.length; j++) {

					tableRows[j].open = false;

				}

			} else {

				for (let j = 1; j < tableRows.length; j++) {

					tableRows[j].open = true;

				}
			}
		}
	})










	