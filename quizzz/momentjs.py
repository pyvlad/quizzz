from datetime import datetime
from jinja2 import Markup

REFRESH_INTERVAL = 10000
DEFAULT_FORMAT = '"MMM D, YYYY [at] h:mm a"'


class momentjs:
    def __init__(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.timestamp = timestamp

    def _timestamp_as_iso_8601(self):
        return self.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _render(self, func, fmt=None, refresh=False):
        t = self._timestamp_as_iso_8601()
        data = {
            "data-timestamp": t,
            "data-func": func,
            "data-refresh": int(refresh) * REFRESH_INTERVAL,
        }
        if fmt:
            data["data-format"] = fmt
        data_values = " ".join("%s=%s" % (k,v) for k,v in data.items())
        html = '<span class="momentjs-date" {}></span>'.format(data_values)
        return Markup(html)

    def format(self, fmt=DEFAULT_FORMAT, refresh=False):
        return self._render('format', fmt, refresh=refresh)

    def calendar(self):
        return self._render('calendar')

    def fromNow(self, refresh=False):
        return self._render('fromNow', refresh=refresh)


class MomentJS:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # make <momentjs> call available in templates:
        app.jinja_env.globals['momentjs'] = momentjs
