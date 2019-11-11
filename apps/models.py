import os
import json
from datetime import datetime, timedelta
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from apps import login, db

kalender = [
    'Pilih',
    'Januari',
    'Februari',
    'Maret',
    'April',
    'Mei',
    'Juni',
    'Juli',
    'Agustus',
    'September',
    'Oktober',
    'November',
    'Desember',
]


class Kejadian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    waktu = db.Column(db.DateTime)
    jenis = db.Column(db.String(35))
    sebab = db.Column(db.String(1000))  # kronologi kejadian
    nama_sungai = db.Column(db.String(1000))
    sungai = db.Column(db.Integer, nullable=True, default=None)  # dalam meter
    sawah = db.Column(db.Integer, nullable=True, default=None)  # dalam hektar
    bangunan = db.Column(db.Integer, nullable=True, default=None)  # unit rusak
    jalan = db.Column(db.Integer, nullable=True, default=None)  # jalan tergenang dalam meter
    jalan_putus = db.Column(db.Integer, nullable=True, default=None)  # jalan terputus dalam titik
    jembatan = db.Column(db.Integer, nullable=True, default=None)  # jembatan putus dalam unit
    lama = db.Column(db.Integer, nullable=True, default=None)  # hari diperkirakan lumpuh
    tindakan = db.Column(db.String(1000))  # penanganan
    dampakdesa = db.relationship('DampakDesa', backref='kejadian', lazy='dynamic')
    hidrologi = db.relationship('SumberHidrologi', backref='kejadian', lazy='dynamic')
    foto = db.relationship('Foto', backref='kejadian', lazy='dynamic')
    cdate = db.Column(db.DateTime, default=datetime.now)
    mdate = db.Column(db.DateTime, default=None)
    cuser = db.Column(db.String(15))
    muser = db.Column(db.String(15))

    def get_date(self):
        return self.waktu.strftime("%d %b %Y")

    def get_date_id(self):
        return f"{self.waktu.day} {kalender[self.waktu.month]} {self.waktu.year}"

    def get_date_before(self):
        yesterday = self.waktu - timedelta(days=1)
        return f"{yesterday.day} {kalender[yesterday.month]} {yesterday.year}"

    @property
    def dampakdesa_count(self):
        count = 0
        for i in self.dampakdesa:
            count += 1
        return count

    @property
    def get_random_point(self):
        point = None
        for desa in self.dampakdesa:
            point = desa.desa.get_point
            break
        return point

    @property
    def get_affected_area(self):
        ''' Return area of surface of the affected desa in Km^2 '''
        affected_areas = []
        for dd in self.dampakdesa:
            affected_areas.append(dd.desa.get_area)
        affected_area = sum(affected_areas)
        return round(affected_area, 2)

    @property
    def date(self):
        return self.waktu.strftime("%d %m %Y")

    @property
    def rusak_desa(self):
        result = {}
        for dd in self.dampakdesa:
            if dd.desa.kecamatan not in result:
                result[dd.desa.kecamatan] = {
                    "dd": [dd],
                    "rumah": dd.rumah,
                    "sekolah": dd.sekolah,
                    "t_ibadah": dd.t_ibadah,
                }
            else:
                result[dd.desa.kecamatan]['dd'].append(dd)
                result[dd.desa.kecamatan]['rumah'] += dd.rumah
                result[dd.desa.kecamatan]['sekolah'] += dd.sekolah
                result[dd.desa.kecamatan]['t_ibadah'] += dd.t_ibadah
        return result

    @property
    def sort_desa(self):
        result = {}
        for dd in self.dampakdesa:
            if dd.desa.propinsi not in result:
                result[dd.desa.propinsi] = {}

            if dd.desa.kabupaten not in result[dd.desa.propinsi]:
                result[dd.desa.propinsi][dd.desa.kabupaten] = {}

            if dd.desa.kecamatan not in result[dd.desa.propinsi][dd.desa.kabupaten]:
                result[dd.desa.propinsi][dd.desa.kabupaten][dd.desa.kecamatan] = f"{dd.desa.desa}"
            else:
                result[dd.desa.propinsi][dd.desa.kabupaten][dd.desa.kecamatan] += f", {dd.desa.desa}"
        return result

    @property
    def summary(self):
        result = {
            'korban': {
                'luka': sum([i.luka for i in self.dampakdesa]),
                'md': sum([i.md for i in self.dampakdesa]),
                'hilang': sum([i.hilang for i in self.dampakdesa]),
                'pengungsi': sum([i.pengungsi for i in self.dampakdesa]),
            },
            'bangunan': {
                'rumah': sum([i.rumah for i in self.dampakdesa]),
                'sekolah': sum([i.sekolah for i in self.dampakdesa]),
                't_ibadah': sum([i.t_ibadah for i in self.dampakdesa]),
            }
        }
        result['korban']['total'] = sum([result['korban'][key] for key in result['korban']])
        result['bangunan']['total'] = sum([result['bangunan'][key] for key in result['bangunan']])
        result['air'] = {
            'total': (self.sungai + self.sawah + self.bangunan)
        }
        result['jalan'] = {
            'total': (self.jalan + self.jalan_putus + self.jembatan)
        }
        return result


class DampakDesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kejadian_id = db.Column(db.Integer, db.ForeignKey('kejadian.id'))
    desa_id = db.Column(db.Integer, db.ForeignKey('desa.id'))
    str_wilayah = db.Column(db.String(100))
    rumah = db.Column(db.Integer)
    sekolah = db.Column(db.Integer)
    t_ibadah = db.Column(db.Integer)
    md = db.Column(db.Integer)
    luka = db.Column(db.Integer)
    hilang = db.Column(db.Integer)
    pengungsi = db.Column(db.Integer)
    geom = db.Column(db.String(1000))
    cdate = db.Column(db.DateTime, default=datetime.now)
    mdate = db.Column(db.DateTime)
    cuser = db.Column(db.String(15))
    muser = db.Column(db.String(15))

    __tablename__ = 'dampak_desa'


class SumberHidrologi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kejadian_id = db.Column(db.Integer, db.ForeignKey('kejadian.id'))
    pos_id = db.Column(db.Integer, db.ForeignKey('pos.id'))
    ch = db.Column(db.Integer)
    durasi = db.Column(db.Integer)
    cdate = db.Column(db.DateTime, default=datetime.now)
    mdate = db.Column(db.DateTime)
    cuser = db.Column(db.String(15))
    muser = db.Column(db.String(15))

    __tablename__ = 'sumber_hidrologi'


class Foto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kejadian_id = db.Column(db.Integer, db.ForeignKey('kejadian.id'))
    filename = db.Column(db.String(255))
    cdate = db.Column(db.DateTime, default=datetime.now)
    mdate = db.Column(db.DateTime)
    cuser = db.Column(db.String(15))
    muser = db.Column(db.String(15))

    def get_url(self):
        return f"uploaded_photos/{self.filename}"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15))
    password = db.Column(db.String(255))
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"

    __tablename__ = 'users'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Pos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pos_name = db.Column(db.String(100))
    geom = db.Column(db.String(10000))
    sumberhidrologi = db.relationship('SumberHidrologi', backref='pos', lazy='dynamic')

    @property
    def get_point(self):
        ''' Get geometry/multi polygon data as geojson '''
        result = db.engine.execute(f"SELECT ST_AsGeoJSON(geom) FROM Pos WHERE id={self.id};")
        rows = [row[0] for row in result]
        return json.loads(rows[0])


class Desa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gid = db.Column(db.Integer, index=True, unique=True)
    desa = db.Column(db.String(35))
    kecamatan = db.Column(db.String(35))
    kabupaten = db.Column(db.String(35))
    propinsi = db.Column(db.String(35))
    geom = db.Column(db.String(10000))
    dampakdesa = db.relationship('DampakDesa', backref='desa', lazy='dynamic')

    def _get_geometry(self):
        ''' Get geometry/multi polygon data as geojson '''
        result = db.engine.execute(f"SELECT ST_AsGeoJSON(geom) FROM Desa WHERE id={self.id};")
        rows = [row[0] for row in result]
        return json.loads(rows[0])

    @property
    def get_point(self):
        ''' Get area/desa center point '''
        result = db.engine.execute(
            f"SELECT ST_AsGeoJSON(ST_MakePoint(ST_Xmin(geom), ST_Ymin(geom))) FROM Desa WHERE id={self.id};")
        rows = [row[0] for row in result]
        return json.loads(rows[0])

    @property
    def get_area(self):
        ''' Get area of surface of the geojson '''
        result = db.engine.execute(f"SELECT ST_Area(geom) FROM Desa WHERE id={self.id};")
        rows = [row[0] for row in result]

        # convert into km^2, 110.5km is how far 1 degree of latitude, 110.3 is longitude (estimation)
        final = rows[0] * (110.5*110.3)
        return final

    @property
    def nama_daerah(self):
        ''' Get full name of the village '''
        return f"Desa {self.desa}, Kec. {self.kecamatan}, Kab. {self.kabupaten}, {self.propinsi}"
