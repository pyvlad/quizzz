const setTimeToMidnight = (hoursInputId, minutesInputId) => {
  /* Note:
  Gecko notes
  Using setAttribute() to modify certain attributes, most notably value in XUL,
  works inconsistently, as the attribute specifies the default value.
  To access or modify the current values, you should use the properties.
  For example, use Element.value instead of Element.setAttribute().
  https://developer.mozilla.org/en-US/docs/Web/API/Element/setAttribute
  */
  document.querySelector(hoursInputId).value = "0";
  document.querySelector(minutesInputId).value = "0";
}


const renderDateTimeSelector = (prefix, timestamp, parentId) => {
  const obj = moment(timestamp);
  const dateValue = obj.format("YYYY-MM-DD");
  const hoursValue = obj.format("HH");
  const minutesValue = obj.format("mm");

  const container = document.createElement("div");
  container.className = "container";

  const row = document.createElement("div");
  row.className = "row";
  row.innerHTML = `
    <div class="col-6">
      <div class="form__input-help">date</div>
      <input class="form__input" type="date"
          id="${prefix}_date" name="${prefix}_date" value="${dateValue}">
    </div>
    <div class="col-offset-1 col-2">
      <div class="form__input-help">hours</div>
      <input class="form__input" type="number" min="0" max="23" required
          id="${prefix}_hours" name="${prefix}_hours" value="${hoursValue}">
    </div>
    <div class="col-offset-1 col-2">
      <div class="form__input-help">minutes</div>
      <input class="form__input" type="number" min="0" max="59" required
          id="${prefix}_minutes" name="${prefix}_minutes" value="${minutesValue}">
    </div>`;

  container.appendChild(row);

  const row2 = document.createElement("div");
  row2.className = "row";
  const div = document.createElement("div");
  div.className = "col-offset-7 col-5";
  const subDiv = document.createElement("div");
  subDiv.className = "link link--grey text-small text-centered";
  subDiv.innerText = "set to midnight";
  subDiv.onclick = () => setTimeToMidnight(`#${prefix}_hours`, `#${prefix}_minutes`);
  
  div.appendChild(subDiv);
  row2.appendChild(div);
  container.appendChild(row2);

  const parentNode = document.getElementById(parentId);
  parentNode.innerHTML = "";
  parentNode.appendChild(container);

  return container;
}


module.exports = renderDateTimeSelector;