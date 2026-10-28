from otree.api import *
import itertools
import json
import math
import random
from math import cos, sin, pi


doc = """
DEMO version of the within-subject network public goods game.
Identical to network_within except NUM_ROUNDS = 3 (1 round per block).

Treatments:
- control
- cycle
- star

Structure:
- 3 treatments × 1 round = 3 rounds total
- Each player receives 15 tokens per round
- Payoff = (endowment - own contribution)
           + BETA × (closed neighborhood contribution / neighborhood size)
"""


# ============================================================
# CONSTANTS
# Deney boyunca değişmeyen sabit parametreler
# ============================================================
class C(BaseConstants):
    NAME_IN_URL = 'demo_network_within'
    PLAYERS_PER_GROUP = 3

    ENDOWMENT_INT = 15
    ENDOWMENT = cu(ENDOWMENT_INT)

    BETA = 1.5
    CONVERSION_RATE = 1.0

    ROUNDS_PER_BLOCK = 1  # Demo: her treatment bloğu 1 tur, toplam NUM_ROUNDS = 3
    BLOCKS = ['control', 'cycle', 'star']
    NUM_ROUNDS = ROUNDS_PER_BLOCK * len(BLOCKS)


# ============================================================
# SUBSESSION
# ============================================================
class Subsession(BaseSubsession):
    pass


# ============================================================
# HELPER FUNCTIONS
# Tekrarlayan işlemleri küçük yardımcı fonksiyonlarda topluyoruz
# ============================================================
def get_rate(player: 'Player'):
    """Jeton -> TL dönüşüm oranını döndürür."""
    return player.session.config.get('real_world_currency_per_point', C.CONVERSION_RATE)


def get_participation_bonus(player: 'Player'):
    """Katılım ücretini döndürür."""
    return player.session.config.get('participation_fee', 0)


def fmt_num(x, decimals=2):
    """Sayıyı hesaplandığı haliyle, en fazla 2 ondalıkla ve Türkçe ondalık virgülüyle gösterir
    (örn. 20 / 18,5 / 13,25). Yuvarlama yapılmaz: payoff'lar 0,25'in katlarıdır."""
    s = f"{float(x):.{decimals}f}".rstrip('0').rstrip('.')
    return (s or '0').replace('.', ',')


def ceil_tl(x) -> int:
    """Nihai ödemeyi tam liraya YUKARI yuvarlar (kayan nokta hatasına karşı önce 6 haneye yuvarlanır)."""
    return int(math.ceil(round(float(x), 6)))


def compute_payment(player: 'Player') -> dict:
    """Ödeme bileşenlerinin tek kaynağı (AltruismMeasure, FinalResults ve PaymentInfo burayı kullanır)."""
    rate = get_rate(player)
    fee = get_participation_bonus(player)
    total_tokens = sum(float(rp.payoff) for rp in player.in_all_rounds())
    game_tl = total_tokens * rate
    retained = float(player.get_charity_retained_amount())
    exact_total = game_tl + retained + fee
    return dict(
        rate=rate, fee=fee, total_tokens=total_tokens, game_tl=game_tl,
        retained=retained, exact_total=exact_total, payable_total=ceil_tl(exact_total),
    )


def get_block_index(round_number: int) -> int:
    """Round'un hangi blokta olduğunu 0-based index olarak döndürür."""
    return (round_number - 1) // C.ROUNDS_PER_BLOCK


def get_block_round(round_number: int) -> int:
    """Round'un blok içindeki sırasını döndürür: 1, 2, 3."""
    return (round_number - 1) % C.ROUNDS_PER_BLOCK + 1


def is_first_round_of_block(player: 'Player') -> bool:
    """Oyuncunun bulunduğu round bir treatment bloğunun ilk round'u mu?"""
    return ((player.round_number - 1) % C.ROUNDS_PER_BLOCK) == 0


def resolve_order_for_round(round_number: int, order_list: list[str]) -> str:
    """Verilen block order listesine göre ilgili round'un treatment tipini döndürür."""
    idx = get_block_index(round_number)
    if idx >= len(order_list):
        raise ValueError(f"Block order index out of range: idx={idx}, order={order_list}")
    return order_list[idx]


# ============================================================
# SESSION SETUP
# Her round başında grup ve treatment bilgilerini kurar
# ============================================================
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        # Round 1'de oyuncular rastgele gruplara atanır.
        # fixed_id_in_group=True olduğu için sonraki roundlarda id_in_group korunur.
        subsession.group_randomly(fixed_id_in_group=True)

        fixed_order = subsession.session.config.get('block_order')

        # Dengeli blok sırası: 3! = 6 permütasyon karıştırılıp gruplara sırayla verilir,
        # havuz bitince yeniden doldurulur. Oturumda 6 grup (18 kişi) varsa her sıra tam 1 kez çıkar.
        order_pool = []

        for group in subsession.get_groups():
            # ------------------------------------------------
            # Treatment sırası belirlenir
            # ------------------------------------------------
            if fixed_order:
                order = fixed_order[:]
            else:
                if not order_pool:
                    order_pool = [list(p) for p in itertools.permutations(C.BLOCKS)]
                    random.shuffle(order_pool)
                order = order_pool.pop()
            group.block_order = ','.join(order)

            # ------------------------------------------------
            # Star treatment için center sırası belirlenir
            # Amaç: 3 star round'unda herkesin bir kez center olması
            # ------------------------------------------------
            center_order = [1, 2, 3]
            random.shuffle(center_order)
            group.star_center_order = ','.join(str(x) for x in center_order)

            # ------------------------------------------------
            # Güvenlik için participant.vars içine de kaydedilir
            # ------------------------------------------------
            for player in group.get_players():
                player.participant.vars['block_order'] = order[:]
                player.participant.vars['star_center_order'] = center_order[:]

    else:
        # İlk round'daki grup yapısı ve order bilgileri sonraki roundlara taşınır.
        subsession.group_like_round(1)
        for group in subsession.get_groups():
            group.block_order = group.in_round(1).block_order
            group.star_center_order = group.in_round(1).star_center_order

    # --------------------------------------------------------
    # Her round için aktif network tipi belirlenir
    # ve treatment'a göre ağ yapısı kurulur
    # --------------------------------------------------------
    for group in subsession.get_groups():
        if not group.field_maybe_none('block_order'):
            raise ValueError(
                f"block_order is empty for group {group.id_in_subsession} in round {subsession.round_number}."
            )

        group.set_network_type_for_round()

        if not group.field_maybe_none('network_type'):
            raise ValueError(
                f"network_type could not be assigned for group {group.id_in_subsession} "
                f"in round {subsession.round_number}."
            )

        if group.network_type == 'cycle':
            group.assign_cycle_neighbors()
        elif group.network_type == 'star':
            group.assign_star_structure_balanced()
            group.build_star_graph_layout()
        else:
            # Control treatment'ta explicit neighbor tutulmaz.
            group.clear_neighbor_fields()

    # --------------------------------------------------------
    # Son adım: player düzeyinde role / degree / treatment bilgisi
    # --------------------------------------------------------
    for player in subsession.get_players():
        player.set_role_and_degree()
        player.treatment = player.group.network_type
        player.block_index = get_block_index(player.round_number) + 1
        player.block_round = get_block_round(player.round_number)


# ============================================================
# GROUP
# Grup düzeyinde treatment ve ağ yapısı bilgileri tutulur
# ============================================================
class Group(BaseGroup):
    block_order = models.StringField()
    network_type = models.StringField()

    network_nodes = models.LongStringField(initial='[]')
    network_edges = models.LongStringField(initial='[]')

    star_center_order = models.StringField(initial='')

    def set_network_type_for_round(self):
        """Bu round'da hangi treatment'ın aktif olduğunu belirler."""
        order = self.block_order.split(',')
        self.network_type = resolve_order_for_round(self.round_number, order)

    def clear_neighbor_fields(self):
        """Control treatment'ta önceki roundlardan kalabilecek neighbor bilgilerini temizler."""
        for player in self.get_players():
            player.neighbor1_id = None
            player.neighbor2_id = None

    def assign_cycle_neighbors(self):
        """
        3 kişilik cycle ağında herkesin iki komşusu vardır:
        1 -> 2 ve 3
        2 -> 3 ve 1
        3 -> 1 ve 2
        """
        players = self.get_players()
        n = len(players)

        if n != C.PLAYERS_PER_GROUP:
            raise ValueError("Cycle network grupları tam olarak 3 kişilik olmalıdır.")

        for i, player in enumerate(players):
            neighbor1 = players[(i + 1) % n]
            neighbor2 = players[(i - 1 + n) % n]
            player.neighbor1_id = neighbor1.id_in_group
            player.neighbor2_id = neighbor2.id_in_group

    def assign_star_structure_balanced(self):
        """
        Star treatment'ta center rolü, star bloğu içindeki 3 tur boyunca dengeli biçimde döner.
        """
        players = self.get_players()

        if len(players) != C.PLAYERS_PER_GROUP:
            raise ValueError("Star network grupları tam olarak 3 kişilik olmalıdır.")

        center_order = [int(x) for x in self.star_center_order.split(',')]

        # Doğru olan: block içindeki sıra
        star_round_index = get_block_round(self.round_number) - 1

        center_id = center_order[star_round_index % len(center_order)]
        center = self.get_player_by_id(center_id)

        periphery = [p for p in players if p.id_in_group != center_id]
        p1, p2 = periphery

        center.neighbor1_id = p1.id_in_group
        center.neighbor2_id = p2.id_in_group

        p1.neighbor1_id = center.id_in_group
        p1.neighbor2_id = None

        p2.neighbor1_id = center.id_in_group
        p2.neighbor2_id = None

    def build_star_graph_layout(self):
        """
        Star treatment için template'te kullanılacak node ve edge verisini üretir.
        """
        players = self.get_players()

        center = None
        periphery = []

        for player in players:
            neighbors = player.get_neighbors()
            if len(neighbors) == 2:
                center = player
            elif len(neighbors) == 1:
                periphery.append(player)

        if center is None or len(periphery) != 2:
            raise ValueError("Star graph layout oluşturulamadı: center/periphery yapısı hatalı.")

        coords = {
            center.id_in_group: (150, 150, 'center'),
            periphery[0].id_in_group: (70, 90, 'periphery'),
            periphery[1].id_in_group: (70, 210, 'periphery'),
        }

        nodes = [
            dict(id=pid, x=x, y=y, role=role)
            for pid, (x, y, role) in coords.items()
        ]
        edges = [
            dict(source=center.id_in_group, target=periphery[0].id_in_group),
            dict(source=center.id_in_group, target=periphery[1].id_in_group),
        ]

        self.network_nodes = json.dumps(nodes)
        self.network_edges = json.dumps(edges)

    def set_payoffs(self):
        """
        Payoff formülü:
        payoff = endowment - own_contribution
                 + BETA × (closed_neighborhood_total / neighborhood_size)
        """
        players = self.get_players()

        contributions = {
            p.id_in_group: (p.contribution if p.contribution is not None else 0)
            for p in players
        }

        for player in players:
            own_contribution = contributions[player.id_in_group]
            closed_neighborhood = player.get_closed_neighborhood()
            neighborhood_size = len(closed_neighborhood)

            if neighborhood_size <= 0:
                player.payoff = C.ENDOWMENT
                player.neighborhood_size = 0
                player.payoff_from_public = cu(0)
                continue

            total_contribution = sum(contributions[p.id_in_group] for p in closed_neighborhood)
            public_return = C.BETA * (total_contribution / neighborhood_size)

            player.neighborhood_size = neighborhood_size
            player.payoff_from_public = cu(public_return)
            player.payoff = C.ENDOWMENT - cu(own_contribution) + cu(public_return)


# ============================================================
# PLAYER
# Bireysel kararlar, survey alanları ve yardımcı metotlar
# ============================================================
class Player(BasePlayer):
    
    
    # --------------------------------------------------------
    # Oyun kararı
    # --------------------------------------------------------
    contribution = models.IntegerField(min=0, max=C.ENDOWMENT_INT)

    # --------------------------------------------------------
    # Treatment metadata
    # --------------------------------------------------------
    treatment = models.StringField()
    block_index = models.IntegerField()
    block_round = models.IntegerField()

    # --------------------------------------------------------
    # Network komşu alanları
    # Control'de None, cycle/star'da creating_session içinde atanır
    # --------------------------------------------------------
    neighbor1_id = models.IntegerField(null=True, blank=True)
    neighbor2_id = models.IntegerField(null=True, blank=True)

    # --------------------------------------------------------
    # Network metadata
    # --------------------------------------------------------
    network_role = models.StringField()
    degree = models.IntegerField()
    neighborhood_size = models.IntegerField()
    payoff_from_public = models.CurrencyField()

    # --------------------------------------------------------
    # Consent
    # --------------------------------------------------------
    consent_given = models.BooleanField(
        label="Yukarıdaki bilgileri okudum ve bu çalışmaya gönüllü olarak katılmayı kabul ediyorum.",
        widget=widgets.CheckboxInput,
        blank=False,
        error_messages={'required': 'Katılım için onay vermeniz gerekiyor'}
    )

    # --------------------------------------------------------
    # Section A: Charity dictator game
    # --------------------------------------------------------
    charity_d1 = models.IntegerField(min=0, max=100)


    # --------------------------------------------------------
    # Section B: Likert items
    # --------------------------------------------------------
    pt_b1 = models.IntegerField(choices=range(1, 8))
    pt_b2 = models.IntegerField(choices=range(1, 8))
    pt_b3 = models.IntegerField(choices=range(1, 8))
    pt_b4 = models.IntegerField(choices=range(1, 8))
    pt_b5 = models.IntegerField(choices=range(1, 8))
    pt_b6 = models.IntegerField(choices=range(1, 8))
    pt_b7 = models.IntegerField(choices=range(1, 8))
    pt_b8 = models.IntegerField(choices=range(1, 8))
    pt_b9 = models.IntegerField(choices=range(1, 8))
    pt_b10 = models.IntegerField(choices=range(1, 8))

    # --------------------------------------------------------
    # Section C: Altruism
    # --------------------------------------------------------
    alt_c1 = models.IntegerField(min=0, max=10)
    alt_c2 = models.IntegerField(min=0, max=10)

    # --------------------------------------------------------
    # Section D: SVO
    # --------------------------------------------------------
    svo_a1 = models.StringField(choices=['A', 'B', 'C'])
    svo_a2 = models.StringField(choices=['A', 'B', 'C'])
    svo_a3 = models.StringField(choices=['A', 'B', 'C'])

    # --------------------------------------------------------
    # Demographics
    # --------------------------------------------------------
    age = models.StringField(
        label="Yaş aralığınız nedir?",
        choices=["18–20", "21–23", "24–26", "27–30", "31 ve üzeri"],
        widget=widgets.RadioSelect
    )
    gender = models.StringField(
        label="Cinsiyetiniz nedir?",
        choices=["Kadın", "Erkek", "Belirtmek istemiyorum", "Diğer"],
        widget=widgets.RadioSelect
    )
    field_of_study = models.StringField(
        label="Okuduğunuz bölüm aşağıdakilerden hangisine daha yakındır?",
        choices=["Sayısal (STEM)", "Sözel (HASS)", "Karışık / Belirsiz"],
        widget=widgets.RadioSelect
    )
    year_of_study = models.StringField(
        label="Kaçıncı sınıftasınız?",
        choices=["Hazırlık", "1. sınıf", "2. sınıf", "3. sınıf", "4. sınıf", "Yüksek lisans", "Doktora"],
        widget=widgets.RadioSelect
    )
    cgpa = models.StringField(
        label="Genel not ortalamanız (4 üzerinden):",
        choices=["0.00–1.99", "2.00–2.49", "2.50–2.99", "3.00–3.49", "3.50–4.00"],
        widget=widgets.RadioSelect
    )
    monthly_income = models.StringField(
        label="Aylık ortalama geliriniz nedir?",
        choices=["0–10.000 TL", "10.001–30.000 TL", "30.001–50.000 TL", "50.001–100.000 TL", "100.001 TL ve üzeri", "Belirtmek istemiyorum"],
        widget=widgets.RadioSelect
    )
    risk_attitude = models.StringField(
        label="Belirsiz durumlarda risk almayı ne kadar tercih edersiniz?",
        choices=[
            "Hiç risk almam", "Çok az risk alırım", "Az risk alırım",
            "Orta düzeyde risk alırım", "Bazen risk alırım", "Sık sık risk alırım",
            "Risk almayı severim", "Oldukça riskli kararlar alırım",
            "Neredeyse her zaman risk alırım", "Tam anlamıyla risk severim"
        ],
        widget=widgets.RadioSelect
    )

    # --------------------------------------------------------
    # Helper methods
    # --------------------------------------------------------
    def _get_network_type(self):
        """
        Bu oyuncu için treatment tipini güvenli biçimde çözer.

        Öncelik:
        1) group.network_type
        2) group.block_order
        3) participant.vars['block_order']
        """
        network_type = self.group.field_maybe_none('network_type')
        if network_type:
            return network_type

        block_order = self.group.field_maybe_none('block_order')
        if block_order:
            order = block_order.split(',')
        else:
            order = self.participant.vars.get('block_order')

        if not order:
            raise ValueError(
                f"Could not resolve treatment for player {self.id_in_group} in round {self.round_number}."
            )

        return resolve_order_for_round(self.round_number, order)

    def set_role_and_degree(self):
        """
        Treatment tipine göre oyuncunun rolünü ve degree'sini belirler.
        """
        network_type = self._get_network_type()

        if network_type in ['control', 'cycle']:
            self.network_role = 'member'
            self.degree = C.PLAYERS_PER_GROUP - 1
            return

        if network_type == 'star':
            neighbors = self.get_neighbors()
            if len(neighbors) == 2:
                self.network_role = 'center'
                self.degree = 2
            elif len(neighbors) == 1:
                self.network_role = 'periphery'
                self.degree = 1
            else:
                raise ValueError(
                    f"Star treatment'ta player {self.id_in_group} için komşu sayısı {len(neighbors)}."
                )
            return

        raise ValueError(f"Bilinmeyen network tipi: {network_type}")

    def get_neighbors(self):
        """neighbor id alanlarını gerçek Player nesnelerine çevirir."""
        neighbors = []
        n1 = self.field_maybe_none('neighbor1_id')
        n2 = self.field_maybe_none('neighbor2_id')

        if n1 is not None:
            neighbors.append(self.group.get_player_by_id(n1))
        if n2 is not None:
            neighbors.append(self.group.get_player_by_id(n2))

        return [p for p in neighbors if p is not None]

    def get_closed_neighborhood(self):
        """
        Payoff hesabında kullanılan kapalı komşuluğu döndürür.
        Control treatment'ta tüm grup,
        diğer treatment'larda self + neighbors.
        """
        network_type = self._get_network_type()
        if network_type == 'control':
            return self.group.get_players()
        return [self] + self.get_neighbors()

    def get_charity_retained_amount(self):
        """Charity dictator bölümünde oyuncuda kalan miktarı hesaplar."""
        donation = self.field_maybe_none('charity_d1')
        if donation is None:
            return cu(100)
        return cu(100 - donation)
    
    # Excel export için ödeme özet alanları
    game_total_tl = models.CurrencyField()
    post_charity_total_tl = models.CurrencyField()
    final_total_tl = models.CurrencyField()




def get_neighborhood_size(player: Player) -> int:
    """Oyuncunun ilgili paylaşım grubunun büyüklüğünü döndürür."""
    network_type = player._get_network_type()

    if network_type == 'control':
        return len(player.group.get_players())

    if network_type == 'cycle':
        return C.PLAYERS_PER_GROUP

    if network_type == 'star':
        return 3 if player.network_role == 'center' else 2

    raise ValueError(f"Bilinmeyen network tipi: {network_type}")


def get_mpcr(player: Player) -> float:
    """MPCR = BETA / neighborhood_size"""
    return C.BETA / get_neighborhood_size(player)


def cycle_network_vars(player: Player):
    """Cycle ağı için node ve edge verisi üretir."""
    n = C.PLAYERS_PER_GROUP
    you_id = player.id_in_group

    r, cx, cy = 120.0, 150.0, 150.0

    coords = []
    for k in range(n):
        theta = 2 * pi * k / n - pi / 2
        coords.append((cx + r * cos(theta), cy + r * sin(theta)))

    nodes = [
        dict(
            id=i,
            x=round(coords[i - 1][0], 2),
            y=round(coords[i - 1][1], 2),
            is_you=(i == you_id),
        )
        for i in range(1, n + 1)
    ]

    edges = [dict(source=i, target=(i % n) + 1) for i in range(1, n + 1)]

    return dict(
        you_id=you_id,
        neighbor1_id=player.field_maybe_none('neighbor1_id'),
        neighbor2_id=player.field_maybe_none('neighbor2_id'),
        nodes=nodes,
        edges=edges,
        nodes_json=json.dumps(nodes),
        edges_json=json.dumps(edges),
        you_id_json=json.dumps(you_id),
    )


def star_network_vars(player: Player):
    """Group üzerinde hazırlanmış star graph verisini template'e taşır."""
    group = player.group
    try:
        nodes = json.loads(group.network_nodes or '[]')
        edges = json.loads(group.network_edges or '[]')
    except Exception:
        nodes, edges = [], []

    return dict(
        you_id=player.id_in_group,
        nodes=nodes,
        edges=edges,
        nodes_json=json.dumps(nodes),
        edges_json=json.dumps(edges),
        you_id_json=json.dumps(player.id_in_group),
    )


def network_vars(player: Player):
    """Treatment tipine göre uygun network görselleştirme verisini döndürür."""
    network_type = player._get_network_type()

    if network_type == 'cycle':
        return cycle_network_vars(player)

    if network_type == 'star':
        return star_network_vars(player)

    return dict(
        you_id=player.id_in_group,
        nodes=[],
        edges=[],
        nodes_json='[]',
        edges_json='[]',
        you_id_json=json.dumps(player.id_in_group),
    )


def build_round_row(round_player: Player, rate: float):
    """
    Results ve FinalResults tabloları için bir round özet satırı üretir.
    """
    group = round_player.group
    network_type = round_player._get_network_type()

    your_contribution = round_player.contribution or 0
    closed_players = round_player.get_closed_neighborhood()
    neigh_size = len(closed_players) if closed_players else 0

    if network_type == 'control':
        total_contribution = sum((p.contribution or 0) for p in group.get_players())
        neighborhood_size = len(group.get_players())
    else:
        total_contribution = (
            sum((p.contribution or 0) for p in closed_players)
            if neigh_size > 0 else your_contribution
        )
        neighborhood_size = neigh_size if neigh_size > 0 else get_neighborhood_size(round_player)

    others_contribution = total_contribution - your_contribution
    mpcr = (C.BETA / neighborhood_size) if neighborhood_size > 0 else 0

    keep = C.ENDOWMENT_INT - your_contribution
    public_return = mpcr * total_contribution
    payoff = float(round_player.payoff) if round_player.payoff is not None else 0.0

    return dict(
        round_num=round_player.round_number,
        network_type=network_type,
        network_label=(
            'Control' if network_type == 'control'
            else 'Cycle' if network_type == 'cycle'
            else 'Star'
        ),
        is_control=(network_type == 'control'),

        endowment=C.ENDOWMENT_INT,
        your_contribution=your_contribution,
        others_contribution=others_contribution,
        total_contribution=total_contribution,
        neighborhood_size=neighborhood_size,
        beta=C.BETA,
        mpcr=mpcr,
        keep=keep,
        public_return=public_return,
        public_return_str=fmt_num(public_return),
        payoff=payoff,
        payoff_str=fmt_num(payoff),
        payoff_tl_str=fmt_num(payoff * rate),
    )


# ============================================================
# PAGES
# ============================================================
class Consent(Page):
    """Katılımcı onay sayfası. Sadece round 1'de görünür."""
    form_model = 'player'
    form_fields = ['consent_given']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            participation_bonus=get_participation_bonus(player),
        )


class InstructionsControl(Page):
    """Control treatment talimat sayfası."""
    @staticmethod
    def is_displayed(player: Player):
        return is_first_round_of_block(player) and player._get_network_type() == 'control'

    @staticmethod
    def vars_for_template(player: Player):
        group_size = len(player.group.get_players())
        mpcr = C.BETA / group_size
        
        return dict(
            num_rounds=C.NUM_ROUNDS,
            rounds_per_block=C.ROUNDS_PER_BLOCK,
            endowment=C.ENDOWMENT_INT,
            beta=C.BETA,
            group_size=group_size,
            mpcr_str=f"{mpcr:.2f}",
            participation_bonus=get_participation_bonus(player),
            rate=get_rate(player),
)


class InstructionsCycle(Page):
    """Cycle treatment talimat sayfası."""
    @staticmethod
    def is_displayed(player: Player):
        return is_first_round_of_block(player) and player._get_network_type() == 'cycle'

    @staticmethod
    def vars_for_template(player: Player):
        group_size = C.PLAYERS_PER_GROUP
        neighborhood_size = C.PLAYERS_PER_GROUP
        mpcr = C.BETA / neighborhood_size

        return dict(
            num_rounds=C.NUM_ROUNDS,
            rounds_per_block=C.ROUNDS_PER_BLOCK,
            endowment=C.ENDOWMENT_INT,
            beta=C.BETA,
            group_size=group_size,
            neighborhood_size=neighborhood_size,
            mpcr_str=f"{mpcr:.2f}",
            participation_bonus=get_participation_bonus(player),
            rate=get_rate(player),
            degree=player.degree,
            **network_vars(player),
        )


class InstructionsStar(Page):
    """Star treatment talimat sayfası."""
    @staticmethod
    def is_displayed(player: Player):
        return is_first_round_of_block(player) and player._get_network_type() == 'star'

    @staticmethod
    def vars_for_template(player: Player):
        beta = C.BETA
        endowment = C.ENDOWMENT_INT

        mpcr_center = beta / 3
        mpcr_periphery = beta / 2

        nv = network_vars(player)

        safe_role = player.field_maybe_none('network_role') or ''

        return dict(
            num_rounds=C.NUM_ROUNDS,
            rounds_per_block=C.ROUNDS_PER_BLOCK,
            group_size=C.PLAYERS_PER_GROUP,
            endowment=endowment,
            beta=beta,

            participation_bonus=get_participation_bonus(player),
            rate=get_rate(player),
            network_role=safe_role,

            neighborhood_size=(
                3 if safe_role == 'center'
                else 2 if safe_role == 'periphery'
                else 0
            ),

            mpcr_center_str=f"{mpcr_center:.2f}",
            mpcr_periphery_str=f"{mpcr_periphery:.2f}",
            **nv,
            my_id_json=json.dumps(player.id_in_group),
        )


class Contribution(Page):
    """Her round'da katkı kararının verildiği sayfa."""
    form_model = 'player'
    form_fields = ['contribution']

    @staticmethod
    def vars_for_template(player: Player):
        network_type = player._get_network_type()
        neighborhood_size = get_neighborhood_size(player)
        mpcr = get_mpcr(player)

        you_idx = player.id_in_group
        left_idx = None
        right_idx = None

        if network_type == 'cycle':
            n = C.PLAYERS_PER_GROUP
            left_idx = you_idx - 1 if you_idx > 1 else n
            right_idx = you_idx + 1 if you_idx < n else 1

        elif network_type == 'star':
            neighbor_ids = sorted([p.id_in_group for p in player.get_neighbors()])
            if len(neighbor_ids) == 2:
                left_idx, right_idx = neighbor_ids
            elif len(neighbor_ids) == 1:
                left_idx = neighbor_ids[0]

        return dict(
            round_num=player.round_number,
            num_rounds=C.NUM_ROUNDS,
            network_type=network_type,
            endowment=C.ENDOWMENT_INT,
            beta=C.BETA,

            degree=player.field_maybe_none('degree') or 0,
            network_role=player.field_maybe_none('network_role') or '',

            neighborhood_size=neighborhood_size,
            mpcr=mpcr,
            mpcr_str=f"{mpcr:.2f}",
            group_size=C.PLAYERS_PER_GROUP,
            contribution=player.field_maybe_none('contribution') or 0,
            you_idx=you_idx,
            left_idx=left_idx,
            right_idx=right_idx,

            **network_vars(player),
        )


class WaitForAll(WaitPage):
    """Tüm oyuncular karar verene kadar bekler, ardından payoff hesaplanır."""
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.set_payoffs()


class Results(Page):
    """Her round sonunda gösterilen sonuç sayfası."""
    @staticmethod
    def vars_for_template(player: Player):
        rate = get_rate(player)
        network_type = player._get_network_type()

        rows = []
        cumulative_payoff = 0.0

        for round_player in player.in_all_rounds():
            row = build_round_row(round_player, rate)
            cumulative_payoff += row["payoff"]
            row["cum_payoff"] = cumulative_payoff
            row["cum_payoff_str"] = fmt_num(cumulative_payoff)
            rows.append(row)

        sentence = "Henüz tamamlanmış tur bulunmamaktadır."
        if rows:
            last = rows[-1]
            pool_scope = 'grup' if last['is_control'] else 'komşuluk'

            sentence = (
                f"Bu turda {last['your_contribution']} jeton katkı yaptınız, "
                f"diğer oyuncular ise toplam {last['others_contribution']} jeton katkı yaptı; "
                f"{pool_scope} ortak havuzunda toplanan katkı {last['total_contribution']} oldu. "
                f"Toplam katkı {last['beta']} ile çarpılarak {last['neighborhood_size']} kişi arasında paylaştırıldı. "
                f"Dolayısıyla ortak havuzdan size düşen pay {last['public_return_str']} jeton oldu. "
                f"Sizde kalan {last['keep']} jeton ile birlikte bu tur kazancınız "
                f"{last['payoff_str']} jeton (≈ {last['payoff_tl_str']} TL)."
            )

        closed_now = player.get_closed_neighborhood()
        neigh_size = len(closed_now)
        neigh_total_contribution = sum((p.contribution or 0) for p in closed_now)

        return dict(
            num_rounds=C.NUM_ROUNDS,
            round_num=player.round_number,
            network_type=network_type,
            rate=rate,
            
            network_role=player.field_maybe_none('network_role') or '',

            cols=rows,
            this_round_sentence=sentence,

            neigh_size=neigh_size,
            neigh_total_contribution=neigh_total_contribution,

            beta=C.BETA,
            group_size=C.PLAYERS_PER_GROUP,
        )


class Demographics(Page):
    """Demografik sorular. Sadece son round'da görünür."""
    form_model = 'player'
    form_fields = [
        'age', 'gender', 'field_of_study', 'year_of_study',
        'cgpa', 'monthly_income', 'risk_attitude',
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


class AltruismMeasure(Page):
    form_model = 'player'
    form_fields = (
        ['charity_d1']
        + [f'pt_b{i}' for i in range(1, 11)]
        + ['alt_c1', 'alt_c2']
        + ['svo_a1', 'svo_a2', 'svo_a3']
    )

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pay = compute_payment(player)

        # 1) Sadece oyun kazancı (TL, yuvarlanmamış)
        player.game_total_tl = cu(pay['game_tl'])

        # 2) Oyun + bağış sonrası oyuncuda kalan miktar (yuvarlanmamış)
        player.post_charity_total_tl = cu(pay['game_tl'] + pay['retained'])

        # 3) Nihai ödeme = oyun + kalan + katılım ücreti, tam liraya YUKARI yuvarlanmış
        player.final_total_tl = cu(pay['payable_total'])

        # oTree admin 'Payments' sayfası = participant.payoff x kur + katılım ücreti hesaplar.
        # Bu yüzden participant.payoff'a katılım ücreti EKLENMEZ (aksi halde ücret 2 kez sayılırdı).
        player.participant.payoff = cu((pay['payable_total'] - pay['fee']) / pay['rate'])

        # Aynı özet alanlarını tüm round kayıtlarına kopyalayarak export'ta boşluk riskini azalt
        for rp in player.in_all_rounds():
            rp.game_total_tl = player.game_total_tl
            rp.post_charity_total_tl = player.post_charity_total_tl
            rp.final_total_tl = player.final_total_tl


class FinalResults(Page):
    """Son round sonunda genel ödeme özetini gösterir."""
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        rate = get_rate(player)
        pay = compute_payment(player)

        rows = []
        cumulative_payoff = 0.0

        for round_player in player.in_all_rounds():
            row = build_round_row(round_player, rate)
            cumulative_payoff += row["payoff"]
            row["cum_payoff"] = cumulative_payoff
            row["cum_payoff_str"] = fmt_num(cumulative_payoff)
            rows.append(row)

        return dict(
            participant_code=player.participant.code,
            num_rounds=C.NUM_ROUNDS,
            rate=rate,
            cols=rows,

            total_tokens=pay['total_tokens'],
            total_tokens_str=fmt_num(pay['total_tokens']),

            total_tl_from_game=pay['game_tl'],
            total_tl_from_game_str=fmt_num(pay['game_tl']),

            retained_amount=pay['retained'],
            retained_amount_str=fmt_num(pay['retained']),

            participation_bonus=pay['fee'],
            participation_bonus_str=fmt_num(pay['fee']),

            exact_total_str=fmt_num(pay['exact_total']),
            grand_total_tl=pay['payable_total'],
            grand_total_tl_str=str(pay['payable_total']),
        )


class PaymentInfo(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        pay = compute_payment(player)

        return dict(
            participant_code=player.participant.code,
            total_tl_from_game=pay['game_tl'],
            total_tl_from_game_str=fmt_num(pay['game_tl']),
            retained_amount=pay['retained'],
            retained_amount_str=fmt_num(pay['retained']),
            participation_bonus=pay['fee'],
            participation_bonus_str=fmt_num(pay['fee']),
            exact_total_str=fmt_num(pay['exact_total']),
            grand_total_tl=pay['payable_total'],
            grand_total_tl_str=str(pay['payable_total']),
        )


class ThankYou(Page):
    """Kapanış sayfası."""
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


# ============================================================
# PAGE SEQUENCE
# Üç instruction sayfası da sequence içinde var;
# hangisinin gösterileceğine is_displayed karar veriyor.
# ============================================================
page_sequence = [
    Consent,
    InstructionsControl,
    InstructionsCycle,
    InstructionsStar,
    Contribution,
    WaitForAll,
    Results,
    Demographics,
    AltruismMeasure,
    FinalResults,
    PaymentInfo,
    ThankYou,
]


# ============================================================
# MODULE EXPORTS
# Bu liste, modül dışına açılan sınıf ve page adlarını toplar.
# ============================================================
__all__ = [
    'C', 'Subsession', 'Group', 'Player',
    'Consent',
    'InstructionsControl', 'InstructionsCycle', 'InstructionsStar',
    'Contribution', 'WaitForAll', 'Results', 'FinalResults',
    'Demographics', 'AltruismMeasure', 'PaymentInfo', 'ThankYou',
]