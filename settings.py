from os import environ

# =========================================================
# SESSION CONFIGURATIONS
# Her session config, oTree admin panelinde ayrı bir oturum
# türü olarak görünür.
# =========================================================

SESSION_CONFIGS = [

    # -----------------------------------------------------
    # Tek başına Control treatment'ını çalıştırmak için
    # -----------------------------------------------------
    dict(
        name='network_control',
        display_name="Control Treatment",
        num_demo_participants=3,
        app_sequence=['network_control'],
    ),

    # -----------------------------------------------------
    # Tek başına Cycle treatment'ını çalıştırmak için
    # -----------------------------------------------------
    dict(
        name='network_cycle',
        display_name="Cycle Treatment",
        num_demo_participants=3,
        app_sequence=['network_cycle'],
    ),

    # -----------------------------------------------------
    # Tek başına Star treatment'ını çalıştırmak için
    # -----------------------------------------------------
    dict(
        name='network_star',
        display_name="Star Treatment",
        num_demo_participants=3,
        app_sequence=['network_star'],
    ),

    # -----------------------------------------------------
    # Tüm blokların tek uygulama içinde yürütüldüğü ana yapı
    # block_order sabit verilirse treatment sırası random olmaz
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
    #    block_order=['control', 'cycle', 'star'],
    ),
]


# ---------------------------------------------------------
# SINIF OTURUMLARI: 3 kişi bulunur bulunmaz tek gruplu oturum
# Her yapılandırma blok sırasını SABİT verir. Sırayı 1'den 6'ya sırayla
# döndürürsen (1,2,3,4,5,6,1,2,...) altı sıra oturumlar boyunca dengeli kalır.
# Oturum oda üzerinden (Rooms > Sınıf Oturumu) 3 katılımcıyla açılır.
# ---------------------------------------------------------
_BLOCK_ORDERS = [
    ['control', 'cycle', 'star'],
    ['control', 'star', 'cycle'],
    ['cycle', 'control', 'star'],
    ['cycle', 'star', 'control'],
    ['star', 'control', 'cycle'],
    ['star', 'cycle', 'control'],
]
for _n, _order in enumerate(_BLOCK_ORDERS, start=1):
    SESSION_CONFIGS.append(dict(
        name=f'sinif_sira{_n}',
        display_name=f'Sınıf (3 kişi) - Sıra {_n}: ' + ' > '.join(_order),
        app_sequence=['network_within'],
        num_demo_participants=3,
        participation_fee=100,
        real_world_currency_per_point=1.0,
        block_order=_order,
    ))


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
    'network_control',
    'network_cycle',
    'network_star',
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
