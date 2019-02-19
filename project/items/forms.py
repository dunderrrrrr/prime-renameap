from flask_wtf import FlaskForm as BaseForm
from wtforms.fields import StringField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired

class MainForm(BaseForm):
    inputArea = StringField('Data', widget=TextArea(), validators=[DataRequired()])
