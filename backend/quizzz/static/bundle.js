var jsFuncs =
/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./js/index.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./js/addFilters.js":
/*!**************************!*\
  !*** ./js/addFilters.js ***!
  \**************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("const addFilters = (filters, parentNodeId, onSelect) => {\n  /*\n      <filters>:      array of [k,v] arrays where:\n          k - filter name\n          v - boolean whether it is selected or not\n      <parentNodeId>: ID of the node where to append filter buttons\n      <onSelect>:     callback to call when selected filter is changed,\n                      <activeFilter> is passed as argument;\n  */\n  let filterSelection = [...filters];\n\n  const getActiveFilter = () => filterSelection.reduce((acc, [k,v]) => v ? k : acc, null);\n\n  const selectFilter = (e, filter) => {\n      e.preventDefault();\n      filterSelection = filterSelection.map(\n          ([k,v]) => ((k === filter) ? [k,true] : [k,false])\n      );\n      renderFilters();\n      onSelect(getActiveFilter());\n  }\n\n  const renderFilters = () => {\n      const parentNode = document.getElementById(parentNodeId);\n      // delete previously shown rows:\n      parentNode.innerHTML = \"\";\n      // append row by row:\n      for (let [k,v] of filterSelection) {\n          const link = document.createElement(\"a\");\n          link.className = \"tabs__button\";\n          if (v) link.classList.add(\"tabs__button--active\");\n          link.onclick = (e) => selectFilter(e, k);\n          link.href = \"?filter=\" + k;\n          link.innerHTML = k[0].toUpperCase() + k.slice(1);\n\n          parentNode.append(link);\n      }\n  }\n\n  // initial render\n  renderFilters();\n  onSelect(getActiveFilter());\n}\n\n\nmodule.exports = addFilters;\n\n//# sourceURL=webpack://jsFuncs/./js/addFilters.js?");

/***/ }),

/***/ "./js/chat.js":
/*!********************!*\
  !*** ./js/chat.js ***!
  \********************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("const renderMomentDate = __webpack_require__(/*! ./renderMomentDate */ \"./js/renderMomentDate.js\");\n\n\nconst makeChatMessageHTML = (msg) => {\n    const article = document.createElement(\"article\");\n    article.className = \"message\";\n    if (msg.is_own) article.classList.add(\"message--own\");\n\n    const detailsDiv = document.createElement(\"div\");\n    detailsDiv.className = \"message__details\";\n    article.append(detailsDiv);\n\n    const containerDiv = document.createElement(\"div\");\n    containerDiv.className = \"message__details-main\";\n\n    const authorDiv = document.createElement(\"div\");\n    authorDiv.className = \"message__details-item message__author\";\n    authorDiv.innerHTML = msg.user_name;\n    containerDiv.append(authorDiv);\n\n    if (msg.is_own) {\n        const editLink = document.createElement(\"a\");\n        editLink.href = msg.edit_url;\n        editLink.className = \"btn btn--secondary message__details-item\";\n        editLink.innerHTML = \"edit\";\n        containerDiv.append(editLink);\n    }\n\n    const relTimeDiv = document.createElement(\"div\");\n    relTimeDiv.dataset.timestamp = msg.time_created;\n    relTimeDiv.dataset.func = \"fromNow\";\n    relTimeDiv.dataset.refresh = 10000;\n    renderMomentDate(relTimeDiv); // adds innerHTML to element\n    relTimeDiv.className = \"message__details-item\";\n    containerDiv.append(relTimeDiv);\n\n    detailsDiv.append(containerDiv);\n\n    const timeDiv = document.createElement(\"div\");\n    timeDiv.innerHTML = moment(msg.time_created).format(\"MMM D, YYYY [at] h:mm a\");\n    timeDiv.className = \"message__details-item\";\n    detailsDiv.append(timeDiv);\n\n    const msgText = document.createElement(\"p\");\n    msgText.className = \"message__text\";\n    msgText.innerHTML = msg.text;\n\n    article.append(detailsDiv);\n    article.append(msgText);\n    if (msg.time_updated) {\n        const timeUpdatedDiv = document.createElement(\"div\");\n        timeUpdatedDiv.className = \"message__edited\";\n        timeUpdatedDiv.innerHTML = (\n            \"last edit: \" + moment(msg.time_updated).format(\"MMM D, YYYY [at] h:mm a\"));\n        article.append(timeUpdatedDiv);\n    }\n\n    return article;\n}\n\n\n\nconst makePaginationHTML = (pagination) => {\n    const wrapperDiv = document.createElement(\"div\");\n    wrapperDiv.className = \"pagination\";\n\n    // add left div to move back to previous and first pages\n    const backDiv = document.createElement(\"div\");\n\n    const firstPageLink = document.createElement(\"a\");\n    firstPageLink.className = \"pagination-button\";\n    if (pagination.has_prev) {\n        firstPageLink.addEventListener(\"click\", () => loadChat(pagination.link_to_first));\n    }\n    firstPageLink.innerHTML = \"<<\";\n    backDiv.append(firstPageLink);\n\n    const prevPageLink = document.createElement(\"a\");\n    prevPageLink.className = \"pagination-button\";\n    if (pagination.has_prev) {\n        prevPageLink.addEventListener(\"click\", () => loadChat(pagination.prev_link));\n    }\n    prevPageLink.innerHTML = \"prev\";\n    backDiv.append(prevPageLink);\n\n    wrapperDiv.append(backDiv);\n\n    // add middle div to show where we are\n    const currentPageDiv = document.createElement(\"div\");\n    currentPageDiv.innerHTML = `${pagination.page} / ${pagination.total_pages}`;\n    wrapperDiv.append(currentPageDiv);\n\n    // add right div to move forward\n    const forwardDiv = document.createElement(\"div\");\n\n    const nextPageLink = document.createElement(\"a\");\n    nextPageLink.className = \"pagination-button\";\n    if (pagination.has_next) {\n        nextPageLink.addEventListener(\"click\", () => loadChat(pagination.next_link));\n    }\n    nextPageLink.innerHTML = \"next\";\n    forwardDiv.append(nextPageLink);\n\n    const lastPageLink = document.createElement(\"a\");\n    lastPageLink.className = \"pagination-button\";\n    if (pagination.has_next) {\n        lastPageLink.addEventListener(\"click\", () => loadChat(pagination.link_to_last));\n    }\n    lastPageLink.innerHTML = \">>\";\n    forwardDiv.append(lastPageLink);\n\n    wrapperDiv.append(forwardDiv);\n\n    return wrapperDiv;\n}\n\n\n\nconst loadChat = (url) => {\n  fetch(url)\n    .then((response) => {\n      if (response.ok) return response.json()\n      else throw new Error(\"Request Failed\");\n    }).then((data) => {\n      const { pagination, messages } = data;\n\n      const messagesDiv = document.getElementById(\"message_list\");\n      messagesDiv.innerHTML = \"\";\n      if (messages.length) {\n          for (let message of messages) {\n            let messageHTML = makeChatMessageHTML(message);\n            messagesDiv.append(messageHTML);\n          }\n      } else {\n          messagesDiv.innerHTML = \"<p>No messages here yet. Be the first to say something!</p>\"\n      }\n\n      const paginationDiv = document.getElementById(\"pagination\");\n      paginationHTML = makePaginationHTML(pagination);\n      paginationDiv.innerHTML = \"\";\n\n      paginationDiv.append(paginationHTML);\n    }).catch(\n      e => console.log(e)\n    );\n}\n\n\nmodule.exports = loadChat;\n\n//# sourceURL=webpack://jsFuncs/./js/chat.js?");

/***/ }),

/***/ "./js/editRound/index.js":
/*!*******************************!*\
  !*** ./js/editRound/index.js ***!
  \*******************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("const renderQuizSelector = __webpack_require__(/*! ./renderQuizSelector */ \"./js/editRound/renderQuizSelector.js\");\nconst renderDateTimeSelector = __webpack_require__(/*! ./renderDateTimeSelector */ \"./js/editRound/renderDateTimeSelector.js\");\n\n\nmodule.exports = {\n  renderQuizSelector,\n  renderDateTimeSelector\n}\n\n//# sourceURL=webpack://jsFuncs/./js/editRound/index.js?");

/***/ }),

/***/ "./js/editRound/renderDateTimeSelector.js":
/*!************************************************!*\
  !*** ./js/editRound/renderDateTimeSelector.js ***!
  \************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("const setTimeToMidnight = (hoursInputId, minutesInputId) => {\n  /* Note:\n  Gecko notes\n  Using setAttribute() to modify certain attributes, most notably value in XUL,\n  works inconsistently, as the attribute specifies the default value.\n  To access or modify the current values, you should use the properties.\n  For example, use Element.value instead of Element.setAttribute().\n  https://developer.mozilla.org/en-US/docs/Web/API/Element/setAttribute\n  */\n  document.querySelector(hoursInputId).value = \"0\";\n  document.querySelector(minutesInputId).value = \"0\";\n}\n\n\nconst renderDateTimeSelector = (prefix, timestamp, parentId) => {\n  const obj = moment(timestamp);\n  const dateValue = obj.format(\"YYYY-MM-DD\");\n  const hoursValue = obj.format(\"HH\");\n  const minutesValue = obj.format(\"mm\");\n\n  const container = document.createElement(\"div\");\n  container.className = \"container\";\n\n  const row = document.createElement(\"div\");\n  row.className = \"row\";\n  row.innerHTML = `\n    <div class=\"col-6\">\n      <div class=\"form__input-help\">date</div>\n      <input class=\"form__input\" type=\"date\"\n          id=\"${prefix}_date\" name=\"${prefix}_date\" value=\"${dateValue}\">\n    </div>\n    <div class=\"col-offset-1 col-2\">\n      <div class=\"form__input-help\">hours</div>\n      <input class=\"form__input\" type=\"number\" min=\"0\" max=\"23\" required\n          id=\"${prefix}_hours\" name=\"${prefix}_hours\" value=\"${hoursValue}\">\n    </div>\n    <div class=\"col-offset-1 col-2\">\n      <div class=\"form__input-help\">minutes</div>\n      <input class=\"form__input\" type=\"number\" min=\"0\" max=\"59\" required\n          id=\"${prefix}_minutes\" name=\"${prefix}_minutes\" value=\"${minutesValue}\">\n    </div>`;\n\n  container.appendChild(row);\n\n  const row2 = document.createElement(\"div\");\n  row2.className = \"row\";\n  const div = document.createElement(\"div\");\n  div.className = \"col-offset-7 col-5\";\n  const subDiv = document.createElement(\"div\");\n  subDiv.className = \"link link--grey text-small text-centered\";\n  subDiv.innerText = \"set to midnight\";\n  subDiv.onclick = () => setTimeToMidnight(`#${prefix}_hours`, `#${prefix}_minutes`);\n  \n  div.appendChild(subDiv);\n  row2.appendChild(div);\n  container.appendChild(row2);\n\n  const parentNode = document.getElementById(parentId);\n  parentNode.innerHTML = \"\";\n  parentNode.appendChild(container);\n\n  return container;\n}\n\n\nmodule.exports = renderDateTimeSelector;\n\n//# sourceURL=webpack://jsFuncs/./js/editRound/renderDateTimeSelector.js?");

/***/ }),

/***/ "./js/editRound/renderQuizSelector.js":
/*!********************************************!*\
  !*** ./js/editRound/renderQuizSelector.js ***!
  \********************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("const renderQuizSelector = (quizId, quizPool) => {\n\n\n  const makeTableRow = (quiz, num, onSelectQuiz) => {\n    const tr = document.createElement(\"tr\");\n    tr.className = \"table__tr\";\n    tr.classList.add(((num + 1) % 2) ? \"table__tr--odd\" : \"table__tr--even\");\n\n    let td;\n\n    td = document.createElement(\"td\");\n    td.className = \"table__td\";\n    td.innerHTML = quiz.author;\n    tr.append(td);\n\n    td = document.createElement(\"td\");\n    td.className = \"table__td\";\n    td.innerHTML = quiz.topic;\n    tr.append(td);\n\n    td = document.createElement(\"td\");\n    td.className = \"table__td table__td--centered\";\n    const momentObj = moment(quiz.time_submitted);\n    td.innerHTML = momentObj.format(\"YYYY-MM-DD HH:mm\");\n    tr.append(td);\n\n    tr.onclick = () => onSelectQuiz(quiz.id);\n\n    return tr;\n  }\n\n\n  const makeQuizPoolTable = (quizPool, onSelectQuiz) => {\n    // table with choices\n    const table = document.createElement(\"table\");\n    table.className = \"table table--full-width\";\n\n    // column names\n    const thead = document.createElement(\"thead\");\n    thead.innerHTML = `<tr>\n        <th width=\"25%\">Author</th>\n        <th width=\"35%\">Name</th>\n        <th width=\"40%\">Submitted</th>\n      </tr>`;\n    table.append(thead);\n\n    // quiz pool\n    const tbody = document.createElement(\"tbody\");\n    if (!quizPool.length) {\n      const tr = document.createElement(\"tr\");\n      tr.className = \"table__tr table__tr--odd\";\n      tr.innerHTML = '<td class=\"table__td\" colspan=\"3\">No quizzes available.</td>';\n      tbody.append(tr);\n    } else {\n      quizPool.forEach((r,i) => {\n        tbody.append(makeTableRow(r, i, onSelectQuiz));\n      })\n    }\n    table.append(tbody);\n\n    return table;\n  }\n\n\n  const makeSelectedQuizTable = (selectedQuiz) => {\n    // table with selection\n    const table = document.createElement(\"table\");\n    table.className = \"table table--full-width table--colorful\";\n\n    const thead = document.createElement(\"thead\");\n    const tr = document.createElement(\"tr\");\n    if (selectedQuiz) {\n      const momentObj = moment(selectedQuiz.time_submitted);\n      const quizTime = momentObj.format(\"YYYY-MM-DD HH:mm\");\n      tr.innerHTML = `\n          <th width=\"25%\">${selectedQuiz.author}</th>\n          <th width=\"35%\">${selectedQuiz.topic}</th>\n          <th width=\"40%\">${quizTime}</th>`;\n    } else {\n      tr.innerHTML = '<th colspan=\"3\">No quiz selected.</th>';\n    }\n    thead.append(tr);\n    table.append(thead);\n\n    return table;\n  }\n\n\n  const makeContainer = (quizPool, selectedQuizId, onSelectQuiz) => {\n    let selectedQuiz = quizPool.filter(q => q.id === selectedQuizId);\n    selectedQuiz = (selectedQuiz.length) ? selectedQuiz[0] : null;\n\n    // container\n    const div = document.createElement(\"div\");\n    // table with selected quiz\n    const table1 = makeSelectedQuizTable(selectedQuiz);\n    div.append(table1);\n    // header\n    const help = document.createElement(\"button\");\n    help.className = \"btn btn--grey my-2\";\n    help.innerHTML = \"Show quiz pool\";\n    function toggleQuizPool(e) {\n      e.preventDefault();\n      if (table2.hidden) {\n        table2.hidden = false;\n        this.innerHTML = \"Hide quiz pool\";\n      } else {\n        table2.hidden = true;\n        this.innerHTML = \"Show quiz pool\";\n      }\n    }\n    help.onclick = toggleQuizPool;\n    div.append(help);\n    // table with quiz pool\n    const table2 = makeQuizPoolTable(quizPool, onSelectQuiz);\n    table2.hidden = true;\n    div.append(table2);\n\n    return div;\n  }\n\n\n  const handleSelectQuiz = (quizId) => {\n    document.querySelector(\"#selectedQuizId\").value = quizId;\n    const container = makeContainer(quizPool, quizId, handleSelectQuiz);  // closure\n    const parent = document.querySelector(\"#selectQuiz\");\n    parent.innerHTML = \"\";\n    parent.append(container);\n  }\n\n  // initial selection\n  handleSelectQuiz(quizId);\n}\n\n\nmodule.exports = renderQuizSelector;\n\n//# sourceURL=webpack://jsFuncs/./js/editRound/renderQuizSelector.js?");

/***/ }),

/***/ "./js/index.js":
/*!*********************!*\
  !*** ./js/index.js ***!
  \*********************/
/*! exports provided: loadChat, renderMomentDate, addFilters, renderMembersTableBody, renderQuizzesTableBody, renderTournamentsTableBody, renderRoundsTableBody, renderQuizSelector, renderDateTimeSelector */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _chat__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./chat */ \"./js/chat.js\");\n/* harmony import */ var _chat__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_chat__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony reexport (default from non-harmony) */ __webpack_require__.d(__webpack_exports__, \"loadChat\", function() { return _chat__WEBPACK_IMPORTED_MODULE_0___default.a; });\n/* harmony import */ var _renderMomentDate__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./renderMomentDate */ \"./js/renderMomentDate.js\");\n/* harmony import */ var _renderMomentDate__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_renderMomentDate__WEBPACK_IMPORTED_MODULE_1__);\n/* harmony reexport (default from non-harmony) */ __webpack_require__.d(__webpack_exports__, \"renderMomentDate\", function() { return _renderMomentDate__WEBPACK_IMPORTED_MODULE_1___default.a; });\n/* harmony import */ var _addFilters__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./addFilters */ \"./js/addFilters.js\");\n/* harmony import */ var _addFilters__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_addFilters__WEBPACK_IMPORTED_MODULE_2__);\n/* harmony reexport (default from non-harmony) */ __webpack_require__.d(__webpack_exports__, \"addFilters\", function() { return _addFilters__WEBPACK_IMPORTED_MODULE_2___default.a; });\n/* harmony import */ var _renderMembersTableBody__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./renderMembersTableBody */ \"./js/renderMembersTableBody.js\");\n/* harmony import */ var _renderMembersTableBody__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_renderMembersTableBody__WEBPACK_IMPORTED_MODULE_3__);\n/* harmony reexport (default from non-harmony) */ __webpack_require__.d(__webpack_exports__, \"renderMembersTableBody\", function() { return _renderMembersTableBody__WEBPACK_IMPORTED_MODULE_3___default.a; });\n/* harmony import */ var _renderQuizzesTableBody__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./renderQuizzesTableBody */ \"./js/renderQuizzesTableBody.js\");\n/* harmony import */ var _renderQuizzesTableBody__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_renderQuizzesTableBody__WEBPACK_IMPORTED_MODULE_4__);\n/* harmony reexport (default from non-harmony) */ __webpack_require__.d(__webpack_exports__, \"renderQuizzesTableBody\", function() { return _renderQuizzesTableBody__WEBPACK_IMPORTED_MODULE_4___default.a; });\n/* harmony import */ var _renderTournamentsTableBody__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./renderTournamentsTableBody */ \"./js/renderTournamentsTableBody.js\");\n/* harmony import */ var _renderTournamentsTableBody__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_renderTournamentsTableBody__WEBPACK_IMPORTED_MODULE_5__);\n/* harmony reexport (default from non-harmony) */ __webpack_require__.d(__webpack_exports__, \"renderTournamentsTableBody\", function() { return _renderTournamentsTableBody__WEBPACK_IMPORTED_MODULE_5___default.a; });\n/* harmony import */ var _renderRoundsTableBody__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./renderRoundsTableBody */ \"./js/renderRoundsTableBody.js\");\n/* harmony import */ var _renderRoundsTableBody__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_renderRoundsTableBody__WEBPACK_IMPORTED_MODULE_6__);\n/* harmony reexport (default from non-harmony) */ __webpack_require__.d(__webpack_exports__, \"renderRoundsTableBody\", function() { return _renderRoundsTableBody__WEBPACK_IMPORTED_MODULE_6___default.a; });\n/* harmony import */ var _editRound__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./editRound */ \"./js/editRound/index.js\");\n/* harmony import */ var _editRound__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(_editRound__WEBPACK_IMPORTED_MODULE_7__);\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"renderQuizSelector\", function() { return _editRound__WEBPACK_IMPORTED_MODULE_7__[\"renderQuizSelector\"]; });\n\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"renderDateTimeSelector\", function() { return _editRound__WEBPACK_IMPORTED_MODULE_7__[\"renderDateTimeSelector\"]; });\n\n\n\n\n\n\n\n\n\n\n\n\n//# sourceURL=webpack://jsFuncs/./js/index.js?");

/***/ }),

/***/ "./js/renderMembersTableBody.js":
/*!**************************************!*\
  !*** ./js/renderMembersTableBody.js ***!
  \**************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("const renderMomentDate = __webpack_require__(/*! ./renderMomentDate */ \"./js/renderMomentDate.js\");\n\n\nconst makeRow = (rowData, num, isAdmin) => {\n  const tr = document.createElement(\"tr\");\n  tr.className = \"table__tr\";\n  tr.classList.add(((num + 1) % 2) ? \"table__tr--odd\" : \"table__tr--even\");\n\n  const td1 = document.createElement(\"td\");\n  td1.className = \"table__td table__td--centered\";\n  td1.innerHTML = num + 1;\n  tr.append(td1);\n\n  const td2 = document.createElement(\"td\");\n  td2.className = \"table__td\";\n  td2.innerHTML = rowData.name;\n  tr.append(td2);\n\n  const td3 = document.createElement(\"td\");\n  td3.className = \"table__td table__td--centered\";\n  td3.innerHTML = rowData.user_id;\n  tr.append(td3);\n\n  const td4 = document.createElement(\"td\");\n  td4.className = \"table__td table__td--centered\";\n  const timeSpan = document.createElement(\"span\");\n  timeSpan.dataset.timestamp = rowData.time_created;\n  timeSpan.dataset.func = \"format\";\n  timeSpan.dataset.format = \"MMM D, YYYY [at] h:mm a\";\n  renderMomentDate(timeSpan); // adds innerHTML to element\n  td4.append(timeSpan);\n  tr.append(td4);\n\n  const td5 = document.createElement(\"td\");\n  td5.className = \"table__td table__td--centered\";\n  td5.innerHTML = rowData.is_admin ? \"admin\" : \"\";\n  tr.append(td5);\n\n  const td6 = document.createElement(\"td\");\n  td6.className = \"table__td table__td--centered\";\n  if (isAdmin && !rowData.is_admin) {\n    td6.innerHTML = `<a class=\"link link--decorated\" href=\"${rowData.edit_url}\">✎</a>`;\n  }\n  tr.append(td6);\n\n  return tr;\n}\n\n\nconst renderMembersTableBody = (members, isAdmin, parentId) => {\n  // apply current filter\n  let rows = [...members];\n\n  // sort selected rows\n  rows.sort((a,b) => (a.name > b.name) ? 1 : -1);\n\n  // re-render\n  const node = document.getElementById(parentId);\n  node.innerHTML = \"\";\n  rows.forEach((r,i) => {\n    node.append(makeRow(r,i,isAdmin));\n  })\n}\n\n\nmodule.exports = renderMembersTableBody;\n\n//# sourceURL=webpack://jsFuncs/./js/renderMembersTableBody.js?");

/***/ }),

/***/ "./js/renderMomentDate.js":
/*!********************************!*\
  !*** ./js/renderMomentDate.js ***!
  \********************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("const renderMomentDate = (el) => {\n  const {timestamp, func, format, refresh} = el.dataset;\n  const obj = moment(timestamp);\n  const args = [];\n  if (format) args.push(format);\n  const val = obj[func].apply(obj, args);\n  el.innerHTML = val;\n  if (refresh) {\n      setTimeout(() => renderMomentDate(el), refresh);\n  }\n}\n\n\nmodule.exports = renderMomentDate;\n\n//# sourceURL=webpack://jsFuncs/./js/renderMomentDate.js?");

/***/ }),

/***/ "./js/renderQuizzesTableBody.js":
/*!**************************************!*\
  !*** ./js/renderQuizzesTableBody.js ***!
  \**************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("const renderMomentDate = __webpack_require__(/*! ./renderMomentDate */ \"./js/renderMomentDate.js\");\n\n\nconst makeRow = (rowData, num) => {\n  const tr = document.createElement(\"tr\");\n  tr.className = \"table__tr\";\n  tr.classList.add(((num + 1) % 2) ? \"table__tr--odd\" : \"table__tr--even\");\n\n  const td1 = document.createElement(\"td\");\n  td1.className = \"table__td table__td--centered\";\n  td1.innerHTML = num + 1;\n  tr.append(td1);\n\n  const td2 = document.createElement(\"td\");\n  td2.className = \"table__td\";\n  td2.innerHTML = `<a class=\"link\" href=\"${ rowData.edit_url }\">\"${ rowData.topic }\"</a>`;\n  tr.append(td2);\n\n  const td3 = document.createElement(\"td\");\n  td3.className = \"table__td table__td--centered\";\n  td3.innerHTML = (rowData.is_submitted) ? \"yes\" : \"no\";\n  tr.append(td3);\n\n  const td4 = document.createElement(\"td\");\n  td4.className = \"table__td table__td--centered\";\n  const relTimeSpan = document.createElement(\"span\");\n  relTimeSpan.dataset.timestamp = rowData.last_update;\n  relTimeSpan.dataset.func = \"fromNow\";\n  relTimeSpan.dataset.refresh = 60000;\n  renderMomentDate(relTimeSpan); // adds innerHTML to element\n\n  const timeDiv = document.createElement(\"div\");\n  timeDiv.dataset.timestamp = rowData.last_update;\n  timeDiv.dataset.func = \"format\";\n  timeDiv.dataset.format = \"MMM D, YYYY [at] h:mm a\";\n  renderMomentDate(timeDiv);\n  timeDiv.hidden = true;\n\n  td4.append(relTimeSpan);\n  td4.append(timeDiv);\n  td4.onclick = () => {\n    timeDiv.hidden = !timeDiv.hidden;\n  }\n  tr.append(td4);\n\n  return tr;\n}\n\n\nconst renderQuizzesTableBody = (activeFilter, quizzes, parentId) => {\n  // apply current filter\n  let rows = [...quizzes];\n  if (activeFilter === \"submitted\") rows = rows.filter(r => r.is_submitted)\n  else if (activeFilter === \"unfinished\") rows = rows.filter(r => !r.is_submitted);\n\n  // sort selected rows\n  rows.sort((a,b) => {\n    if (a.is_submitted && !b.is_submitted) return 1;\n    if (!a.is_submitted && b.is_submitted) return -1;\n    if (a.last_update > b.last_update) return -1;\n  });\n\n  // re-render\n  const node = document.getElementById(parentId);\n  node.innerHTML = \"\";\n  if (!rows.length) {\n    const tr = document.createElement(\"tr\");\n    tr.className = \"table__tr table__tr--odd\";\n    tr.innerHTML = '<td class=\"table__td\" colspan=\"5\">Nothing here.</td>';\n    node.append(tr);\n  } else {\n    rows.forEach((r,i) => {\n      node.append(makeRow(r,i));\n    })\n  }\n}\n\n\nmodule.exports = renderQuizzesTableBody;\n\n//# sourceURL=webpack://jsFuncs/./js/renderQuizzesTableBody.js?");

/***/ }),

/***/ "./js/renderRoundsTableBody.js":
/*!*************************************!*\
  !*** ./js/renderRoundsTableBody.js ***!
  \*************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("const renderMomentDate = __webpack_require__(/*! ./renderMomentDate */ \"./js/renderMomentDate.js\");\n\n\nconst makeRoundRow = (round, num, isAdmin) => {\n  const tr = document.createElement(\"tr\");\n  tr.className = \"table__tr\";\n  tr.classList.add(((num + 1) % 2) ? \"table__tr--odd\" : \"table__tr--even\");\n\n  const td1 = document.createElement(\"td\");\n  td1.className = \"table__td table__td--centered\";\n  td1.innerHTML = num + 1;\n  tr.append(td1);\n\n  const td2 = document.createElement(\"td\");\n  td2.className = \"table__td\";\n  td2.innerHTML = `<a class=\"link\" href=\"${ round.view_url }\">${ round.quiz.topic }</a>`;\n  tr.append(td2);\n\n  const td3 = document.createElement(\"td\");\n  td3.className = \"table__td table__td--centered\";\n  td3.innerHTML = round.quiz.author;\n  tr.append(td3);\n\n  const td4 = document.createElement(\"td\");\n  td4.className = \"table__td table__td--centered\";\n  const relTimeSpan = document.createElement(\"span\");\n  relTimeSpan.dataset.timestamp = round.finish_time;\n  relTimeSpan.dataset.func = \"fromNow\";\n  relTimeSpan.dataset.refresh = 10000;\n  renderMomentDate(relTimeSpan); // adds innerHTML to element\n  td4.append(relTimeSpan);\n  tr.append(td4);\n\n  const td5 = document.createElement(\"td\");\n  td5.className = \"table__td table__td--centered\";\n  td5.innerHTML = (round.is_taken) ? \"yes\" : \"no\";\n  tr.append(td5);\n\n  const td6 = document.createElement(\"td\");\n  td6.className = \"table__td table__td--centered\";\n  if (isAdmin) td6.innerHTML = `<a class=\"link link--decorated\" href=\"${round.edit_url}\">✎</a>`;\n  tr.append(td6);\n\n  return tr;\n}\n\nconst renderRoundsTableBody = (activeFilter, rounds, isAdmin, parentId) => {\n  // apply current filter\n  const rows = (activeFilter === \"all\")\n    ? rounds\n    : rounds.filter(r => r.status === activeFilter);\n\n  // sort selected rows\n  if (activeFilter === \"finished\" || activeFilter === \"all\") {\n    rows.sort((a,b) => (a.finish_time > b.finish_time) ? -1 : 1);\n  } else {\n    rows.sort((a,b) => (a.finish_time > b.finish_time) ? 1 : -1);\n  }\n\n  // re-render\n  const node = document.getElementById(parentId);\n  node.innerHTML = \"\";\n  if (!rows.length) {\n    const tr = document.createElement(\"tr\");\n    tr.className = \"table__tr table__tr--odd\";\n    tr.innerHTML = '<td class=\"table__td\" colspan=\"6\">No rounds available.</td>';\n    node.append(tr);\n  } else {\n    rows.forEach((r,i) => {\n      node.append(makeRoundRow(r,i, isAdmin));\n    })\n  }\n}\n\n\nmodule.exports = renderRoundsTableBody;\n\n//# sourceURL=webpack://jsFuncs/./js/renderRoundsTableBody.js?");

/***/ }),

/***/ "./js/renderTournamentsTableBody.js":
/*!******************************************!*\
  !*** ./js/renderTournamentsTableBody.js ***!
  \******************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("const renderMomentDate = __webpack_require__(/*! ./renderMomentDate */ \"./js/renderMomentDate.js\");\n\n\nconst makeRow = (rowData, num, isAdmin) => {\n  const tr = document.createElement(\"tr\");\n  tr.className = \"table__tr\";\n  tr.classList.add(((num + 1) % 2) ? \"table__tr--odd\" : \"table__tr--even\");\n\n  const td1 = document.createElement(\"td\");\n  td1.className = \"table__td table__td--centered\";\n  td1.innerHTML = num + 1;\n  tr.append(td1);\n\n  const td2 = document.createElement(\"td\");\n  td2.className = \"table__td\";\n  td2.innerHTML = `<a class=\"link\" href=\"${ rowData.view_url }\">${ rowData.name }</a>`;\n  tr.append(td2);\n\n  const td3 = document.createElement(\"td\");\n  td3.className = \"table__td table__td--centered\";\n  td3.innerHTML = (rowData.is_active) ? \"yes\" : \"no\";\n  tr.append(td3);\n\n  const td4 = document.createElement(\"td\");\n  td4.className = \"table__td table__td--centered\";\n  const relTimeSpan = document.createElement(\"span\");\n  relTimeSpan.dataset.timestamp = rowData.time_created;\n  relTimeSpan.dataset.func = \"fromNow\";\n  relTimeSpan.dataset.refresh = 60000;\n  renderMomentDate(relTimeSpan); // adds innerHTML to element\n  td4.append(relTimeSpan);\n  tr.append(td4);\n\n  const td5 = document.createElement(\"td\");\n  td5.className = \"table__td table__td--centered\";\n  if (isAdmin) td5.innerHTML = `<a class=\"link link--decorated \" href=\"${rowData.edit_url}\">✎</a>`;\n  tr.append(td5);\n\n  return tr;\n}\n\n\nconst renderTournamentsTableBody = (activeFilter, tournaments, isAdmin, parentId) => {\n  // apply current filter\n  let rows = [...tournaments];\n  if (activeFilter === \"active\") rows = rows.filter(r => r.is_active)\n  else if (activeFilter === \"inactive\") rows = rows.filter(r => !r.is_active);\n\n  // sort selected rows\n  rows.sort((a,b) => {\n    if (a.is_active && !b.is_active) return -1;\n    if (!a.is_active && b.is_active) return 1;\n    if (a.time_created > b.time_created) return -1;\n  });\n\n  // re-render\n  const node = document.getElementById(parentId);\n  node.innerHTML = \"\";\n  if (!rows.length) {\n    const tr = document.createElement(\"tr\");\n    tr.className = \"table__tr table__tr--odd\";\n    tr.innerHTML = '<td class=\"table__td\" colspan=\"5\">No tournaments available.</td>';\n    node.append(tr);\n  } else {\n    rows.forEach((r,i) => {\n      node.append(makeRow(r,i, isAdmin));\n    })\n  }\n}\n\n\nmodule.exports = renderTournamentsTableBody;\n\n//# sourceURL=webpack://jsFuncs/./js/renderTournamentsTableBody.js?");

/***/ })

/******/ });