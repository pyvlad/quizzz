const renderQuizSelector = (quizId, quizPool) => {


  const makeTableRow = (quiz, num, onSelectQuiz) => {
    const tr = document.createElement("tr");
    tr.className = "table__tr";
    tr.classList.add(((num + 1) % 2) ? "table__tr--odd" : "table__tr--even");

    let td;

    td = document.createElement("td");
    td.className = "table__td";
    td.innerHTML = quiz.author;
    tr.append(td);

    td = document.createElement("td");
    td.className = "table__td";
    td.innerHTML = quiz.topic;
    tr.append(td);

    td = document.createElement("td");
    td.className = "table__td table__td--centered";
    const momentObj = moment(quiz.time_submitted);
    td.innerHTML = momentObj.format("YYYY-MM-DD HH:mm");
    tr.append(td);

    tr.onclick = () => onSelectQuiz(quiz.id);

    return tr;
  }


  const makeQuizPoolTable = (quizPool, onSelectQuiz) => {
    // table with choices
    const table = document.createElement("table");
    table.className = "table table--full-width";

    // column names
    const thead = document.createElement("thead");
    thead.innerHTML = `<tr>
        <th width="25%">Author</th>
        <th width="35%">Name</th>
        <th width="40%">Submitted</th>
      </tr>`;
    table.append(thead);

    // quiz pool
    const tbody = document.createElement("tbody");
    if (!quizPool.length) {
      const tr = document.createElement("tr");
      tr.className = "table__tr table__tr--odd";
      tr.innerHTML = '<td class="table__td" colspan="3">No quizzes available.</td>';
      tbody.append(tr);
    } else {
      quizPool.forEach((r,i) => {
        tbody.append(makeTableRow(r, i, onSelectQuiz));
      })
    }
    table.append(tbody);

    return table;
  }


  const makeSelectedQuizTable = (selectedQuiz) => {
    // table with selection
    const table = document.createElement("table");
    table.className = "table table--full-width table--colorful";

    const thead = document.createElement("thead");
    const tr = document.createElement("tr");
    if (selectedQuiz) {
      const momentObj = moment(selectedQuiz.time_submitted);
      const quizTime = momentObj.format("YYYY-MM-DD HH:mm");
      tr.innerHTML = `
          <th width="25%">${selectedQuiz.author}</th>
          <th width="35%">${selectedQuiz.topic}</th>
          <th width="40%">${quizTime}</th>`;
    } else {
      tr.innerHTML = '<th colspan="3">No quiz selected.</th>';
    }
    thead.append(tr);
    table.append(thead);

    return table;
  }


  const makeContainer = (quizPool, selectedQuizId, onSelectQuiz) => {
    let selectedQuiz = quizPool.filter(q => q.id === selectedQuizId);
    selectedQuiz = (selectedQuiz.length) ? selectedQuiz[0] : null;

    // container
    const div = document.createElement("div");
    // table with selected quiz
    const table1 = makeSelectedQuizTable(selectedQuiz);
    div.append(table1);
    // header
    const help = document.createElement("button");
    help.className = "btn btn--grey my-2";
    help.innerHTML = "Show quiz pool";
    function toggleQuizPool(e) {
      e.preventDefault();
      if (table2.hidden) {
        table2.hidden = false;
        this.innerHTML = "Hide quiz pool";
      } else {
        table2.hidden = true;
        this.innerHTML = "Show quiz pool";
      }
    }
    help.onclick = toggleQuizPool;
    div.append(help);
    // table with quiz pool
    const table2 = makeQuizPoolTable(quizPool, onSelectQuiz);
    table2.hidden = true;
    div.append(table2);

    return div;
  }


  const handleSelectQuiz = (quizId) => {
    document.querySelector("#selectedQuizId").value = quizId;
    const container = makeContainer(quizPool, quizId, handleSelectQuiz);  // closure
    const parent = document.querySelector("#selectQuiz");
    parent.innerHTML = "";
    parent.append(container);
  }

  // initial selection
  handleSelectQuiz(quizId);
}


module.exports = renderQuizSelector;