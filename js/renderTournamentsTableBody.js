const renderMomentDate = require("./renderMomentDate");


const makeRow = (rowData, num, isAdmin) => {
  const tr = document.createElement("tr");
  tr.className = "table__tr";
  tr.classList.add(((num + 1) % 2) ? "table__tr--odd" : "table__tr--even");

  const td1 = document.createElement("td");
  td1.className = "table__td table__td--centered";
  td1.innerHTML = num + 1;
  tr.append(td1);

  const td2 = document.createElement("td");
  td2.className = "table__td";
  td2.innerHTML = `<a class="link" href="${ rowData.view_url }">${ rowData.name }</a>`;
  tr.append(td2);

  const td3 = document.createElement("td");
  td3.className = "table__td table__td--centered";
  td3.innerHTML = (rowData.is_active) ? "yes" : "no";
  tr.append(td3);

  const td4 = document.createElement("td");
  td4.className = "table__td table__td--centered";
  const relTimeSpan = document.createElement("span");
  relTimeSpan.dataset.timestamp = rowData.time_created;
  relTimeSpan.dataset.func = "fromNow";
  relTimeSpan.dataset.refresh = 60000;
  renderMomentDate(relTimeSpan); // adds innerHTML to element
  td4.append(relTimeSpan);
  tr.append(td4);

  const td5 = document.createElement("td");
  td5.className = "table__td table__td--centered";
  if (isAdmin) td5.innerHTML = `<a class="link link--decorated " href="${rowData.edit_url}">✎</a>`;
  tr.append(td5);

  return tr;
}


const renderTournamentsTableBody = (activeFilter, tournaments, isAdmin, parentId) => {
  // apply current filter
  let rows = [...tournaments];
  if (activeFilter === "active") rows = rows.filter(r => r.is_active)
  else if (activeFilter === "inactive") rows = rows.filter(r => !r.is_active);

  // sort selected rows
  rows.sort((a,b) => {
    if (a.is_active && !b.is_active) return -1;
    if (!a.is_active && b.is_active) return 1;
    if (a.time_created > b.time_created) return -1;
  });

  // re-render
  const node = document.getElementById(parentId);
  node.innerHTML = "";
  if (!rows.length) {
    const tr = document.createElement("tr");
    tr.className = "table__tr table__tr--odd";
    tr.innerHTML = '<td class="table__td" colspan="5">No tournaments available.</td>';
    node.append(tr);
  } else {
    rows.forEach((r,i) => {
      node.append(makeRow(r,i, isAdmin));
    })
  }
}


module.exports = renderTournamentsTableBody;