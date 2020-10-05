const renderMomentDate = require("./renderMomentDate");


const makeChatMessageHTML = (msg) => {
    const article = document.createElement("article");
    article.className = "message";
    if (msg.is_own) article.classList.add("message--own");

    const detailsDiv = document.createElement("div");
    detailsDiv.className = "message__details";
    article.append(detailsDiv);

    const containerDiv = document.createElement("div");
    containerDiv.className = "message__details-main";

    const authorDiv = document.createElement("div");
    authorDiv.className = "message__details-item message__author";
    authorDiv.innerHTML = msg.user_name;
    containerDiv.append(authorDiv);

    if (msg.is_own) {
        const editLink = document.createElement("a");
        editLink.href = msg.edit_url;
        editLink.className = "btn btn--secondary message__details-item";
        editLink.innerHTML = "edit";
        containerDiv.append(editLink);
    }

    const relTimeDiv = document.createElement("div");
    relTimeDiv.dataset.timestamp = msg.time_created;
    relTimeDiv.dataset.func = "fromNow";
    relTimeDiv.dataset.refresh = 10000;
    renderMomentDate(relTimeDiv); // adds innerHTML to element
    relTimeDiv.className = "message__details-item";
    containerDiv.append(relTimeDiv);

    detailsDiv.append(containerDiv);

    const timeDiv = document.createElement("div");
    timeDiv.innerHTML = moment(msg.time_created).format("MMM D, YYYY [at] h:mm a");
    timeDiv.className = "message__details-item";
    detailsDiv.append(timeDiv);

    const msgText = document.createElement("p");
    msgText.className = "message__text";
    msgText.innerHTML = msg.text;

    article.append(detailsDiv);
    article.append(msgText);
    if (msg.time_updated) {
        const timeUpdatedDiv = document.createElement("div");
        timeUpdatedDiv.className = "message__edited";
        timeUpdatedDiv.innerHTML = (
            "last edit: " + moment(msg.time_updated).format("MMM D, YYYY [at] h:mm a"));
        article.append(timeUpdatedDiv);
    }

    return article;
}



const makePaginationHTML = (pagination) => {
    const wrapperDiv = document.createElement("div");
    wrapperDiv.className = "pagination";

    // add left div to move back to previous and first pages
    const backDiv = document.createElement("div");

    const firstPageLink = document.createElement("a");
    firstPageLink.className = "pagination-button";
    if (pagination.has_prev) {
        firstPageLink.addEventListener("click", () => loadChat(pagination.link_to_first));
    }
    firstPageLink.innerHTML = "<<";
    backDiv.append(firstPageLink);

    const prevPageLink = document.createElement("a");
    prevPageLink.className = "pagination-button";
    if (pagination.has_prev) {
        prevPageLink.addEventListener("click", () => loadChat(pagination.prev_link));
    }
    prevPageLink.innerHTML = "prev";
    backDiv.append(prevPageLink);

    wrapperDiv.append(backDiv);

    // add middle div to show where we are
    const currentPageDiv = document.createElement("div");
    currentPageDiv.innerHTML = `${pagination.page} / ${pagination.total_pages}`;
    wrapperDiv.append(currentPageDiv);

    // add right div to move forward
    const forwardDiv = document.createElement("div");

    const nextPageLink = document.createElement("a");
    nextPageLink.className = "pagination-button";
    if (pagination.has_next) {
        nextPageLink.addEventListener("click", () => loadChat(pagination.next_link));
    }
    nextPageLink.innerHTML = "next";
    forwardDiv.append(nextPageLink);

    const lastPageLink = document.createElement("a");
    lastPageLink.className = "pagination-button";
    if (pagination.has_next) {
        lastPageLink.addEventListener("click", () => loadChat(pagination.link_to_last));
    }
    lastPageLink.innerHTML = ">>";
    forwardDiv.append(lastPageLink);

    wrapperDiv.append(forwardDiv);

    return wrapperDiv;
}



const loadChat = (url) => {
  fetch(url)
    .then((response) => {
      if (response.ok) return response.json()
      else throw new Error("Request Failed");
    }).then((data) => {
      const { pagination, messages } = data;

      const messagesDiv = document.getElementById("message_list");
      messagesDiv.innerHTML = "";
      if (messages.length) {
          for (let message of messages) {
            let messageHTML = makeChatMessageHTML(message);
            messagesDiv.append(messageHTML);
          }
      } else {
          messagesDiv.innerHTML = "<p>No messages here yet. Be the first to say something!</p>"
      }

      const paginationDiv = document.getElementById("pagination");
      paginationHTML = makePaginationHTML(pagination);
      paginationDiv.innerHTML = "";

      paginationDiv.append(paginationHTML);
    }).catch(
      e => console.log(e)
    );
}


module.exports = loadChat;