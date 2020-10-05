const renderMomentDate = require('./renderMomentDate');


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
  td2.innerHTML = rowData.name;
  tr.append(td2);

  const td3 = document.createElement("td");
  td3.className = "table__td table__td--centered";
  td3.innerHTML = rowData.user_id;
  tr.append(td3);

  const td4 = document.createElement("td");
  td4.className = "table__td table__td--centered";
  const timeSpan = document.createElement("span");
  timeSpan.dataset.timestamp = rowData.time_created;
  timeSpan.dataset.func = "format";
  timeSpan.dataset.format = "MMM D, YYYY [at] h:mm a";
  renderMomentDate(timeSpan); // adds innerHTML to element
  td4.append(timeSpan);
  tr.append(td4);

  const td5 = document.createElement("td");
  td5.className = "table__td table__td--centered";
  td5.innerHTML = rowData.is_admin ? "admin" : "";
  tr.append(td5);

  const td6 = document.createElement("td");
  td6.className = "table__td table__td--centered";
  if (isAdmin && !rowData.is_admin) {
    td6.innerHTML = `<a class="link link--decorated" href="${rowData.edit_url}">✎</a>`;
  }
  tr.append(td6);

  return tr;
}


const renderMembersTableBody = (members, isAdmin, parentId) => {
  // apply current filter
  let rows = [...members];

  // sort selected rows
  rows.sort((a,b) => (a.name > b.name) ? 1 : -1);

  // re-render
  const node = document.getElementById(parentId);
  node.innerHTML = "";
  rows.forEach((r,i) => {
    node.append(makeRow(r,i,isAdmin));
  })
}


module.exports = renderMembersTableBody;