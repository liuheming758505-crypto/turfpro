from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import (db, User, Category, Post, Reply, NewsArticle, TurfProblem)
from datetime import datetime

main = Blueprint('main', __name__)

# ==================== INDEX ====================
@main.route('/')
def index():
    articles = Post.query.filter_by(is_article=True).order_by(Post.created_at.desc()).limit(3).all()
    news_items = NewsArticle.query.filter_by(is_published=True).order_by(NewsArticle.published_at.desc()).limit(3).all()
    categories = Category.query.order_by(Category.display_order).all()
    # 首页社区活力模块：最新讨论帖（非文章）
    hot_posts = Post.query.filter_by(is_article=False).order_by(Post.created_at.desc()).limit(5).all()
    post_count = Post.query.filter_by(is_article=False).count()
    diagnose_count = TurfProblem.query.count()
    return render_template('index.html', articles=articles, news=news_items, categories=categories,
                          hot_posts=hot_posts, post_count=post_count, diagnose_count=diagnose_count)

# ==================== FORUM ====================
@main.route('/forum')
def forum():
    cat_slug = request.args.get('category'); sort = request.args.get('sort','latest')
    q = (request.args.get('q') or '').strip()
    if cat_slug:
        cat = Category.query.filter_by(slug=cat_slug).first_or_404()
        posts = Post.query.filter_by(category_id=cat.id)
    else: cat = None; posts = Post.query
    if q:
        posts = posts.filter(Post.title.contains(q) | Post.content.contains(q))
    # 置顶帖始终排最前
    if sort == 'popular': posts = posts.order_by(Post.is_pinned.desc(), Post.views.desc())
    else: posts = posts.order_by(Post.is_pinned.desc(), Post.created_at.desc())
    return render_template('forum.html', posts=posts.all(), categories=Category.query.order_by(Category.display_order).all(),
                          current_cat=cat, sort=sort, q=q)

@main.route('/post/<int:id>')
def post_detail(id):
    post = Post.query.get_or_404(id); post.views += 1; db.session.commit()
    return render_template('post.html', post=post, replies=Reply.query.filter_by(post_id=id).order_by(Reply.created_at).all())

@main.route('/post/new', methods=['GET','POST'])
@login_required
def new_post():
    if request.method=='POST':
        title=request.form.get('title'); content=request.form.get('content'); cid=request.form.get('category_id')
        if not title or not content: flash('标题和内容不能为空','error'); return redirect(url_for('main.new_post'))
        post=Post(title=title,content=content,category_id=cid,user_id=current_user.id)
        db.session.add(post); db.session.commit(); flash('发帖成功！','success')
        return redirect(url_for('main.post_detail',id=post.id))
    return render_template('new_post.html',categories=Category.query.order_by(Category.display_order).all())

@main.route('/post/<int:id>/reply', methods=['POST'])
@login_required
def reply_post(id):
    content=request.form.get('content')
    if content: db.session.add(Reply(content=content,post_id=id,user_id=current_user.id)); db.session.commit(); flash('回复成功','success')
    return redirect(url_for('main.post_detail',id=id))

# ==================== NEWS ====================
@main.route('/news')
def news():
    items = NewsArticle.query.filter_by(is_published=True).order_by(NewsArticle.published_at.desc()).all()
    return render_template('news.html', news=items)

@main.route('/news/<slug>')
def news_detail(slug):
    return render_template('news_article.html', article=NewsArticle.query.filter_by(slug=slug).first_or_404())

# ==================== MAGAZINE ====================
@main.route('/magazine')
def magazine():
    articles = Post.query.filter_by(is_article=True).order_by(Post.created_at.desc()).all()
    return render_template('magazine.html', articles=articles)

# ==================== TOOLS ====================
@main.route('/tools')
def tools():
    return render_template('tools.html')

@main.route('/weather')
def weather_tool():
    return render_template('weather_tool.html')

@main.route('/tools/iguide')
def iguide():
    return render_template('iguide.html')

@main.route('/api/seed-calculator', methods=['POST'])
def seed_calculator():
    area=request.json.get('area',0,type=float); grass=request.json.get('grass_type','百慕大')
    if area<=0: return jsonify({'error':'请输入面积'})
    rates={'百慕大':25,'黑麦草':30,'本特草':15,'结缕草':35,'高羊茅':40}
    seed=round(area/rates.get(grass,25),1)
    return jsonify({'seed_kg':seed,'recommendation':f'推荐购买{seed}kg，建议多备10%用量'})

@main.route('/api/fertilizer-calculator', methods=['POST'])
def fertilizer_calculator():
    area=request.json.get('area',0,type=float); n=request.json.get('n_need',20,type=float); npk=request.json.get('npk','20-5-10')
    if area<=0: return jsonify({'error':'请输入面积'})
    fert=round(area*n/1000/(int(npk.split('-')[0])/100)*1.1,1)
    return jsonify({'fertilizer_kg':fert,'total_n_kg':round(area*n/1000,1)})

# ==================== AUTH ====================
@main.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        user=User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user); flash('登录成功','success')
            next_url = request.args.get('next') or url_for('main.index')
            return redirect(next_url)
        flash('用户名或密码错误','error')
    return render_template('login.html', next=request.args.get('next',''))

@main.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        u=request.form.get('username'); e=request.form.get('email'); p=request.form.get('password')
        if User.query.filter_by(username=u).first(): flash('用户名已存在','error')
        elif User.query.filter_by(email=e).first(): flash('邮箱已注册','error')
        else: user=User(username=u,email=e); user.set_password(p); db.session.add(user); db.session.commit(); login_user(user); flash('注册成功！','success'); return redirect(url_for('main.index'))
    return render_template('register.html')

@main.route('/logout')
@login_required
def logout(): logout_user(); flash('已退出','success'); return redirect(url_for('main.index'))

# ==================== STATIC PAGES ====================
@main.route('/about')
def about(): return render_template('about.html')

@main.route('/contact', methods=['GET','POST'])
def contact():
    if request.method=='POST': flash('感谢留言，我们会尽快回复！','success')
    return render_template('contact.html')

@main.route('/jobs')
def jobs(): return render_template('jobs.html')

@main.route('/advertise')
def advertise(): return render_template('advertise.html')

@main.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method=='POST':
        action = request.form.get('action','info')
        if action == 'info':
            current_user.phone = request.form.get('phone','')
            current_user.company = request.form.get('company','')
            db.session.commit(); flash('信息已更新','success')
        elif action == 'username':
            new_username = request.form.get('username','').strip()
            if not new_username: flash('用户名不能为空','error')
            elif User.query.filter(User.username==new_username, User.id!=current_user.id).first():
                flash('用户名已被占用','error')
            else:
                old_name = current_user.username
                current_user.username = new_username
                db.session.commit(); flash(f'用户名已从 {old_name} 改为 {new_username}','success')
        elif action == 'password':
            old_pw = request.form.get('current_password','')
            new_pw = request.form.get('new_password','')
            if not current_user.check_password(old_pw):
                flash('当前密码错误','error')
            elif len(new_pw) < 4:
                flash('新密码至少4位','error')
            else:
                current_user.set_password(new_pw)
                db.session.commit(); flash('密码已修改','success')
    return render_template('profile.html')

# ==================== 病虫草害诊断库 ====================
@main.route('/diagnose')
def diagnose():
    ptype = request.args.get('type'); q = request.args.get('q')
    query = TurfProblem.query
    if ptype in ('disease','pest','weed'): query = query.filter_by(ptype=ptype)
    if q: query = query.filter(TurfProblem.name.contains(q) | TurfProblem.symptoms.contains(q))
    problems = query.order_by(TurfProblem.ptype, TurfProblem.id).all()
    counts = {'all': TurfProblem.query.count(), 'disease': TurfProblem.query.filter_by(ptype='disease').count(),
              'pest': TurfProblem.query.filter_by(ptype='pest').count(), 'weed': TurfProblem.query.filter_by(ptype='weed').count()}
    return render_template('diagnose.html', problems=problems, counts=counts, current_type=ptype, q=q)

@main.route('/diagnose/<slug>')
def problem_detail(slug):
    problem = TurfProblem.query.filter_by(slug=slug).first_or_404()
    related = TurfProblem.query.filter(TurfProblem.ptype==problem.ptype, TurfProblem.id!=problem.id).limit(3).all()
    return render_template('problem.html', problem=problem, recommended=[], related=related)

@main.context_processor
def inject_globals():
    from admin import load_settings
    settings = load_settings()
    return dict(
        categories=Category.query.order_by(Category.display_order).all(),
        current_year=datetime.now().year,
        site_settings=settings,
        nav_items=[n for n in settings.get('nav_items',[]) if n.get('visible')],
        page_heroes=settings.get('page_heroes',{}),
    )
