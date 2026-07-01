"""TurfPro 管理后台 — 蓝图"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from models import db, User, Post, NewsArticle, TurfProblem, Reply
import json

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash('无权访问管理后台', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

@admin.route('/')
@admin_required
def dashboard():
    stats = {
        'users': User.query.count(),
        'posts': Post.query.count(),
        'articles': Post.query.filter_by(is_article=True).count(),
        'news': NewsArticle.query.count(),
        'problems': TurfProblem.query.count(),
        'replies': Reply.query.count(),
    }
    latest_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, latest_users=latest_users)

# ============ 文章管理 ============
@admin.route('/articles')
@admin_required
def articles():
    items = Post.query.filter_by(is_article=True).order_by(Post.created_at.desc()).all()
    return render_template('admin/articles.html', items=items)

@admin.route('/articles/delete/<int:id>')
@admin_required
def delete_article(id):
    item = Post.query.get_or_404(id)
    db.session.delete(item); db.session.commit()
    flash('已删除', 'success')
    return redirect(url_for('admin.articles'))

@admin.route('/articles/toggle-pin/<int:id>')
@admin_required
def toggle_pin(id):
    item = Post.query.get_or_404(id)
    item.is_pinned = not item.is_pinned
    db.session.commit()
    return redirect(url_for('admin.articles'))

# ============ 资讯管理 ============
@admin.route('/news')
@admin_required
def news_list():
    items = NewsArticle.query.order_by(NewsArticle.published_at.desc()).all()
    return render_template('admin/news_list.html', items=items)

@admin.route('/news/delete/<int:id>')
@admin_required
def delete_news(id):
    item = NewsArticle.query.get_or_404(id)
    db.session.delete(item); db.session.commit()
    flash('已删除', 'success')
    return redirect(url_for('admin.news_list'))

# ============ 诊断库管理 ============
@admin.route('/diagnose')
@admin_required
def diagnose_list():
    items = TurfProblem.query.order_by(TurfProblem.ptype, TurfProblem.id).all()
    return render_template('admin/diagnose_list.html', items=items)

@admin.route('/diagnose/delete/<int:id>')
@admin_required
def delete_diagnose(id):
    item = TurfProblem.query.get_or_404(id)
    db.session.delete(item); db.session.commit()
    flash('已删除', 'success')
    return redirect(url_for('admin.diagnose_list'))

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
    flash('已删除', 'success')
    return redirect(url_for('admin.forum_list'))

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
