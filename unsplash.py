"""TurfPro 统一图库 — 全部使用 Unsplash 直连图（国内可达，免VPN）。
原 pexels 链接已全部失效(404)，故重建。"""
import random

# 经过可达性验证(200)的 Unsplash photo id，按主题归类
PHOTO = {
    # 球场/场地
    "stadium":        "1459865264687-595d652de67e",
    "soccer":         "1551958219-acbc608c6377",
    "field_green":    "1530549387789-4c1017266635",
    "field_aerial":   "1431324155629-1a6deb1dec8d",
    "field_wide":     "1574629810360-7efbbe195018",
    "field_open":     "1486286701208-1d58e9338013",
    "stadium_night":  "1522778119026-d647f0596c20",
    "golf":           "1587174486073-ae5e5cff23aa",
    "golf2":          "1535131749006-b7f58c99034b",
    "rugby":          "1485395037613-e83d5c1f5290",
    "tennis":         "1554068865-24cecd4e34b8",
    "landscape":      "1558618666-fcd25c85cd64",
    # 草坪特写/材质
    "grass_macro":    "1500382017468-9049fed747ef",
    "turf_roll":      "1558904541-efa843a96f01",
    # 产品类
    "seeds":          "1574943320219-553eb213f72d",
    "soil":           "1622383563227-04401ab4e5ea",
    "watering":       "1416879595882-3373a0480b5b",
    "sprinkler":      "1565011523534-747a8601f10a",
    "mower":          "1556910103-1c02745aae4d",
    "tractor":        "1605000797499-95a51c5269ae",
    # 问题诊断
    "disease":        "1591857177580-dc82b9ac4e1e",
    "weeds":          "1592419044706-39796d40f98c",
    "pest":           "1589923188900-85dae523342b",
    # 资讯
    "news":           "1495107334309-fcf20504a5ab",
}

def u(name, w=800, h=600, q=75):
    """生成裁剪后的图片 URL。"""
    pid = PHOTO.get(name, PHOTO["field_green"])
    fit = f"&h={h}&fit=crop" if h else "&fit=max"
    return f"https://images.unsplash.com/photo-{pid}?w={w}{fit}&q={q}&auto=format"

HERO_IMAGES = [u("stadium",1600,900), u("soccer",1600,900), u("field_aerial",1600,900),
               u("golf",1600,900), u("stadium_night",1600,900)]

CATEGORY_IMAGES = {
    'turf-care': u("grass_macro"), 'field-standards': u("field_green"),
    'irrigation': u("sprinkler"), 'equipment': u("mower"),
    'pest-control': u("disease"), 'market': u("tractor"),
    'products': u("seeds"), 'all': u("field_green"),
}

def get_hero_image():
    return random.choice(HERO_IMAGES)

def get_category_images(slug):
    img = CATEGORY_IMAGES.get(slug, CATEGORY_IMAGES['all'])
    return {'hero': img, 'thumb': img}

def search_turf_images(query="sports field", count=4):
    return HERO_IMAGES[:count]
