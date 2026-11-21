from os import environ

# =========================================================
# SESSION CONFIGURATIONS
# Her session config, oTree admin panelinde ayrı bir oturum
# türü olarak görünür.
# =========================================================

SESSION_CONFIGS = [

    # -----------------------------------------------------
    # ANA DENEY: tüm blokların (control, cycle, star) tek uygulama içinde
    # yürütüldüğü 18 turluk yapı. block_order verilmezse sıra gruplara
    # dengeli ve rastgele atanır; sabit sıra için aşağıdaki satırı açın.
    # -----------------------------------------------------
    dict(
        name='network_within',
        app_sequence=['network_within'],
        num_demo_participants=3,
        participation_fee=100,
        real_world_currency_per_point=1.0,
    #    block_order=['control', 'cycle', 'star'],
    ),

    # -----------------------------------------------------
    # DEMO: network_within ile birebir aynı, yalnızca
    # toplam 3 tur (her treatment bloğu 1 tur)
    # -----------------------------------------------------
    dict(
        name='demo_network_within',
        display_name="DEMO - Network Within (3 tur)",
        app_sequence=['demo_network_within'],
        num_demo_participants=3,
        participation_fee=100,
        real_world_currency_per_point=1.0,
        block_order=['control', 'cycle', 'star'],  # demo: sabit sıra
    ),
]


# =========================================================
# DEFAULT SESSION SETTINGS
# Buradaki değerler, SESSION_CONFIGS içinde ayrıca
# tanımlanmadığı sürece varsayılan olarak kullanılır.
# =========================================================

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.0,
    participation_fee=100.0,
    doc="",
)


# =========================================================
# LANGUAGE AND CURRENCY SETTINGS
# =========================================================

LANGUAGE_CODE = 'tr'
REAL_WORLD_CURRENCY_CODE = 'TRY'
USE_POINTS = True
# Payoff'lar (0,5 / 0,25 gibi) yuvarlanmadan, 2 ondalıkla saklanır ve gösterilir.
POINTS_DECIMAL_PLACES = 2


# =========================================================
# INSTALLED APPS
# oTree'nin ve projedeki uygulamaların burada tanımlanması gerekir
# =========================================================

INSTALLED_APPS = [
    'otree',
    'network_within',
    'demo_network_within',
]


# =========================================================
# ADMIN AND SECURITY SETTINGS
# Not: Bu bilgileri GitHub'a koymadan önce mutlaka değiştir.
# Özellikle gerçek bir sunucuya çıkarken güçlü bir admin şifresi kullan.
# =========================================================

# Gerçek oturumda şifreler ortam değişkenlerinden okunur (baslat_sinif.ps1 bunları ayarlar).
# Dosyada/GitHub'da şifre tutulmaz. Ortam değişkeni yoksa (devserver) varsayılanlar geçerli olur.
SECRET_KEY = environ.get('OTREE_SECRET_KEY', 'yerel-gelistirme-anahtari')
ADMIN_USERNAME = 'eoy'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')


# =========================================================
# ROOMS
# Her laboratuvar için kalıcı oda: terminal etiketleri _rooms/*.txt dosyalarından gelir.
# Katılımcı terminalinin sabit bağlantısı sayesinde bağlantı koparsa kaldığı yerden devam eder.
# Oturum, odadaki katılımcı sayısı 3'ün katına ulaşınca admin panelinden başlatılır.
# =========================================================

ROOMS = [
    # Sınıf oturumu: etiket dosyası YOK; herkes aynı adresle girer (/room/sinif)
    dict(
        name='sinif',
        display_name='Sınıf Oturumu',
    ),
    # Demo oturumu için ayrı oda (/room/demo): ana deneyle aynı tarayıcı çerezi karışmasın
    dict(
        name='demo',
        display_name='Demo Oturumu',
    ),
    dict(
        name='itu_lab',
        display_name='İTÜ Laboratuvarı',
        participant_label_file='_rooms/itu_lab.txt',
    ),
    dict(
        name='yeditepe_lab',
        display_name='Yeditepe Laboratuvarı',
        participant_label_file='_rooms/yeditepe_lab.txt',
    ),
]
