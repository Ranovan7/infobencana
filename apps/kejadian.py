from flask import Blueprint, render_template, request, redirect, url_for, abort, jsonify, flash
from flask_login import login_required, current_user
from apps import app, db
from apps.models import Kejadian, DampakDesa, SumberHidrologi, Foto, User
from apps.forms import KejadianForm, DampakDesaForm, SumberHidrologiForm, FotoForm, UserForm
from sqlalchemy import desc
from datetime import datetime
from random import randrange
import base64
import os

bp = Blueprint('admin', __name__)


@bp.route('/')
@login_required
def index():
    '''Menampilkan dashboard admin'''
    return redirect(url_for('admin.kejadian'))


@bp.route('/user', methods=['GET', 'POST'])
@login_required
def users():
    '''Menampilkan dashboard users'''
    all_users = User.query.all()
    form = UserForm()
    if form.validate_on_submit():
        username = request.values.get('username')
        password = request.values.get('password')
        password2 = request.values.get('password2')

        # check if password2 is the same as password
        if password != password2:
            flash('Verifikasi Password gagal !', 'danger')
            return render_template('kejadian/users.html', all_users=all_users, form=form, user=current_user)

        # save new user data
        user = User.query.filter_by(username=username).first()
        # hash password as md5
        user.set_password(password)
        db.session.commit()

        flash('Ubah Password berhasil !', 'success')
        return redirect(url_for('admin.users'))
    return render_template('kejadian/users.html', all_users=all_users, form=form, user=current_user)


@bp.route('/user/tambah', methods=['GET', 'POST'])
@login_required
def tambah_user():
    '''Menambah user'''
    form = UserForm()
    if form.validate_on_submit():
        username = request.values.get('username')
        password = request.values.get('password')
        password2 = request.values.get('password2')

        # check if username is available
        if User.query.filter_by(username=username).first():
            flash('Username tidak tersedia !', 'danger')
            return render_template('kejadian/tambah_user.html', form=form, user=current_user)

        # check if password2 is the same as password
        if password != password2:
            flash('Verifikasi Password gagal !', 'danger')
            return render_template('kejadian/tambah_user.html', form=form, user=current_user)

        # save new user data
        new_user = User(
            username=username
        )
        # hash password as md5
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.flush()
        db.session.commit()

        flash('Tambah User berhasil !', 'success')
        return redirect(url_for('admin.users'))

    return render_template('kejadian/tambah_user.html', form=form, user=current_user)


@bp.route('/bencana/', strict_slashes=False)
@login_required
def kejadian():
    '''Menampilkan daftar kejadian'''
    if not current_user.is_authenticated:
        print("You are currently logged out!")
    all_kejadian = Kejadian.query.order_by(desc(Kejadian.waktu)).all()
    return render_template('kejadian/kejadian.html', all_kejadian=all_kejadian, user=current_user)


@bp.route("/bencana/add", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def tambah_kejadian():
    '''Form Menambah Index'''
    form = KejadianForm()
    if form.validate_on_submit():
        waktu_raw = request.values.get('waktu').split('-')
        waktu = f"{waktu_raw[2]}-{waktu_raw[1]}-{waktu_raw[0]}"
        jenis = request.values.get('jenis')
        sebab = request.values.get('sebab')
        sungai = request.values.get('sungai')
        sawah = request.values.get('sawah')
        bangunan = request.values.get('bangunan')
        jalan = request.values.get('jalan')
        jalan_putus = request.values.get('jalan_putus')
        jembatan = request.values.get('jembatan')
        lama = request.values.get('lama')
        tindakan = request.values.get('tindakan')

        new_kejadian = Kejadian(
            waktu=waktu,
            jenis=jenis,
            sebab=sebab,
            sungai=sungai,
            sawah=sawah,
            bangunan=bangunan,
            jalan=jalan,
            jalan_putus=jalan_putus,
            jembatan=jembatan,
            lama=lama,
            tindakan=tindakan,
        )

        print(waktu)

        db.session.add(new_kejadian)
        db.session.flush()
        newest_id = new_kejadian.id
        db.session.commit()
        return redirect(url_for('admin.lihat_kejadian', kejadian_id=newest_id))

    # checking value
    # print(request.values.get('waktu'))

    return render_template('kejadian/tambah_kejadian.html', form=form, user=current_user)


@bp.route("/bencana/<kejadian_id>", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def lihat_kejadian(kejadian_id):
    ''' Lihat Satu Kejadian '''
    kejadian = Kejadian.query.filter_by(id=kejadian_id).first()
    dampakdesa = DampakDesa.query.filter_by(kejadian_id=kejadian_id)

    # return 404 if kejadian is none
    if not kejadian:
        return abort(404)

    # dealing with multifile (photos) upload
    form = FotoForm()

    context = {}
    context["kejadian"] = kejadian
    context["dampakdesa"] = dampakdesa
    context["form"] = form
    context["foto_urls"] = Foto.query.filter_by(kejadian_id=kejadian_id)
    return render_template('kejadian/lihat_kejadian.html', context=context, user=current_user)


@bp.route('/upload/<kejadian_id>', methods=['POST'])
def upload(kejadian_id):
    print(f" Image Acquired for Kejadian {kejadian_id} ! ")
    raw = request.data
    imageStr = base64.b64encode(raw).decode('ascii')
    kejadian = Kejadian.query.filter_by(id=kejadian_id).first()
    count = kejadian.foto.count()
    randnum = randrange(1000)
    # print(imageStr[:30])
    file_name = f"kejadian-{kejadian.id}-foto-{count + 1}-{randnum}.jpeg"
    # print(file_name)
    img_file = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

    # convert base64 into image file and then save it
    imgdata = base64.b64decode(imageStr)
    # print(imgdata)
    with open(img_file, 'wb') as f:
        f.write(imgdata)

    print("saving image !")

    # save image record in database
    new_image = Foto(kejadian_id=kejadian_id, filename=file_name)
    db.session.add(new_image)
    db.session.flush()
    db.session.commit()

    result = {
        'status': "SUCCESS!"
    }
    return jsonify(result)


@bp.route('/bencana/<kejadian_id>/print')
@login_required
def laporan(kejadian_id):
    '''Menampilkan data kejadian dalam bentuk paper'''
    kejadian = Kejadian.query.filter_by(id=kejadian_id).first()

    return render_template('kejadian/paper.html', kejadian=kejadian)


@bp.route("/bencana/<kejadian_id>/desa/add", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def tambah_dampakdesa(kejadian_id):
    ''' Tambah Desa yang Terdampak '''
    kejadian = Kejadian.query.filter_by(id=kejadian_id).first()
    form = DampakDesaForm()
    if form.validate_on_submit():
        desa = request.values.get('desa')
        str_wilayah = request.values.get('str_wilayah')
        rumah = request.values.get('rumah')
        sekolah = request.values.get('sekolah')
        t_ibadah = request.values.get('t_ibadah')
        md = request.values.get('md')
        luka = request.values.get('luka')
        hilang = request.values.get('hilang')
        pengungsi = request.values.get('pengungsi')

        new_dampakdesa = DampakDesa(
            kejadian_id=kejadian_id,
            desa_id=desa,
            str_wilayah=str_wilayah,
            rumah=rumah,
            sekolah=sekolah,
            t_ibadah=t_ibadah,
            md=md,
            luka=luka,
            hilang=hilang,
            pengungsi=pengungsi
        )
        db.session.add(new_dampakdesa)
        db.session.flush()
        db.session.commit()
        return redirect(url_for('admin.lihat_kejadian', kejadian_id=kejadian_id))

    return render_template('kejadian/tambah_dampakdesa.html', kejadian=kejadian, form=form, user=current_user)


@bp.route("/bencana/<kejadian_id>/hidrologi/add", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def tambah_sumberhidrologi(kejadian_id):
    ''' Tambah Sumber Hidrologi '''
    kejadian = Kejadian.query.filter_by(id=kejadian_id).first()
    form = SumberHidrologiForm()
    if form.validate_on_submit():
        pos = request.values.get('pos')
        ch = request.values.get('ch')
        durasi = request.values.get('durasi')

        new_sumberhidrologi = SumberHidrologi(
            kejadian_id=kejadian_id,
            pos_id=pos,
            ch=ch,
            durasi=durasi
        )
        db.session.add(new_sumberhidrologi)
        db.session.flush()
        db.session.commit()
        return redirect(url_for('admin.lihat_kejadian', kejadian_id=kejadian_id))

    return render_template('kejadian/tambah_sumberhidrologi.html', kejadian=kejadian, form=form, user=current_user)


@bp.route("/bencana/<kejadian_id>/update", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def update_kejadian(kejadian_id):
    ''' Update Kejadian'''
    kejadian = Kejadian.query.filter_by(id=kejadian_id).first()
    form = KejadianForm(
        waktu=kejadian.waktu,
        jenis=kejadian.jenis,
        sebab=kejadian.sebab,
        sungai=kejadian.sungai,
        sawah=kejadian.sawah,
        bangunan=kejadian.bangunan,
        jalan=kejadian.jalan,
        jalan_putus=kejadian.jalan_putus,
        jembatan=kejadian.jembatan,
        lama=kejadian.lama,
        tindakan=kejadian.tindakan,
    )
    print("Updating Kejadian")
    if form.validate_on_submit():
        waktu_raw = request.values.get('waktu').split('-')
        kejadian.waktu = f"{waktu_raw[2]}-{waktu_raw[1]}-{waktu_raw[0]}"
        kejadian.jenis = request.values.get('jenis')
        kejadian.sebab = request.values.get('sebab')
        kejadian.sungai = request.values.get('sungai')
        kejadian.sawah = request.values.get('sawah')
        kejadian.bangunan = request.values.get('bangunan')
        kejadian.jalan = request.values.get('jalan')
        kejadian.jalan_putus = request.values.get('jalan_putus')
        kejadian.jembatan = request.values.get('jembatan')
        kejadian.lama = request.values.get('lama')
        kejadian.tindakan = request.values.get('tindakan')

        # save/commit the changes
        print("Commiting Uptdates")
        db.session.commit()
        return redirect(url_for('admin.lihat_kejadian', kejadian_id=kejadian_id))

    return render_template('kejadian/update_kejadian.html', kejadian=kejadian, form=form, user=current_user)


@bp.route("/bencana/desa/<dampakdesa_id>", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def update_dampakdesa(dampakdesa_id):
    ''' Update '''
    dampakdesa = DampakDesa.query.filter_by(id=dampakdesa_id).first()
    form = DampakDesaForm(
        desa=dampakdesa.desa_id,
        str_wilayah=dampakdesa.str_wilayah,
        rumah=dampakdesa.rumah,
        sekolah=dampakdesa.sekolah,
        t_ibadah=dampakdesa.t_ibadah,
        md=dampakdesa.md,
        luka=dampakdesa.luka,
        hilang=dampakdesa.hilang,
        pengungsi=dampakdesa.pengungsi,
    )

    if form.validate_on_submit():
        dampakdesa.desa_id = request.values.get('desa')
        dampakdesa.str_wilayah = request.values.get('str_wilayah')
        dampakdesa.rumah = request.values.get('rumah')
        dampakdesa.sekolah = request.values.get('sekolah')
        dampakdesa.t_ibadah = request.values.get('t_ibadah')
        dampakdesa.md = request.values.get('md')
        dampakdesa.luka = request.values.get('luka')
        dampakdesa.hilang = request.values.get('hilang')
        dampakdesa.pengungsi = request.values.get('pengungsi')

        # save/commit changes
        db.session.commit()

    return render_template('kejadian/update_dampakdesa.html', kejadian_id=dampakdesa.kejadian_id, dampakdesa=dampakdesa, form=form, user=current_user)


@bp.route("/bencana/hidrologi/<hidrologi_id>", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def update_sumberhidrologi(hidrologi_id):
    ''' Update Sumber Hidrologi '''
    sumberhidrologi = SumberHidrologi.query.filter_by(id=hidrologi_id).first()
    form = SumberHidrologiForm(
        pos=sumberhidrologi.pos_id,
        ch=sumberhidrologi.ch,
        durasi=sumberhidrologi.durasi
    )

    if form.validate_on_submit():
        sumberhidrologi.pos_id = request.values.get('pos')
        sumberhidrologi.ch = request.values.get('ch')
        sumberhidrologi.durasi = request.values.get('durasi')

        # save/commit changes
        db.session.commit()

    return render_template(
        'kejadian/update_sumberhidrologi.html',
        kejadian_id=sumberhidrologi.kejadian_id,
        sumberhidrologi=sumberhidrologi,
        form=form,
        user=current_user
    )


@bp.route("/bencana/<kejadian_id>/delete", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def delete_kejadian(kejadian_id):
    ''' Delete Kejadian'''
    kejadian = Kejadian.query.filter_by(id=kejadian_id).first()
    db.session.delete(kejadian)
    db.session.commit()
    return redirect(url_for('admin.kejadian'))


@bp.route("/bencana/desa/<dampakdesa_id>/delete", methods=['GET'], strict_slashes=False)
@login_required
def delete_dampakdesa(dampakdesa_id):
    ''' Delete Dampak Desa '''
    dampakdesa = DampakDesa.query.filter_by(id=dampakdesa_id).first()
    kejadian_id = dampakdesa.kejadian_id
    db.session.delete(dampakdesa)
    db.session.commit()
    return redirect(url_for('admin.lihat_kejadian', kejadian_id=kejadian_id))


@bp.route("/bencana/hidrologi/<hidrologi_id>/delete", methods=['GET'], strict_slashes=False)
@login_required
def delete_sumberhidrologi(hidrologi_id):
    ''' Delete Sumber Hidrologi '''
    sumberhidrologi = SumberHidrologi.query.filter_by(id=hidrologi_id).first()
    kejadian_id = sumberhidrologi.kejadian_id
    db.session.delete(sumberhidrologi)
    db.session.commit()
    return redirect(url_for('admin.lihat_kejadian', kejadian_id=kejadian_id))
