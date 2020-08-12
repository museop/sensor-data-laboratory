import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app,
    send_file
)
from flask_paginate import get_page_parameter

from werkzeug.utils import secure_filename

from .auth import login_required
from .model import db, User, File

bp = Blueprint('storage', __name__)


@bp.route('/', methods=('GET',))
def index():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    files = File.query.order_by(File.date_uploaded.desc()).paginate(per_page=5)

    return render_template('storage/index.html', files=files)


@bp.route('/user/<string:username>')
def user_files(username):
    page = request.args.get(get_page_parameter(), type=int, default=1)
    user = User.query.filter_by(username=username).first_or_404()
    files = File.query.filter_by(uploader=user) \
        .order_by(File.date_uploaded.desc()) \
        .paginate(per_page=5)

    return render_template('storage/user_files.html', files=files, user=user)


@bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    if request.method == 'POST':
        f = request.files['file']
        filetype = request.form['filetype']
        description = request.form['description']

        filename = secure_filename(f.filename)
        error = None

        if File.query.filter_by(filename=f'{filename}').first() is not None:
            error = 'File {} is already uploaded.'.format(filename)

        if error is None:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if filetype == "none":
                file = File(filename=filename, filepath=filepath, description=description)
            else:
                file = File(filename=filename, filepath=filepath, filetype=filetype, description=description)

            f.save(filepath)
            g.user.files.append(file)
            db.session.commit()
            return redirect(url_for('storage.index'))

        flash(error)

    return render_template('storage/upload.html')


@bp.route('/download/<int:file_id>', methods=('GET',))
def download_file(file_id):
    error = None
    file = File.query.filter_by(id=file_id).first()

    if file is None:
        error = 'File id {} is not exists.'.format(file_id)

    if error is None:
        return send_file(file.filepath, attachment_filename=file.filename, as_attachment=True)

    flash(error)
