const addFilters = (filters, parentNodeId, onSelect) => {
  /*
      <filters>:      array of [k,v] arrays where:
          k - filter name
          v - boolean whether it is selected or not
      <parentNodeId>: ID of the node where to append filter buttons
      <onSelect>:     callback to call when selected filter is changed,
                      <activeFilter> is passed as argument;
  */
  let filterSelection = [...filters];

  const getActiveFilter = () => filterSelection.reduce((acc, [k,v]) => v ? k : acc, null);

  const selectFilter = (e, filter) => {
      e.preventDefault();
      filterSelection = filterSelection.map(
          ([k,v]) => ((k === filter) ? [k,true] : [k,false])
      );
      renderFilters();
      onSelect(getActiveFilter());
  }

  const renderFilters = () => {
      const parentNode = document.getElementById(parentNodeId);
      // delete previously shown rows:
      parentNode.innerHTML = "";
      // append row by row:
      for (let [k,v] of filterSelection) {
          const link = document.createElement("a");
          link.className = "tabs__button";
          if (v) link.classList.add("tabs__button--active");
          link.onclick = (e) => selectFilter(e, k);
          link.href = "?filter=" + k;
          link.innerHTML = k[0].toUpperCase() + k.slice(1);

          parentNode.append(link);
      }
  }

  // initial render
  renderFilters();
  onSelect(getActiveFilter());
}


module.exports = addFilters;