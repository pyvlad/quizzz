const renderMomentDate = (el) => {
  const {timestamp, func, format, refresh} = el.dataset;
  const obj = moment(timestamp);
  const args = [];
  if (format) args.push(format);
  const val = obj[func].apply(obj, args);
  el.innerHTML = val;
  if (refresh) {
      setTimeout(() => renderMomentDate(el), refresh);
  }
}


module.exports = renderMomentDate;