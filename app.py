from __future__ import annotations
from pathlib import Path
import json
from typing import Any
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / 'static' / 'uploads'
CONTENT_FILE = BASE_DIR / 'content.json'

ADMIN_ID = '9810444571'
ADMIN_PASSWORD = 'Viplov@123'
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.pdf'}

app = Flask(__name__)
app.secret_key = 'replace-this-before-public-deploy'
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024


def load_content() -> dict[str, Any]:
    return json.loads(CONTENT_FILE.read_text(encoding='utf-8'))


def save_content(data: dict[str, Any]) -> None:
    CONTENT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def allowed(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def save_upload(file_storage, prefix: str = '') -> str | None:
    if not file_storage or not file_storage.filename:
        return None
    filename = secure_filename(file_storage.filename)
    if not filename or not allowed(filename):
        return None
    if prefix:
        filename = f"{prefix}_{filename}"
    target = UPLOAD_DIR / filename
    file_storage.save(target)
    return filename


def is_logged_in() -> bool:
    return session.get('admin_logged_in') is True


@app.context_processor
def inject_helpers():
    def asset_url(filename: str | None) -> str:
        if not filename:
            return ''
        return url_for('uploaded_file', filename=filename)
    return {'asset_url': asset_url}


@app.route('/uploads/<path:filename>')
def uploaded_file(filename: str):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route('/')
def index():
    content = load_content()
    return render_template('index.html', content=content)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not is_logged_in():
        return redirect(url_for('login'))

    content = load_content()
    if request.method == 'POST':
        # site fields
        site = content['site']
        site['name'] = request.form.get('site_name', site['name']).strip()
        site['title'] = request.form.get('site_title', site['title']).strip()
        site['hero_headline_html'] = request.form.get('hero_headline_html', site['hero_headline_html']).strip()
        site['hero_copy'] = request.form.get('hero_copy', site['hero_copy']).strip()
        site['location'] = request.form.get('location', site['location']).strip()
        site['phone'] = request.form.get('phone', site['phone']).strip()
        site['linkedin'] = request.form.get('linkedin', site['linkedin']).strip()

        # learning list
        learning_raw = request.form.get('learning_raw', '')
        content['learning'] = [line.strip() for line in learning_raw.splitlines() if line.strip()]

        # stats
        for i, stat in enumerate(content.get('stats', [])):
            stat['value'] = request.form.get(f'stat_value_{i}', stat['value']).strip()
            stat['label'] = request.form.get(f'stat_label_{i}', stat['label']).strip()

        # general uploads
        profile_image = save_upload(request.files.get('profile_image'), 'profile')
        if profile_image:
            site['profile_image'] = profile_image
        resume_pdf = save_upload(request.files.get('resume_pdf'), 'resume')
        if resume_pdf:
            site['resume_pdf'] = resume_pdf
        resume_preview = save_upload(request.files.get('resume_preview'), 'resume_preview')
        if resume_preview:
            site['resume_preview'] = resume_preview

        # projects
        for idx, project in enumerate(content.get('projects', [])):
            project['type'] = request.form.get(f'project_type_{idx}', project['type']).strip()
            project['title'] = request.form.get(f'project_title_{idx}', project['title']).strip()
            project['summary'] = request.form.get(f'project_summary_{idx}', project['summary']).strip()
            project['highlight'] = request.form.get(f'project_highlight_{idx}', project['highlight']).strip()
            tags = request.form.get(f'project_tags_{idx}', ', '.join(project['tags']))
            project['tags'] = [t.strip() for t in tags.split(',') if t.strip()]

            for img_idx in range(2):
                uploaded = save_upload(request.files.get(f'project_{idx}_image_{img_idx}'), f"project{idx}_img{img_idx}")
                if uploaded:
                    if len(project['images']) <= img_idx:
                        project['images'].append(uploaded)
                    else:
                        project['images'][img_idx] = uploaded

            for link_idx, link in enumerate(project.get('links', [])):
                link['label'] = request.form.get(f'project_{idx}_link_label_{link_idx}', link['label']).strip()
                uploaded = save_upload(request.files.get(f'project_{idx}_link_file_{link_idx}'), f"project{idx}_link{link_idx}")
                if uploaded:
                    link['file'] = uploaded

        save_content(content)
        flash('Portfolio content updated successfully.')
        return redirect(url_for('admin'))

    return render_template('admin.html', content=content)


@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('admin'))
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '')
        if user_id == ADMIN_ID and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        flash('Invalid ID or password.')
    return render_template('login.html')


@app.route('/admin/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
