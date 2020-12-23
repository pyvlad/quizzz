from math import ceil

from flask import abort, request


def paginate(query, page=None, per_page=None, error_out=True, max_per_page=None, count=True):
    """
    Returns ``per_page`` items from page ``page``.
    If ``page`` or ``per_page`` are ``None``, they will be retrieved from the request query.
    If ``max_per_page`` is specified, ``per_page`` will be limited to that value.
    If there is no request or they aren't in the query, they default to 1 and 20 respectively.
    If ``count`` is ``False``, no query to help determine total page count will be run.
    When ``error_out`` is ``True`` (default), the following rules will
    cause a 404 response:
    * No items are found and ``page`` is not 1.
    * ``page`` is less than 1, or ``per_page`` is negative.
    * ``page`` or ``per_page`` are not ints.
    When ``error_out`` is ``False``, ``page`` and ``per_page`` default to
    1 and 20 respectively.
    Returns a :class:`Pagination` object.
    """
    if request:
        if page is None:
            try:
                page = int(request.args.get("page", 1))
            except (TypeError, ValueError):
                if error_out:
                    abort(404)

                page = 1

        if per_page is None:
            try:
                per_page = int(request.args.get("per_page", 20))
            except (TypeError, ValueError):
                if error_out:
                    abort(404)

                per_page = 20
    else:
        if page is None:
            page = 1

        if per_page is None:
            per_page = 20

    if max_per_page is not None:
        per_page = min(per_page, max_per_page)

    if page < 1:
        if error_out:
            abort(404)
        else:
            page = 1

    if per_page < 0:
        if error_out:
            abort(404)
        else:
            per_page = 20

    if not count:
        total = None
    else:
        total = query.order_by(None).count()

    return Pagination(query, page, per_page, total, error_out)



class Pagination:
    """Internal helper class returned by :meth:`BaseQuery.paginate`."""
    def __init__(self, query, page, per_page, total, error_out):
        #: the unlimited query object that was used to create this
        #: pagination object.
        self.query = query
        #: the current page number (1 indexed)
        self.page = page
        #: the number of items to be displayed on a page.
        self.per_page = per_page
        #: the total number of items matching the query
        self.total = total
        self.error_out = error_out
        #: the items for current page
        self._items = None

    def get_items(self):
        """The items for the current page. """
        if self._items:
            return self._items

        items = self.query.limit(self.per_page).offset((self.page - 1) * self.per_page).all()
        if not items and self.page != 1 and self.error_out:
            abort(404)

        self._items = items

        return items

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0 or self.total is None:
            pages = 0
        else:
            pages = ceil(self.total / self.per_page)
        return pages

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    @property
    def prev_num(self):
        """Number of the previous page."""
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        if not self.has_next:
            return None
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides.  Skipped page numbers are represented as `None`.
        This is how you could render such a pagination in the templates:
        .. sourcecode:: html+jinja
            {% macro render_pagination(pagination, endpoint) %}
              <div class=pagination>
              {%- for page in pagination.iter_pages() %}
                {% if page %}
                  {% if page != pagination.page %}
                    <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
                  {% else %}
                    <strong>{{ page }}</strong>
                  {% endif %}
                {% else %}
                  <span class=ellipsis>…</span>
                {% endif %}
              {%- endfor %}
              </div>
            {% endmacro %}
        """
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left_edge
                or (
                    num > self.page - left_current - 1
                    and num < self.page + right_current
                )
                or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num
