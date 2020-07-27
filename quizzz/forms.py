from flask_wtf import FlaskForm
from wtforms.widgets import html_params
from wtforms.validators import Length, Regexp
from markupsafe import Markup, escape


class EmptyForm(FlaskForm):
    """ Reusable empty form with a CSRF token. """
    pass


def add_params_from_field_validators_to_kwargs(kwargs, field):
    """ Helper funtion for reuse. """
    for validator in field.validators:
        if isinstance(validator, Length):

            maxlength = getattr(validator, 'max')
            if maxlength not in (-1, None):
                kwargs.setdefault('maxlength', maxlength)

            minlength = getattr(validator,'min')
            if minlength not in (-1, None):
                kwargs.setdefault('minlength', minlength)
                kwargs.setdefault('required', True)

        if isinstance(validator, Regexp):
            kwargs["pattern"] = validator.regex.pattern


class ValidatedInput:
    """
    Render a basic ``<input>`` field.
    This is used as the basis for most of the other input fields.
    By default, the `_value()` method will be called upon the associated field
    to provide the ``value=`` HTML attribute.

    Adds html5 minlength, maxlength, required.
    Based on: https://github.com/wtforms/wtforms/issues/337
    """
    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)

        if not self.hide_value:
            if 'value' not in kwargs:
                kwargs['value'] = field._value()
        if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
            kwargs['required'] = True

        add_params_from_field_validators_to_kwargs(kwargs, field)

        return Markup('<input %s>' % self.html_params(name=field.name, **kwargs))


class ValidatedTextInput(ValidatedInput):
    input_type = "text"
    hide_value = False


class ValidatedPasswordInput(ValidatedInput):
    input_type = "password"
    hide_value = True


class ValidatedTextArea:
    """
    Renders a multi-line text area.
    `rows` and `cols` ought to be passed as keyword args when rendering.
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
            kwargs['required'] = True

        add_params_from_field_validators_to_kwargs(kwargs, field)

        return Markup('<textarea %s>\r\n%s</textarea>' % (
            html_params(name=field.name, **kwargs),
            escape(field._value())
        ))
