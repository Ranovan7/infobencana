from flask import Blueprint, jsonify, request
from apps.models import Desa, Kejadian, Pos
from sqlalchemy import or_


bp = Blueprint('api', __name__)


@bp.route('/desa')
def index():
    # q = request.args.get('q', None)
    # if q:
    #     rst =
    #     return jsonify(rst)
    picked_desa = Desa.query.all()
    result = []
    for desa in picked_desa:
        result.append(
            {
                "type": "Feature",
                "properties": {
                    "name": desa.nama_daerah,
                },
                "geometry": desa.get_point
            }
        )
    return jsonify(result)


@bp.route('/desa/')
def data_desa():
    key = request.args.get('key', None)
    # geom = request.args.get('geom', None)
    desa = Desa.query.filter(or_(
                            Desa.desa.ilike(f"%{key}%"),
                            Desa.kecamatan.ilike(f"%{key}%"),
                            Desa.kabupaten.ilike(f"%{key}%")
                        )).all()
    result = {
        "type": "Features",
        "data": []
    }
    for d in desa:
        result['data'].append({
            "id": d.id,
            "properties": {
                "desa": d.desa,
                "kecamatan": d.kecamatan,
                "kabupaten": d.kabupaten,
                "provinsi": d.propinsi,
            },
        })
    return jsonify(result)


@bp.route('/desa/<int:id>')
def show_desa(id):
    type = request.args.get('type', "multipolygon")
    desa = Desa.query.filter_by(id=id).first()
    if type == "point":
        geom = desa.get_point
    else:
        geom = desa._get_geometry()

    result = {
        "type": "Feature",
        "properties": {
            "desa": desa.desa,
            "kecamatan": desa.kecamatan,
            "kabupaten": desa.kabupaten,
            "provinsi": desa.propinsi,
        },
        "geometry": geom
    }
    return jsonify(result)


@bp.route('/kejadian/<int:id>/get_point')
def get_point(id):
    kejadian = Kejadian.query.filter_by(id=id).first()

    # due to strange interaction between foreignkey backref and binary check, got to use forloop
    daerah = "Belum Ada Daerah"
    for desa in kejadian.dampakdesa:
        daerah = desa.desa.kabupaten
        break

    result = {
        "type": "Feature",
        "properties": {
            "description": f"{kejadian.jenis} di daerah Kab. {daerah}",
        },
        "geometry": kejadian.get_random_point
    }
    return jsonify(result)


@bp.route('/kejadian/<int:id>/get_hidrologi')
def get_hidrologi(id):
    kejadian = Kejadian.query.filter_by(id=id).first()
    result = []
    for hidro in kejadian.hidrologi:
        temp = {
            "type": "Feature",
            "properties": {
                "description": hidro.pos.pos_name,
            },
            "geometry": hidro.pos.get_point
        }
        result.append(temp)
    return jsonify(result)


@bp.route('/kejadian/<int:id>/dampakdesa')
def getall_dampakdesa(id):
    kejadian = Kejadian.query.filter_by(id=id).first()
    result = []
    for dampakdesa in kejadian.dampakdesa:
        result.append(
            {
                "type": "Feature",
                "properties": {
                    "desa": dampakdesa.desa.desa,
                    "kecamatan": dampakdesa.desa.kecamatan,
                    "kabupaten": dampakdesa.desa.kabupaten,
                    "provinsi": dampakdesa.desa.propinsi,
                    "pengungsi": dampakdesa.pengungsi,
                    "luka": dampakdesa.luka,
                    "md": dampakdesa.md,
                    "hilang": dampakdesa.hilang,
                    "rumah": dampakdesa.rumah,
                    "sekolah": dampakdesa.sekolah,
                    "t_ibadah": dampakdesa.t_ibadah,
                },
                "geometry": dampakdesa.desa._get_geometry()
            }
        )
    return jsonify(result)


@bp.route('/pos/<int:id>')
def show_pos(id):
    pos = Pos.query.filter_by(id=id).first()

    result = {
        "type": "Feature",
        "properties": {
            "name": pos.pos_name,
        },
        "geometry": pos.get_point
    }
    return jsonify(result)
