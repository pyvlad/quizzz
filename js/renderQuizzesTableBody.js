const renderMomentDate = require("./renderMomentDate");


const makeRow = (rowData, num) => {
  const tr = document.createElement("tr");
  tr.className = "table__tr";
  tr.classList.add(((num + 1) % 2) ? "table__tr--odd" : "table__tr--even");

  const td1 = document.createElement("td");
  td1.className = "table__td table__td--centered";
  td1.innerHTML = num + 1;
  tr.append(td1);

  const td2 = document.createElement("td");
  td2.className = "table__td";
  td2.innerHTML = `<a class="link" href="${ rowData.edit_url }">"${ rowData.topic }"</a>`;
  tr.append(td2);

  const td3 = document.createElement("td");
  td3.className = "table__td table__td--centered";
  td3.innerHTML = (rowData.is_submitted) ? "yes" : "no";
  tr.append(td3);

  const td4 = document.createElement("td");
  td4.className = "table__td table__td--centered";
  const relTimeSpan = document.createElement("span");
  relTimeSpan.dataset.timestamp = rowData.last_update;
  relTimeSpan.dataset.func = "fromNow";
  relTimeSpan.dataset.refresh = 60000;
  renderMomentDate(relTimeSpan); // adds innerHTML to element

  const timeDiv = document.createElement("div");
  timeDiv.dataset.timestamp = rowData.last_update;
  timeDiv.dataset.func = "format";
  timeDiv.dataset.format = "MMM D, YYYY [at] h:mm a";
  renderMomentDate(timeDiv);
  timeDiv.hidden = true;

  td4.append(relTimeSpan);
  td4.append(timeDiv);
  td4.onclick = () => {
    timeDiv.hidden = !timeDiv.hidden;
  }
  tr.append(td4);

  return tr;
}


const renderQuizzesTableBody = (activeFilter, quizzes, parentId) => {
  // apply current filter
  let rows = [...quizzes];
  if (activeFilter === "submitted") rows = rows.filter(r => r.is_submitted)
  else if (activeFilter === "unfinished") rows = rows.filter(r => !r.is_submitted);

  // sort selected rows
  rows.sort((a,b) => {
    if (a.is_submitted && !b.is_submitted) return 1;
    if (!a.is_submitted && b.is_submitted) return -1;
    if (a.last_update > b.last_update) return -1;
  });

  // re-render
  const node = document.getElementById(parentId);
  node.innerHTML = "";
  if (!rows.length) {
    const tr = document.createElement("tr");
    tr.className = "table__tr table__tr--odd";
    tr.innerHTML = '<td class="table__td" colspan="5">Nothing here.</td>';
    node.append(tr);
  } else {
    rows.forEach((r,i) => {
      node.append(makeRow(r,i));
    })
  }
}


module.exports = renderQuizzesTableBody;