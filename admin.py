"""TurfPro 管理后台 — 蓝图"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from models import db, User, Post, NewsArticle, TurfProblem, Reply
from werkzeug.utils import secure_filename
import os, json

admin = Blueprint('admin', __name__, url_prefix='/admin')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash('无权访问管理后台', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

# ============ 站点设置 ============
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site_settings.json')

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {
        'site_name': 'TurfPro',
        'hero_title': '专业草坪养护平台',
        'hero_subtitle': '为中国草坪管理者打造的专业平台',
        'hero_image': 'https://images.unsplash.com/photo-1459865264687-595d652de67e?w=1600',
        'logo_text': 'TurfPro',
    }

def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@admin.route('/')
@admin_required
def dashboard():
    stats = {
        'users': User.query.count(), 'posts': Post.query.count(),
        'articles': Post.query.filter_by(is_article=True).count(),
        'news': NewsArticle.query.count(), 'problems': TurfProblem.query.count(),
        'replies': Reply.query.count(),
    }
    latest_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, latest_users=latest_users)

@admin.route('/settings', methods=['GET','POST'])
@admin_required
def site_settings():
    settings = load_settings()
    if request.method == 'POST':
        settings['site_name'] = request.form.get('site_name', 'TurfPro')
        settings['hero_title'] = request.form.get('hero_title', '')
        settings['hero_subtitle'] = request.form.get('hero_subtitle', '')
        settings['hero_image'] = request.form.get('hero_image', '')
        settings['logo_text'] = request.form.get('logo_text', 'TurfPro')
        # Upload logo
        if 'logo_file' in request.files and request.files['logo_file'].filename:
            f = request.files['logo_file']
            filename = secure_filename('logo_' + f.filename)
            f.save(os.path.join(UPLOAD_FOLDER, filename))
            settings['logo_file'] = '/static/uploads/' + filename
        save_settings(settings)
        flash('站点设置已保存', 'success')
        return redirect(url_for('admin.site_settings'))
    return render_template('admin/settings.html', settings=settings)

# ============ 文章管理 ============
@admin.route('/articles')
@admin_required
def articles():
    items = Post.query.filter_by(is_article=True).order_by(Post.created_at.desc()).all()
    return render_template('admin/articles.html', items=items)

@admin.route('/articles/edit', methods=['GET','POST'])
@admin.route('/articles/edit/<int:id>', methods=['GET','POST'])
@admin_required
def edit_article(id=None):
    item = Post.query.get(id) if id else None
    from models import Category
    categories = Category.query.filter_by(display_order=1).all()  # 草坪产品/技术论坛...
    # Get all categories for dropdown
    all_cats = Category.query.order_by(Category.display_order).all()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        cat_id = request.form.get('category_id', type=int)
        if not title or not content:
            flash('标题和内容不能为空', 'error')
        else:
            if item:
                item.title = title; item.content = content
                if cat_id: item.category_id = cat_id
                item.updated_at = datetime.utcnow()
            else:
                item = Post(title=title, content=content, category_id=cat_id or (all_cats[0].id if all_cats else 1),
                           user_id=current_user.id, is_article=True)
                db.session.add(item)
            db.session.commit()
            flash('文章已保存', 'success')
            return redirect(url_for('admin.articles'))
    return render_template('admin/edit_article.html', item=item, categories=all_cats)

@admin.route('/articles/delete/<int:id>')
@admin_required
def delete_article(id):
    item = Post.query.get_or_404(id)
    db.session.delete(item); db.session.commit()
    flash('已删除', 'success'); return redirect(url_for('admin.articles'))

@admin.route('/articles/toggle-pin/<int:id>')
@admin_required
def toggle_pin(id):
    item = Post.query.get_or_404(id)
    item.is_pinned = not item.is_pinned; db.session.commit()
    return redirect(url_for('admin.articles'))

# ============ 资讯管理 ============
@admin.route('/news')
@admin_required
def news_list():
    items = NewsArticle.query.order_by(NewsArticle.published_at.desc()).all()
    return render_template('admin/news_list.html', items=items)

@admin.route('/news/edit', methods=['GET','POST'])
@admin.route('/news/edit/<int:id>', methods=['GET','POST'])
@admin_required
def edit_news(id=None):
    item = NewsArticle.query.get(id) if id else None
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        author = request.form.get('author', '编辑部')
        source = request.form.get('source', 'TurfPro')
        image_url = request.form.get('image_url', '')
        if not title or not content:
            flash('标题和内容不能为空', 'error')
        else:
            if item:
                item.title = title; item.content = content
                item.author = author; item.source = source
                if image_url: item.image_url = image_url
            else:
                slug = title.lower()[:60].replace(' ','-').replace(':','')
                item = NewsArticle(title=title, content=content, slug=slug,
                                 author=author, source=source, image_url=image_url or '')
                db.session.add(item)
            db.session.commit()
            flash('资讯已保存', 'success')
            return redirect(url_for('admin.news_list'))
    return render_template('admin/edit_news.html', item=item)

@admin.route('/news/delete/<int:id>')
@admin_required
def delete_news(id):
    item = NewsArticle.query.get_or_404(id)
    db.session.delete(item); db.session.commit()
    flash('已删除', 'success'); return redirect(url_for('admin.news_list'))

# ============ 诊断库管理 ============
@admin.route('/diagnose')
@admin_required
def diagnose_list():
    items = TurfProblem.query.order_by(TurfProblem.ptype, TurfProblem.id).all()
    return render_template('admin/diagnose_list.html', items=items)

@admin.route('/diagnose/edit', methods=['GET','POST'])
@admin.route('/diagnose/edit/<int:id>', methods=['GET','POST'])
@admin_required
def edit_diagnose(id=None):
    item = TurfProblem.query.get(id) if id else None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('名称不能为空', 'error')
        else:
            if item:
                item.name = name; item.ptype = request.form.get('ptype', 'disease')
                item.latin_name = request.form.get('latin_name', '')
                item.summary = request.form.get('summary', '')
                item.symptoms = request.form.get('symptoms', '')
                item.conditions = request.form.get('conditions', '')
                item.season = request.form.get('season', '')
                item.severity = request.form.get('severity', '中')
                item.solution = request.form.get('solution', '')
                item.prevention = request.form.get('prevention', '')
                item.image_url = request.form.get('image_url', '')
            else:
                slug = name.lower().replace(' ','-').replace('(','').replace(')','')[:80]
                item = TurfProblem(name=name, ptype=request.form.get('ptype','disease'),
                    slug=slug, latin_name=request.form.get('latin_name',''),
                    summary=request.form.get('summary',''), symptoms=request.form.get('symptoms',''),
                    conditions=request.form.get('conditions',''), season=request.form.get('season',''),
                    severity=request.form.get('severity','中'), solution=request.form.get('solution',''),
                    prevention=request.form.get('prevention',''), image_url=request.form.get('image_url',''))
                db.session.add(item)
            db.session.commit()
            flash('条目已保存', 'success')
            return redirect(url_for('admin.diagnose_list'))
    return render_template('admin/edit_diagnose.html', item=item)

@admin.route('/diagnose/delete/<int:id>')
@admin_required
def delete_diagnose(id):
    item = TurfProblem.query.get_or_404(id)
    db.session.delete(item); db.session.commit()
    flash('已删除', 'success'); return redirect(url_for('admin.diagnose_list'))

# ============ 论坛管理 ============
@admin.route('/forum')
@admin_required
def forum_list():
    items = Post.query.filter_by(is_article=False).order_by(Post.created_at.desc()).all()
    return render_template('admin/forum_list.html', items=items)

@admin.route('/forum/delete/<int:id>')
@admin_required
def delete_forum_post(id):
    item = Post.query.get_or_404(id)
    db.session.delete(item); db.session.commit()
    flash('已删除', 'success'); return redirect(url_for('admin.forum_list'))

# ============ 用户管理 ============
@admin.route('/users')
@admin_required
def users():
    items = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', items=items)

@admin.route('/users/toggle-admin/<int:id>')
@admin_required
def toggle_admin(id):
    if id == current_user.id:
        flash('不能取消自己的管理员', 'error')
        return redirect(url_for('admin.users'))
    user = User.query.get_or_404(id)
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f'{user.username} 管理员状态已切换', 'success')
    return redirect(url_for('admin.users'))

# ============ 图片上传 API ============
ALLOWED_EXT = {'png','jpg','jpeg','gif','webp','svg'}

@admin.route('/api/upload', methods=['POST'])
@admin_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'})
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': '未选择文件'})
    ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
    if ext not in ALLOWED_EXT:
        return jsonify({'error': '不支持的文件格式'})
    filename = secure_filename(f'{datetime.now().strftime("%Y%m%d%H%M%S")}_{f.filename}')
    f.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({'url': '/static/uploads/' + filename, 'ok': True})
