from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class CreateForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=100)])
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0)])
    category = StringField("Category", validators=[Optional(), Length(min=2, max=50)])
    submit = SubmitField("Valider") 

    

class DeleteForm(FlaskForm):
    user_id = StringField("ID de l'entrée à supprimer", validators=[DataRequired()])
    submit = SubmitField("Supprimer")


class UpdateForm(FlaskForm):
    id = StringField("ID", validators=[DataRequired()])
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=100)])
    amount = DecimalField("Montant", validators=[
        DataRequired(),
        NumberRange(min=0, message="Le montant doit être positif")
    ])
    category = StringField("Catégorie", validators=[Optional(), Length(max=50)])
    submit = SubmitField("Mettre à jour")    

