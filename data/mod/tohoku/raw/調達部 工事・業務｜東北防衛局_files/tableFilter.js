// table filter common	: querySelector


	const Sub_TableFilter = (tableName,rowName,cellName,startRow,search_text,selectAndOr) => {

		let search_catch = search_text.trim()
						      .replace(/(\s|　)+/g," ")
						      .toLowerCase();

		search_catch = AlfaNumSymboltoHarfWidth(search_catch);

		search_catch = ZenHiratoZenKatakana(search_catch);

		search_catch = KatakanatoHarftWidth(search_catch);

		const arr_searchValue = search_catch.split(' ');

		let displayRowCounter = 0;


		const tableRowsA = document.querySelectorAll(tableName);

		for (let i = 0; i < tableRowsA.length; i++) {

			const tableRowsB = tableRowsA[i].querySelectorAll(rowName);

			for (let j = parseInt(startRow); j < tableRowsB.length; j++) {

//				let tableRowCells = tableRowsB[j].cells;

				let tableRowCells = tableRowsB[j].querySelectorAll(cellName);

				let ArrayKeyword = new Array(arr_searchValue.length).fill(false);

				for (let k = 0; k < tableRowCells.length; k++) {
			
					let RowCell = tableRowCells[k].textContent.toLowerCase();

					RowCell = AlfaNumSymboltoHarfWidth(RowCell);

					RowCell = ZenHiratoZenKatakana(RowCell);

					RowCell = KatakanatoHarftWidth(RowCell);
				
					for (let m = 0; m < arr_searchValue.length; m++) {

						const regPattern = /^\?([1-9]\d*|0)=.*$/

						const result = arr_searchValue[m].match(regPattern)

						if (result !== null) {

							if (1 <= (result[1] <= tableRowCells.length) && ((result[1] - 1) === k)) {

								const arr_searchValue_revided = arr_searchValue[m].replace(/^\?([1-9]\d*|0)=/,'')

    								if (RowCell.indexOf(arr_searchValue_revided) > -1) {

									ArrayKeyword[m] = true;

    								}

							} else {


							} 

						} else {
			
    							if (RowCell.indexOf(arr_searchValue[m]) > -1) {

								ArrayKeyword[m] = true;
						
    							}
						}						
					}
				}
			

				switch (selectAndOr) {

					case 'and':

						if (ArrayKeyword.some(value => value == false)) {

							tableRowsB[j].style.display = 'none';

						} else {

							tableRowsB[j].style.display = '';

							if (displayRowCounter % 2 === 1) {

								tableRowsB[j].style.backgroundColor = "rgba(232,241,254,0.3)";

							} else {

								tableRowsB[j].style.backgroundColor = 'rgb(255,255,255)';

							}

							displayRowCounter = displayRowCounter + 1

						}

						break;

					case 'or':

						if (ArrayKeyword.some(value => value == true)) {

							tableRowsB[j].style.display = '';

							if (displayRowCounter % 2 === 1) {

								tableRowsB[j].style.backgroundColor = "rgba(232,241,254,0.3)";

							} else {

								tableRowsB[j].style.backgroundColor = 'rgb(255,255,255)';

							}

							displayRowCounter = displayRowCounter + 1


						} else {

							tableRowsB[j].style.display = 'none';

						}

						break;

					default:

 				}
			}
		}
		

		/*

		if (displayRowCounter === 0) {

			alert('検索条件に一致するデータはありません。');

			document.querySelector(class_txt).value = '';

			Sub_TableFilter(id_tbl,class_txt,SelectorName);
		
		}

		*/	
	}

	
	const AlfaNumSymboltoHarfWidth = (str) => {


//		return str.replace(/[！-～]/g,char => {
		return str.replace(/[\uFF01-\uFF5E]/g,char => {

			return String.fromCharCode(char.charCodeAt(0) - 0xFEE0);		

		});
	}


	const ZenHiratoZenKatakana = (str) => {


		return str.replace(/[\u3041-\u3096]/g,char => {
		
			return String.fromCharCode(char.charCodeAt(0) + 0x60);		

		});
	}
		
	const KatakanatoHarftWidth = (str) => {


    		var kanaMap = {
         		"ガ": "ｶﾞ", "ギ": "ｷﾞ", "グ": "ｸﾞ", "ゲ": "ｹﾞ", "ゴ": "ｺﾞ",
         		"ザ": "ｻﾞ", "ジ": "ｼﾞ", "ズ": "ｽﾞ", "ゼ": "ｾﾞ", "ゾ": "ｿﾞ",
         		"ダ": "ﾀﾞ", "ヂ": "ﾁﾞ", "ヅ": "ﾂﾞ", "デ": "ﾃﾞ", "ド": "ﾄﾞ",
         		"バ": "ﾊﾞ", "ビ": "ﾋﾞ", "ブ": "ﾌﾞ", "ベ": "ﾍﾞ", "ボ": "ﾎﾞ",
         		"パ": "ﾊﾟ", "ピ": "ﾋﾟ", "プ": "ﾌﾟ", "ペ": "ﾍﾟ", "ポ": "ﾎﾟ",
         		"ヴ": "ｳﾞ", "ヷ": "ﾜﾞ", "ヺ": "ｦﾞ",
        		"ア": "ｱ", "イ": "ｲ", "ウ": "ｳ", "エ": "ｴ", "オ": "ｵ",
         		"カ": "ｶ", "キ": "ｷ", "ク": "ｸ", "ケ": "ｹ", "コ": "ｺ",
         		"サ": "ｻ", "シ": "ｼ", "ス": "ｽ", "セ": "ｾ", "ソ": "ｿ",
         		"タ": "ﾀ", "チ": "ﾁ", "ツ": "ﾂ", "テ": "ﾃ", "ト": "ﾄ",
         		"ナ": "ﾅ", "ニ": "ﾆ", "ヌ": "ﾇ", "ネ": "ﾈ", "ノ": "ﾉ",
         		"ハ": "ﾊ", "ヒ": "ﾋ", "フ": "ﾌ", "ヘ": "ﾍ", "ホ": "ﾎ",
         		"マ": "ﾏ", "ミ": "ﾐ", "ム": "ﾑ", "メ": "ﾒ", "モ": "ﾓ",
         		"ヤ": "ﾔ", "ユ": "ﾕ", "ヨ": "ﾖ",
         		"ラ": "ﾗ", "リ": "ﾘ", "ル": "ﾙ", "レ": "ﾚ", "ロ": "ﾛ",
         		"ワ": "ﾜ", "ヲ": "ｦ", "ン": "ﾝ",
         		"ァ": "ｧ", "ィ": "ｨ", "ゥ": "ｩ", "ェ": "ｪ", "ォ": "ｫ",
         		"ッ": "ｯ", "ャ": "ｬ", "ュ": "ｭ", "ョ": "ｮ",
         		"。": "｡", "、": "､", "ー": "ｰ", "「": "｢", "」": "｣", "・": "･"
    		}

    		var reg = new RegExp('(' + Object.keys(kanaMap).join('|') + ')', 'g');

    		return str.replace(reg, function (match) {

            	return kanaMap[match];
            })
			.replace(/゛/g, 'ﾞ')
			.replace(/゜/g, 'ﾟ');
	};	
	
	
// addEventListener

// table name : id='Table_addFilter_01'	: querySelector

	
	document.querySelectorAll('.tableFilter_btn2').forEach ((searchText) => {

		searchText.addEventListener('click',function(e){

			const filterSection = searchText.closest('.Table_addFilter');

			filterSection.querySelector('.tableFilter_txt1').value = "";
			
			Sub_TableFilter(filterSection.dataset.tablename,
					    	filterSection.dataset.rowname,
					    	filterSection.dataset.cellname,
					    	filterSection.dataset.startrow,
					    	filterSection.querySelector('.tableFilter_txt1').value,
					    	filterSection.querySelector('input[name="' + filterSection.dataset.tablename +'FilterRadio"]:checked').value)
		})
	})

	document.querySelectorAll('.tableFilter_btn1').forEach ((searchText) => {

		searchText.addEventListener('click',function(e){

			const filterSection = searchText.closest('.Table_addFilter');
			
			Sub_TableFilter(filterSection.dataset.tablename,
					    	filterSection.dataset.rowname,
					    	filterSection.dataset.cellname,
					    	filterSection.dataset.startrow,
					    	filterSection.querySelector('.tableFilter_txt1').value,
					    	filterSection.querySelector('input[name="' + filterSection.dataset.tablename +'FilterRadio"]:checked').value)
		})
	})

	document.querySelectorAll('.tableFilter_txt1').forEach ((searchText) => {

		searchText.addEventListener('change',function(e){

			const filterSection = searchText.closest('.Table_addFilter');
			
			Sub_TableFilter(filterSection.dataset.tablename,
					    	filterSection.dataset.rowname,
					    	filterSection.dataset.cellname,
					    	filterSection.dataset.startrow,
					    	filterSection.querySelector('.tableFilter_txt1').value,
					    	filterSection.querySelector('input[name="' + filterSection.dataset.tablename +'FilterRadio"]:checked').value)
		})
	})

	document.querySelectorAll('input[type="radio"]').forEach ((selectRadio) => {

		selectRadio.addEventListener('change',function(e){

			const filterSection = selectRadio.closest('.Table_addFilter');

			Sub_TableFilter(filterSection.dataset.tablename,
					    	filterSection.dataset.rowname,
					    	filterSection.dataset.cellname,
					    	filterSection.dataset.startrow,
					    	filterSection.querySelector('.tableFilter_txt1').value,
					    	filterSection.querySelector('input[name="' + filterSection.dataset.tablename +'FilterRadio"]:checked').value)
		})
	})









	