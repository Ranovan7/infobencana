from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from apps.models import Desa, Pos
from datetime import datetime
import wtforms as wtf

jenis_kejadian = (
    ('Tanah Longsor', "Tanah Longsor"),
    ('Banjir', "Banjir")
)
all_desa = Desa.query.all()
all_pos = Pos.query.all()
select_desa = [(desa.id, f"{desa.desa}, {desa.kecamatan}, {desa.kabupaten}") for desa in all_desa]
select_pos = [(pos.id, pos.pos_name) for pos in all_pos]


class LoginForm(FlaskForm):
    username = wtf.StringField('username', validators=[DataRequired(), Length(max=15)])
    password = wtf.PasswordField('password', validators=[DataRequired()])
    submit = wtf.SubmitField()


class UserForm(FlaskForm):
    username = wtf.StringField('Username', validators=[DataRequired()])
    password = wtf.PasswordField('Password', validators=[DataRequired()])
    password2 = wtf.PasswordField('Verifikasi Password', validators=[DataRequired()])
    submit = wtf.SubmitField()


class KejadianForm(FlaskForm):
    ''' Form Kejadian '''
    waktu = wtf.DateTimeField("Waktu Bencana", format="%d-%m-%Y", validators=[DataRequired()], default=datetime.now())  # wajib
    jenis = wtf.SelectField("Jenis", choices=jenis_kejadian, validators=[DataRequired()], default="Tanah Longsor")  # wajib
    sebab = wtf.TextAreaField("Sebab", default="Belum Diketahui", validators=[DataRequired()])  # wajib
    nama_sungai = wtf.TextAreaField("Nama Sungai", default="Belum Diketahui")
    sungai = wtf.IntegerField("Sungai", default=0)
    sawah = wtf.IntegerField("Sawah", default=0)
    bangunan = wtf.IntegerField("Bangunan Pengairan", default=0)
    jalan = wtf.IntegerField("Jalan", default=0)
    jalan_putus = wtf.IntegerField("Jalan putus", default=0)
    jembatan = wtf.IntegerField("Jembatan", default=0)
    lama = wtf.IntegerField("Lama Bencana", default=0)
    tindakan = wtf.TextAreaField("Tindakan", default="Belum Ada", validators=[DataRequired()])  # wajib
    submit = wtf.SubmitField()


class DampakDesaForm(FlaskForm):
    ''' Form Desa yang terkena dampak Kejadian '''
    desa = wtf.SelectField("Desa", choices=select_desa, validators=[DataRequired()], default=select_desa[0][0], coerce=int)
    str_wilayah = wtf.StringField("Str Wilayah", validators=[Length(max=100)])
    rumah = wtf.IntegerField("Rumah", default=0)
    sekolah = wtf.IntegerField("Sekolah", default=0)
    t_ibadah = wtf.IntegerField("Tempat Ibadah", default=0)
    md = wtf.IntegerField("Meninggal Dunia", default=0)
    luka = wtf.IntegerField("Luka", default=0)
    hilang = wtf.IntegerField("Hilang", default=0)
    pengungsi = wtf.IntegerField("Pengungsi", default=0)
    submit = wtf.SubmitField()


class SumberHidrologiForm(FlaskForm):
    ''' Form Sumber Hidrologi Kejadian '''
    pos = wtf.SelectField("Pos", choices=select_pos, validators=[DataRequired()], default=select_pos[0][0], coerce=int)
    ch = wtf.IntegerField("Curah Hujan", default=0)
    durasi = wtf.IntegerField("Durasi", default=0)
    submit = wtf.SubmitField()


class FotoForm(FlaskForm):
    ''' Form input Foto Kejadian '''
    foto = wtf.MultipleFileField(label="Upload Foto")
    submit = wtf.SubmitField()
