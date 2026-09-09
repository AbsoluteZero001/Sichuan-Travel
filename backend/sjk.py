import mysql.connector
from mysql.connector import Error

config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'sichuan_tourism',
    'charset': 'utf8mb4'
}

EXTRA_SPOTS = [
    ('大熊猫繁育研究基地', '成都市', '春季', 55.00, '07:30-18:00', '/images/dxm.jpg', '["/images/dxm.jpg"]', '成都大熊猫繁育研究基地位于成都市成华区，是世界著名的大熊猫迁地保护基地，可以近距离观看憨态可掬的大熊猫和幼年熊猫。', '自驾：成都市区沿三环路到达北湖附近。公共交通：可乘坐地铁3号线至熊猫大道站，换乘景区接驳车。', '建议上午前往，大熊猫早晨最活跃。旺季请提前预约门票。'),
    ('黄龙', '阿坝藏族羌族自治州', '秋季', 170.00, '08:00-18:00', '/images/huanglong.jpg', '["/images/huanglong.jpg"]', '黄龙风景名胜区位于四川省阿坝藏族羌族自治州松潘县境内，以彩池、雪山、峡谷、森林著称，被称为"人间瑶池"。', '自驾：成都出发经都江堰、汶川、茂县至松潘。公共交通：成都茶店子客运站有班车前往松潘。', '景区海拔较高，需预防高原反应。秋季彩池颜色最为绚丽。'),
    ('西岭雪山', '成都市', '冬季', 120.00, '09:00-17:00', '/images/xiling-xueshan.jpg', '["/images/xiling-xueshan.jpg"]', '西岭雪山位于四川省成都市大邑县境内，是成都周边最受欢迎的滑雪和冰雪旅游胜地，因杜甫诗句"窗含西岭千秋雪"而得名。', '自驾：成都出发经成温邛高速至大邑，再前往西岭雪山。公共交通：成都茶店子客运站有直达西岭雪山的班车。', '冬季可体验滑雪、雪地摩托等项目，请提前准备好防寒装备。'),
    ('蜀南竹海', '宜宾市', '夏季', 100.00, '08:00-18:00', '/images/shunan-zhuhai.jpg', '["/images/shunan-zhuhai.jpg"]', '蜀南竹海位于四川省宜宾市长宁县境内，是国内外罕见的竹类生态景观，万亩翠竹连绵起伏，景色清幽宜人。', '自驾：成都出发经成宜高速至宜宾，转蜀南竹海旅游公路。公共交通：成都东站有高铁至宜宾西站。', '夏季清凉避暑，适合徒步和拍照，建议游玩一天至两天。'),
    ('阆中古城', '南充市', '春季', 110.00, '08:00-18:00', '/images/langzhong-gucheng.jpg', '["/images/langzhong-gucheng.jpg"]', '阆中古城位于四川省南充市阆中市，是中国保存最完好的四大古城之一，拥有两千多年历史，城内古街古院保存完好。', '自驾：成都出发经成巴高速至阆中，车程约3小时。公共交通：成都东站有动车直达阆中。', '古城适合步行游览，建议在古城内住宿一晚，体验夜景和晨景。'),
    ('泸沽湖', '凉山彝族自治州', '夏季', 70.00, '08:00-18:00', '/images/lugu-lake.jpg', '["/images/lugu-lake.jpg"]', '泸沽湖位于四川省凉山彝族自治州盐源县与云南省交界处，是中国第三大深水湖泊，以摩梭文化和清澈湖景闻名。', '自驾：成都出发经雅西高速至西昌，再前往泸沽湖。公共交通：可先乘飞机至西昌，再转旅游大巴。', '可以环湖骑行、乘猪槽船游湖，请尊重当地摩梭风俗。')
]

def insert_missing_spots(cursor):
    cursor.execute("SELECT name FROM spots")
    existing_names = {row[0] for row in cursor.fetchall()}
    new_spots = [spot for spot in EXTRA_SPOTS if spot[0] not in existing_names]
    if new_spots:
        cursor.executemany(
            "INSERT INTO spots (name, city, season, price, open_time, image, images, description, guide, tips) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            new_spots
        )

def get_connection():
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None

def init_db():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('user', 'admin') DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spots (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                city VARCHAR(50) NOT NULL,
                season ENUM('春季','夏季','秋季','冬季'),
                price DECIMAL(10,2) DEFAULT 0,
                open_time VARCHAR(50),
                image VARCHAR(255),
                images TEXT,
                description TEXT,
                guide TEXT,
                tips TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spot_favorites (
                id INT PRIMARY KEY AUTO_INCREMENT,
                spot_id INT NOT NULL,
                user_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (spot_id) REFERENCES spots(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_favorite (spot_id, user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
            cursor.execute("INSERT INTO users (username, password, role) VALUES ('user1', 'user123', 'user')")
        
        cursor.execute("SELECT COUNT(*) FROM spots")
        if cursor.fetchone()[0] == 0:
            spots_data = [
                ('九寨沟', '阿坝藏族羌族自治州', '秋季', 169.00, '07:30-17:00', '/images/jiuzhaigou.jpg', '["/images/jiuzhaigou.jpg"]', '九寨沟位于四川省阿坝藏族羌族自治州九寨沟县境内，因沟内有九个藏族村寨而得名。', '自驾：成都出发沿都汶高速至汶川。', '最佳游览季节为9-10月。'),
                ('峨眉山', '乐山市', '夏季', 160.00, '06:00-18:00', '/images/emeishan.jpg', '["/images/emeishan.jpg"]', '峨眉山是中国"四大佛教名山"之一，地势陡峭，风景秀丽。', '成都东站有高铁直达峨眉山。', '山上气候变化大，请备好防寒衣物。'),
                ('都江堰', '成都市', '春季', 90.00, '08:00-18:00', '/images/dujiangyan.jpg', '["/images/dujiangyan.jpg"]', '都江堰是战国时期秦国蜀郡太守李冰父子率众修建的大型水利工程。', '成都市区沿成灌高速直达都江堰。', '建议下午游览，光线较好适合拍照。'),
                ('乐山大佛', '乐山市', '春季', 80.00, '08:00-18:00', '/images/leshan-dafo.jpg', '["/images/leshan-dafo.jpg"]', '乐山大佛是中国最大的一尊摩崖石刻造像。', '成都东站有高铁至乐山。', '可乘船游览，从江上观看大佛全景更震撼。'),
                ('稻城亚丁', '甘孜藏族自治州', '秋季', 150.00, '06:00-18:00', '/images/daocheng-yading.jpg', '["/images/daocheng-yading.jpg"]', '稻城亚丁风景区由三座神山和周围的河流、湖泊和高山草甸组成。', '可飞抵稻城亚丁机场。', '海拔较高，请注意高原反应。'),
                ('四姑娘山', '阿坝藏族羌族自治州', '夏季', 150.00, '08:00-17:00', '/images/siguniangshan.jpg', '["/images/siguniangshan.jpg"]', '四姑娘山由四座绵延不断的山峰组成，被誉为"东方的阿尔卑斯山"。', '成都茶店子客运站有直达小金县的班车。', '双桥沟适合普通游客游览。'),
                ('青城山', '成都市', '夏季', 60.00, '08:00-18:00', '/images/qingchengshan.jpg', '["/images/qingchengshan.jpg"]', '青城山群峰环绕起伏、林木葱茏幽翠，享有"青城天下幽"的美誉。', '成都茶店子客运站有直达青城山的班车。', '夏季凉爽宜人，是避暑好去处。'),
                ('海螺沟', '甘孜藏族自治州', '冬季', 90.00, '08:00-14:00', '/images/hailuogou.jpg', '["/images/hailuogou.jpg"]', '海螺沟是亚洲最低海拔的现代冰川之一。', '成都新南门车站有直达磨西镇的车票。', '冬季是观赏冰川的最佳季节。')
            ]
            cursor.executemany("INSERT INTO spots (name, city, season, price, open_time, image, images, description, guide, tips) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", spots_data)

        insert_missing_spots(cursor)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("数据库初始化完成")
