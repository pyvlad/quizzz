const renderMomentDate = require("./renderMomentDate");


const makeRoundRow = (round, num, isAdmin) => {
  const tr = document.createElement("tr");
  tr.className = "table__tr";
  tr.classList.add(((num + 1) % 2) ? "table__tr--odd" : "table__tr--even");

  const td1 = document.createElement("td");
  td1.className = "table__td table__td--centered";
  td1.innerHTML = num + 1;
  tr.append(td1);

  const td2 = document.createElement("td");
  td2.className = "table__td";
  td2.innerHTML = `<a class="link" href="${ round.view_url }">${ round.quiz.topic }</a>`;
  tr.append(td2);

  const td3 = document.createElement("td");
  td3.className = "table__td table__td--centered";
  td3.innerHTML = round.quiz.author;
  tr.append(td3);

  const td4 = document.createElement("td");
  td4.className = "table__td table__td--centered";
  const relTimeSpan = document.createElement("span");
  relTimeSpan.dataset.timestamp = round.finish_time;
  relTimeSpan.dataset.func = "fromNow";
  relTimeSpan.dataset.refresh = 10000;
  renderMomentDate(relTimeSpan); // adds innerHTML to element
  td4.append(relTimeSpan);
  tr.append(td4);

  const td5 = document.createElement("td");
  td5.className = "table__td table__td--centered";
  td5.innerHTML = (round.is_taken) ? "yes" : "no";
  tr.append(td5);

  const td6 = document.createElement("td");
  td6.className = "table__td table__td--centered";
  if (isAdmin) td6.innerHTML = `<a class="link link--decorated" href="${round.edit_url}">✎</a>`;
  tr.append(td6);

  return tr;
}

const renderRoundsTableBody = (activeFilter, rounds, isAdmin, parentId) => {
  // apply current filter
  const rows = (activeFilter === "all")
    ? rounds
    : rounds.filter(r => r.status === activeFilter);

  // sort selected rows
  if (activeFilter === "finished" || activeFilter === "all") {
    rows.sort((a,b) => (a.finish_time > b.finish_time) ? -1 : 1);
  } else {
    rows.sort((a,b) => (a.finish_time > b.finish_time) ? 1 : -1);
  }

  // re-render
  const node = document.getElementById(parentId);
  node.innerHTML = "";
  if (!rows.length) {
    const tr = document.createElement("tr");
    tr.className = "table__tr table__tr--odd";
    tr.innerHTML = '<td class="table__td" colspan="6">No rounds available.</td>';
    node.append(tr);
  } else {
    rows.forEach((r,i) => {
      node.append(makeRoundRow(r,i, isAdmin));
    })
  }
}


module.exports = renderRoundsTableBody;