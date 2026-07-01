"""Full data models for XFieldMate"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    def set_password(self, p): self.password_hash = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password_hash, p)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    display_order = db.Column(db.Integer, default=0)
    subcategories = db.relationship('ProductCategory', backref='main_cat', lazy=True)
    posts = db.relationship('Post', backref='category', lazy=True)

class ProductCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    icon = db.Column(db.String(50), default='📦')
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    products = db.relationship('Product', backref='subcategory', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True)
    sku = db.Column(db.String(100), unique=True)
    short_desc = db.Column(db.String(500))
    description = db.Column(db.Text)
    specs = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)
    unit = db.Column(db.String(50), default='件')
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    image_urls = db.Column(db.Text)  # JSON array
    brand = db.Column(db.String(100))
    is_featured = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('product_category.id'))
    reviews = db.relationship('Review', backref='product', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, default=5)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all,delete-orphan')

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending/paid/shipped/delivered/cancelled
    total = db.Column(db.Float)
    shipping_name = db.Column(db.String(100))
    shipping_phone = db.Column(db.String(20))
    shipping_address = db.Column(db.Text)
    shipping_company = db.Column(db.String(200))
    note = db.Column(db.Text)
    paid_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all,delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product_name = db.Column(db.String(300))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    views = db.Column(db.Integer, default=0)
    is_pinned = db.Column(db.Boolean, default=False)
    is_article = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    replies = db.relationship('Reply', backref='post', lazy=True, cascade='all,delete-orphan')

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user = db.relationship('User')

class NewsArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True)
    summary = db.Column(db.String(500))
    content = db.Column(db.Text)
    author = db.Column(db.String(100))
    source = db.Column(db.String(200))
    source_url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=True)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TurfProblem(db.Model):
    """草坪病害/虫害/杂草诊断库"""
    id = db.Column(db.Integer, primary_key=True)
    ptype = db.Column(db.String(20), nullable=False)  # disease/pest/weed
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    latin_name = db.Column(db.String(160))
    summary = db.Column(db.String(400))
    symptoms = db.Column(db.Text)       # 症状识别
    conditions = db.Column(db.Text)     # 发病/发生条件
    season = db.Column(db.String(80))   # 高发季节
    severity = db.Column(db.String(20), default='中')  # 低/中/高
    solution = db.Column(db.Text)       # 防治方案
    prevention = db.Column(db.Text)     # 预防措施
    product_keywords = db.Column(db.String(200))  # 推荐产品关键词(逗号分隔)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UsedMachine(db.Model):
    """二手机械市场"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(80))   # 剪草机/打孔机/喷灌等
    brand = db.Column(db.String(100))
    year = db.Column(db.String(20))
    hours = db.Column(db.String(40))      # 使用时长
    condition = db.Column(db.String(40))  # 成色
    price = db.Column(db.Float)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    contact = db.Column(db.String(120))
    image_url = db.Column(db.String(500))
    is_sold = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


def seed_data():
    """Initial data"""
    if Category.query.first(): return
    # Main categories
    cats = [
        ('草坪产品','products','专业草坪养护产品大全','🌾',1),
        ('技术论坛','forum','草坪养护技术交流社区','📋',2),
        ('养护知识','turf-care','草坪养护技术文章与指南','📖',3),
        ('行业资讯','news','草坪行业新闻与动态','📰',4),
        ('工具箱','tools','草坪养护计算器与实用工具','🔧',5),
    ]
    for n,s,d,i,o in cats:
        db.session.add(Category(name=n,slug=s,description=d,icon=i,display_order=o))
    db.session.commit()

    # Product subcategories
    subcats = [
        ('草坪草种','seed','各类运动场地草种，适配中国南北气候','🌾',1),
        ('足球场草种','football-seed','FIFA级足球场专用草种','⚽',1),
        ('果岭草种','green-seed','高尔夫果岭及高档景观草种','🏌️',1),
        ('暖季型草种','warm-seed','适合南方地区的暖季型草种','☀️',1),
        ('冷季型草种','cool-seed','适合北方地区的冷季型草种','❄️',1),
        ('肥料与土壤','fertilizer','草坪专用肥料与土壤改良剂','🧪',1),
        ('缓释肥','slow-fertilizer','长效缓释肥，一次施效管半年','⏳',1),
        ('土壤改良剂','soil-conditioner','改善土壤结构，促进根系发育','🌍',1),
        ('设备与机具','equipment','专业草坪养护机械设备','🔧',1),
        ('剪草机','mower','滚筒式、旋刀式专业剪草机','✂️',1),
        ('打孔/梳草机','aerator','草坪打孔通气、梳草设备','🔩',1),
        ('灌排水系统','irrigation','草坪自动喷灌与排水解决方案','💧',1),
        ('喷灌设备','sprinkler','专业喷头、阀门、控制系统','🚿',1),
        ('排水材料','drainage','排水板、排水管、砂基','🌊',1),
    ]
    for n,s,d,i,pid in subcats:
        db.session.add(ProductCategory(name=n,slug=s,description=d,icon=i,parent_id=pid))
    db.session.commit()

    # Products
    products = [
        ('百慕大419草种','bermuda-419','BKS-1001','顶级暖季型草种，耐热耐旱','百慕大419是运动场首选暖季型草种，耐践踏、恢复快，广泛用于足球场、高尔夫球场','每公斤可覆盖20㎡','198.00','https://images.pexels.com/photos/291679/pexels-photo-291679.jpeg','百慕大草业',True,1),
        ('黑麦草种(多年生)','perennial-rye','BKS-2001','冷季型草种，迅速成坪','多年生黑麦草，出芽快、成坪迅速，适合足球场补播及冬季足球场维护','每公斤可覆盖25㎡','88.00','https://images.pexels.com/photos/1263349/pexels-photo-1263349.jpeg','百慕大草业',True,1),
        ('本特草种','bentgrass','BKS-3001','果岭级草种，细腻致密','本特草果岭品质，叶片纤细致密，适合高尔夫果岭及高档景观草坪','每公斤可覆盖15㎡','268.00','https://images.pexels.com/photos/123593/pexels-photo-123593.jpeg','百慕大草业',True,3),
        ('结缕草种','zoysia','BKS-4001','耐阴耐旱，低维护','结缕草耐阴、耐旱、耐瘠薄，极其耐践踏，适合足球场及公共绿地','每公斤可覆盖30㎡','158.00','https://images.pexels.com/photos/6446/grass-green-field-meadow.jpg','百慕大草业',True,4),
        ('高羊茅草种','tall-fescue','BKS-5001','粗犷耐用的冷季型草','高羊茅根系发达、抗旱耐热，适合运动场及水土保持','每公斤可覆盖35㎡','68.00','https://images.pexels.com/photos/37628/peacock-grass-pasture-peafowl.jpg','百慕大草业',True,5),
        ('草坪专用缓释肥20-5-10','slow-fertilizer-20','FERT-001','N20-P5-K10缓释颗粒肥','专为运动草坪设计的缓释配方，氮磷钾配比20-5-10，肥效持续6个月，不烧苗','25kg/袋','368.00','https://images.pexels.com/photos/93398/pexels-photo-93398.jpeg','绿丰农化',True,7),
        ('草坪复绿肥','green-up-fertilizer','FERT-002','速效草坪复绿液体肥','速效液体肥，3天见效，适合赛前快速复绿，稀释后直接喷施','1L/瓶','88.00','https://images.pexels.com/photos/221012/pexels-photo-221012.jpeg','绿丰农化',True,7),
        ('有机土壤改良剂','organic-conditioner','SOIL-001','生物有机质土壤改良','含腐殖酸+有益微生物，改善土壤团粒结构，促进根系发育','20kg/袋','128.00','https://images.pexels.com/photos/7513/pexels-photo.jpg','沃土生物',True,8),
        ('滚刀式草坪剪草机','cylinder-mower','EQ-001','专业级滚刀式剪草机','适合足球场、高尔夫球场，剪草高度可调5-50mm，工作宽度76cm，配备集草箱','定制价格','0.00','https://images.pexels.com/photos/303134/pexels-photo-303134.jpeg','绿野机械',True,10),
        ('自走式打孔机','walk-aerator','EQ-002','小型草坪通气打孔机','8mm打孔针，可调深度20-80mm，适合中小型场地草坪打孔作业','询价','0.00','https://images.pexels.com/photos/35971/pexels-photo-35971.jpeg','绿野机械',True,11),
        ('自动旋转喷头','rotor-sprinkler','IRR-001','专业级地埋旋转喷头','360度可调角度，射程6-15米，覆盖面积280㎡','耐压8kg/cm²，全铜接头','498.00','https://images.pexels.com/photos/93398/pexels-photo-93398.jpeg','雨鸟灌溉',True,13),
        ('排水板(可拆卸)','drainage-board','DRAIN-001','HDPE可拆卸排水板','高强度HDPE材质，抗压50吨/㎡，排水量5L/秒/㎡','适合各类运动场地排水需求，可拆卸循环使用','85.00','https://images.pexels.com/photos/1105095/pexels-photo-1105095.jpeg','宇通排水',True,14),
    ]
    for p in products:
        name,slug,sku,sdesc,desc,specs,price,img,brand,featured,subcat_id = p
        db.session.add(Product(name=name,slug=slug,sku=sku,short_desc=sdesc,description=desc,
            specs=specs,price=float(price) if price!='0.00' else 99999.00,image_url=img,
            brand=brand,is_featured=featured,subcategory_id=subcat_id,stock=100,
            unit='袋' if '草种' in name else '袋' if '肥' in name else '瓶' if '瓶' in sku else '台' if 'EQ' in sku else '件'))
    db.session.commit()

    # News articles
    news = [
        ('2026年中国足球场草坪养护行业趋势报告','随着中超联赛职业化程度提升，运动场地草坪养护行业正迎来高速发展期。报告指出，2026年市场规模有望突破80亿元。','赵明义','中国草坪网'),
        ('FIFA Quality Pro认证标准更新：2026版解读','FIFA最新发布的场地认证标准在草坪密度、根系深度、排水速率等指标上提出了更高要求。','李振华','体育设施报'),
        ('世界杯球场草坪技术深度解析','从2022卡塔尔世界杯到2026美加墨，球场草坪技术在应对极端气候方面取得了哪些突破？','王磊','XFieldMate'),
        ('南方高尔夫球场夏季草坪养护要点','夏季高温高湿季节，暖季型草果岭如何保证推杆品质？专家分享实战经验。','陈思远','高尔夫周刊'),
        ('智慧灌溉：AI赋能草坪精准用水','基于土壤传感器和气象数据的智能灌溉系统，可节水30%以上，正在成为专业球场的标配。','周明','灌溉技术'),
    ]
    for title,content,author,source in news:
        slug = title.lower().replace(':','').replace(' ','-')[:100]
        db.session.add(NewsArticle(title=title,slug=slug,summary=content[:150],content=content,
            author=author,source=source,image_url='https://images.pexels.com/photos/303134/pexels-photo-303134.jpeg'))
    db.session.commit()

    seed_problems()

    # 第一个注册用户自动设为管理员
    first = User.query.order_by(User.id).first()
    if first and not first.is_admin:
        first.is_admin = True
        db.session.commit()


def seed_problems():
    """草坪病虫草害诊断库种子数据"""
    if TurfProblem.query.first(): return
    GREEN = 'https://images.pexels.com/photos/6231/marketing-color-colors-wheel.jpg'
    problems = [
        # ptype, name, slug, latin, summary, symptoms, conditions, season, severity, solution, prevention, keywords, img
        ('disease','褐斑病(立枯丝核菌)','brown-patch','Rhizoctonia solani',
         '高温高湿季节最常见的草坪真菌病害，能在数天内毁掉大片草坪。',
         '草坪上出现直径几厘米到数米的圆形或不规则枯黄斑块，清晨可见斑块边缘有灰白色"烟圈"状菌丝环；病叶呈水浸状腐烂、易拔起。',
         '气温25-32℃、空气湿度>85%、夜间结露时间长、氮肥过量、排水不良时高发。',
         '夏季(6-9月)','高',
         '①立即停止傍晚浇水，改为清晨灌溉缩短结露时间；②喷施嘧菌酯、苯醚甲环唑或丙环唑类杀菌剂，间隔7-10天连喷2-3次；③打孔通气、清除病残体。',
         '控制氮肥用量、增施钾肥提高抗性；保证排水与通风；避免傍晚浇水；高发期预防性喷药。',
         '杀菌剂,嘧菌酯,缓释肥,打孔',GREEN),
        ('disease','币斑病','dollar-spot','Clarireedia jacksonii',
         '细叶草坪与果岭最常见病害，形成大量银币大小的漂白斑点。',
         '草坪上密布直径2-5cm的圆形枯白色小斑(似银币)，相邻斑点可连成片；单株叶片出现两端深褐、中间漂白的束腰状病斑。',
         '昼夜温差大、夜间结露重、低氮、干旱胁迫的春秋季高发。',
         '春秋(4-6月/9-10月)','中',
         '①适当补充氮肥可显著减轻病情；②喷施嘧菌酯、戊唑醇或异菌脲；③清晨拖露水、减少叶面湿润时间。',
         '保持均衡施肥避免缺氮；改善灌溉时间；定期梳草减少枯草层。',
         '杀菌剂,氮肥,液体肥,梳草',GREEN),
        ('disease','腐霉枯萎病','pythium-blight',
         'Pythium spp.',
         '爆发最快、最致命的草坪病害，高温高湿夜间可一夜成灾。',
         '出现暗绿色油浸状不规则斑块，清晨湿润时可见白色棉絮状菌丝；病草迅速塌陷、黏滑、变褐枯死，斑块常沿排水/行走线呈条状蔓延。',
         '气温>30℃且夜温>20℃、湿度>90%、低洼积水、密植区高发。',
         '盛夏(7-8月)','高',
         '①紧急喷施甲霜灵·锰锌、霜霉威或乙膦铝等专性药剂；②立即排水、停止傍晚灌溉；③避免在病区行走与作业防止传播。',
         '改善排水与空气流通；避免夜间高湿；高温高湿期预防用药；控制密度。',
         '杀菌剂,排水板,缓释肥',GREEN),
        ('disease','红丝病','red-thread',
         'Laetisaria fuciformis',
         '低氮、冷凉潮湿环境下的常见病，以红色丝状菌体为典型特征。',
         '草坪出现淡粉至枯黄的不规则斑块，近看病叶尖端伸出红色至粉红色针状/丝状菌体，潮湿时明显。',
         '气温15-25℃、潮湿多雨、土壤贫瘠缺氮时高发。',
         '春秋多雨季','低',
         '①补充氮肥通常即可使草坪恢复；②严重时喷施戊唑醇或嘧菌酯；③改善通风。',
         '保持充足均衡施肥；及时清除枯草层；改善排水通风。',
         '氮肥,缓释肥,杀菌剂',GREEN),
        ('pest','蛴螬(金龟子幼虫)','grubs',
         'Scarabaeidae larvae',
         '啃食草坪根系的地下害虫，导致草皮成片枯死可整块掀起。',
         '草坪出现不规则枯黄斑块、浇水也不返青；草皮根系被咬断、可像地毯一样掀起；常伴鸟类、鼹鼠扒草觅食。',
         '成虫夏季产卵，幼虫秋季危害最重；沙质、有机质丰富土壤多发。',
         '夏末至秋季','高',
         '①使用噻虫胺、氯虫苯甲酰胺等土壤杀虫剂灌根；②可施用昆虫病原线虫做生物防治；③灌药后浇透水送药入根层。',
         '监测成虫高峰期；幼虫低龄期(8-9月)防治效果最佳；保持健壮根系。',
         '杀虫剂,生物防治,缓释肥',GREEN),
        ('pest','蝼蛄/夜蛾类','armyworm',
         'Spodoptera spp.',
         '咬食草坪叶片的地上害虫，短时间内可将草啃成秃斑。',
         '叶片被啃出缺刻、草坪边缘快速向内推进式变秃；傍晚或清晨可见幼虫；常伴大量鸟类聚集觅食。',
         '高温季节虫口暴增，新播草坪与嫩草受害重。',
         '夏秋','中',
         '①傍晚喷施氯虫苯甲酰胺、甲维盐等触杀型杀虫剂；②清除杂草减少产卵场所；③严重时连续防治。',
         '定期巡查；保留天敌；新坪期重点监测。',
         '杀虫剂,PPE,喷雾器',GREEN),
        ('weed','马唐','crabgrass',
         'Digitaria sanguinalis',
         '夏季最顽固的一年生禾本科杂草，繁殖力极强。',
         '匍匐状生长、节处生根呈放射状铺展，叶片宽扁淡绿，与草坪争光争肥形成斑块状疏草。',
         '春末土温升至15℃以上时萌发，疏草、低剪、裸露地块易爆发。',
         '春末至夏季','中',
         '①萌芽前(3-4月)施用二甲戊灵等芽前封闭除草剂；②已出苗用专性茎叶除草剂；③提高剪草高度增强草坪竞争力。',
         '保持草坪密度与适当剪草高度；芽前封闭是关键；及时补播裸地。',
         '除草剂,芽前除草剂,草种',GREEN),
        ('weed','早熟禾(一年生杂草型)','annual-bluegrass',
         'Poa annua',
         '果岭与精细草坪头号入侵杂草，浅绿色、抽穗影响平整与观感。',
         '浅黄绿色丛生、贴地抽出大量白色种穗，质地与周边草坪明显不同，低温季节尤为显眼。',
         '冷凉潮湿、土壤紧实、低剪果岭环境最适其入侵。',
         '秋冬至早春','中',
         '①使用专性芽前除草剂(如氟唑磺隆)抑制萌发；②打孔缓解土壤紧实；③精准控水控肥削弱其竞争。',
         '减少土壤紧实；控制过度灌溉；保持目标草坪健壮；芽前防治。',
         '除草剂,打孔,土壤改良剂',GREEN),
        ('weed','苔藓','moss',
         'Bryophyta',
         '并非真正杂草，但是草坪稀疏、环境潮湿阴蔽的信号性入侵物。',
         '低洼阴湿、树荫下或排水不良处形成毛毡状绿色/黄绿色苔层，草坪逐渐被取代变稀。',
         '荫蔽、潮湿、酸性土壤、紧实、低肥力、过度修剪共同诱发。',
         '阴湿季节','低',
         '①施用硫酸亚铁(铁制剂)直接灭杀苔藓使其变黑；②打孔改善排水、修剪树枝增加光照；③改良土壤并补播草种。',
         '根治需改善光照/排水/通气并提升草坪密度，单纯杀苔会复发。',
         '铁制剂,打孔,草种,土壤改良剂',GREEN),
    ]
    for p in problems:
        ptype,name,slug,latin,summary,sym,cond,season,sev,sol,prev,kw,img = p
        db.session.add(TurfProblem(ptype=ptype,name=name,slug=slug,latin_name=latin,summary=summary,
            symptoms=sym,conditions=cond,season=season,severity=sev,solution=sol,prevention=prev,
            product_keywords=kw,image_url=img))
    db.session.commit()

    # 二手机械市场种子
    machines = [
        ('出售 John Deere 2500B 三联滚刀果岭剪草机','剪草机','John Deere','2019','约1200小时','9成新',85000,'江苏·南京',
         '果岭专用三联滚刀，原装进口，保养记录齐全，刀片去年新换，因球场升级设备出售。','微信 turf_nj_2024'),
        ('Toro 打孔机 ProCore 648 转让','打孔/梳草机','Toro','2020','约800小时','95新',62000,'广东·广州',
         '648mm工作幅宽，空心打孔针，状态极好，附赠全套打孔针。','电话 138****6621'),
        ('二手雨鸟地埋喷灌系统(整场拆除)','喷灌设备','Rain Bird','2017','—','8成新',28000,'山东·济南',
         '某足球场改造拆除，含喷头48个+控制器+电磁阀，可整套打包，需自提。','微信 sd_irrigation'),
        ('久保田旋刀剪草机 F3690 出售','剪草机','Kubota','2018','约1500小时','8成新',98000,'浙江·杭州',
         '前置旋刀大型剪草机，柴油动力，适合大面积运动场，发动机大修过。','电话 159****3300'),
    ]
    for m in machines:
        title,cat,brand,year,hours,cond,price,loc,desc,contact = m
        db.session.add(UsedMachine(title=title,category=cat,brand=brand,year=year,hours=hours,
            condition=cond,price=price,location=loc,description=desc,contact=contact,
            image_url='https://images.pexels.com/photos/303134/pexels-photo-303134.jpeg'))
    db.session.commit()
