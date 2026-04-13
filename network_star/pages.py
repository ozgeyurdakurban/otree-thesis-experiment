# star_network/pages.py
from otree.api import *
from .models import C, Player, Group
# math importu artık gerekmeyebilir, çünkü koordinatlar sabit
# from math import cos, sin, pi 

doc = """
Star Network Treatment Sayfaları
- Consent: Genel onay
- Instructions: Star kuralları, role özel MPCR ve örnekler, ağ görseli
- AltruismMeasure: DG ve SVO ölçümü
- Contribution: Katkı kararı, role özel MPCR hatırlatması, ağ görseli
- Results: Sonuçlar, role özel komşuluk hesaplamaları
"""

# --- Ağ Görselleştirmesi için Yardımcı Fonksiyonlar (Star'a Özel) ---

def _star_coords(n: int, width=300, height=300):
    """Star ağı için sabit koordinatlar üretir (merkez altta)."""
    # Merkez (ID=1)
    cx, cy = width / 2, height * 0.8  # Alt ortaya yakın
    # Çevreler (ID=2, ID=3)
    p1x, p1y = width * 0.25, height * 0.2
    p2x, p2y = width * 0.75, height * 0.2
    
    # ID sırasına göre döndür (1, 2, 3)
    return [(cx, cy), (p1x, p1y), (p2x, p2y)]

def _star_edges(n: int):
    """Merkezden (1) diğerlerine (2, 3) giden kenarları oluşturur."""
    # [(1, 2), (1, 3)]
    return [{'source': 1, 'target': i} for i in range(2, n + 1)]

def network_vars(player: Player):
    """HTML'de SVG çizimi için gerekli star ağı değişkenlerini hazırlar."""
    n = C.PLAYERS_PER_GROUP
    you_id = player.id_in_group # Kendi ID'si
    
    coords = _star_coords(n)
    nodes = []
    for i in range(1, n + 1):
        nodes.append(dict(
            id=i, # Düğüm ID'si (1, 2, 3) - TUTARLILIK
            x=round(coords[i - 1][0], 2),
            y=round(coords[i - 1][1], 2),
            is_you=(i == you_id),
            role='center' if i == 1 else 'periphery' # Düğümün rolü
        ))

    edges = _star_edges(n) # [{'source': 1, 'target': 2}, ...] - TUTARLILIK

    return dict(
        you_id=you_id,
        nodes=nodes,
        edges=edges
        # Komşu ID'lerini ayrıca göndermeye gerek yok, JS'den bulunabilir
    )
# --- Bitiş: Ağ Görselleştirme Fonksiyonları ---


class Consent(Page):
    form_model = 'player'
    form_fields = ['consent_given']
    
    def is_displayed(self): 
        return self.player.round_number == 1
        
    def vars_for_template(self):
        # HTML'in ihtiyaç duyduğu değişkenleri buraya ekliyoruz
        return dict(
            participation_bonus=self.session.config.get('participation_fee', 0),
            
            # HTML'in ihtiyaç duyduğu YENİ değişkenler
            num_rounds=C.NUM_ROUNDS,
            group_size=C.PLAYERS_PER_GROUP,
            endowment=C.ENDOWMENT, # models.py'de cu() ise .to_real_world_currency() gerekebilir
            beta=C.BETA,
            rate=self.session.config.get('real_world_currency_per_point', C.CONVERSION_RATE)
        )

class Instructions(Page):
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        p = self.player

        # --- çekirdek parametreler (template’te kesin kullanılıyor) ---
        group_size = C.PLAYERS_PER_GROUP
        num_rounds = C.NUM_ROUNDS
        endowment = C.ENDOWMENT_INT
        beta = C.BETA

        participation_bonus = self.session.config.get('participation_fee', 0)
        rate = self.session.config.get('real_world_currency_per_point', C.CONVERSION_RATE)

        # rol / komşuluk
        network_role = p.network_role
        degree = p.degree
        neighborhood_size = 3 if network_role == 'center' else 2

        # mpcr
        mpcr_center = beta / 3
        mpcr_periphery = beta / 2

        # network çizimi
        nv = network_vars(p)  # nodes/edges/neighborhood_size döndürüyor olabilir; biz yine garanti ediyoruz

        # --- examples (silme; her zaman üret) ---
        examples = {}

        # Senaryo 1: herkes 10
        ex1_keep = endowment - 10
        ex1_pay_c = ex1_keep + (mpcr_center * 30)      # center neigh size 3 => sum=30
        ex1_pay_p = ex1_keep + (mpcr_periphery * 20)   # periphery neigh size 2 => sum=20
        examples.update(dict(
            ex1_pay_c_str=f"{ex1_pay_c:.2f}",
            ex1_pay_p_str=f"{ex1_pay_p:.2f}",
        ))

        # Senaryo 2: herkes 0
        ex2_pay = endowment
        examples.update(dict(
            ex2_pay_c_str=f"{ex2_pay:.2f}",
            ex2_pay_p_str=f"{ex2_pay:.2f}",
        ))

        # Senaryo 3: siz 0, komşular 10
        ex3_keep = endowment
        ex3_pay_c = ex3_keep + (mpcr_center * 20)      # center: 0 + 10 + 10 = 20
        ex3_pay_p = ex3_keep + (mpcr_periphery * 10)   # periphery: 0 + 10 = 10
        examples.update(dict(
            ex3_pay_c_str=f"{ex3_pay_c:.2f}",
            ex3_pay_p_str=f"{ex3_pay_p:.2f}",
        ))

        # Senaryo 4: siz 10, komşular 0
        ex4_keep = endowment - 10
        ex4_pay_c = ex4_keep + (mpcr_center * 10)
        ex4_pay_p = ex4_keep + (mpcr_periphery * 10)
        examples.update(dict(
            ex4_pay_c_str=f"{ex4_pay_c:.2f}",
            ex4_pay_p_str=f"{ex4_pay_p:.2f}",
        ))

        # --- template’e giden TEK ve GARANTİLİ context ---
        ctx = dict(
            # template header pill’leri
            group_size=group_size,
            num_rounds=num_rounds,
            endowment=endowment,
            beta=beta,

            participation_bonus=participation_bonus,
            rate=rate,

            # rol bilgileri
            my_role=network_role,
            network_role=network_role,
            degree=degree,
            my_id=p.id_in_group,

            # komşuluk
            neighborhood_size=neighborhood_size,

            # mpcr
            mpcr_center_str=f"{mpcr_center:.2f}",
            mpcr_periphery_str=f"{mpcr_periphery:.2f}",

            # svg
            nodes=nv.get('nodes', []),
            edges=nv.get('edges', []),
        )

        # network_vars ekstra bir şey dönüyorsa (zararsız) ekle
        ctx.update(nv)

        # örnekler (silme)
        ctx.update(examples)

        return ctx


class Contribution(Page):
    form_model = 'player'
    form_fields = ['contribution']

    def vars_for_template(self):
        player = self.player

        # Rol bazlı MPCR
        mpcr_center = C.BETA / 3
        mpcr_periphery = C.BETA / 2

        # ✅ bu sayfada kullanılacak mpcr_str (rolüne göre)
        my_role = player.network_role  # 'center' veya 'periphery' (sende bu var)
        if my_role == 'center':
            mpcr_str = f"{mpcr_center:.2f}"
        else:
            mpcr_str = f"{mpcr_periphery:.2f}"

        # ✅ kimlik / komşular
        n = C.PLAYERS_PER_GROUP
        you_idx = player.id_in_group

        # Star'da merkez genelde id=1 olarak kurgulanır.
        # network_vars(player) içinden "center_id" gibi bir şey geliyorsa onu kullanmak daha garanti olur.
        # Şimdilik standart varsayım: merkez = 1
        center_id = 1

        if you_idx == center_id:
            # merkez: iki komşu = çevreler (2 ve 3)
            left_idx = 2
            right_idx = 3 if n >= 3 else 2
        else:
            # çevre: tek komşu = merkez
            left_idx = center_id
            right_idx = center_id  # UI'da "Komşu 2" boş kalmasın diye aynı gösteriyoruz

        return dict(
            round_num=player.round_number,
            endowment=C.ENDOWMENT,
            beta=C.BETA,
            degree=player.degree,  # Merkez: 2, Çevre: 1

            # ✅ template'te beklenenler
            group_size=n,
            you_idx=you_idx,
            left_idx=left_idx,
            right_idx=right_idx,
            my_role=my_role,              # JS rol etiketi için
            network_role=my_role,         # sende zaten var; dursun
            mpcr_str=mpcr_str,            # template'teki {{ mpcr_str }} için

            # mevcutlerin aynen kalsın
            mpcr_center_str=f"{mpcr_center:.2f}",
            mpcr_periphery_str=f"{mpcr_periphery:.2f}",

            contribution=player.field_maybe_none('contribution') or 0,

            **network_vars(player),
        )


class WaitForAll(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.set_payoffs() # models.py'daki star set_payoffs'u çağırır

    def vars_for_template(self):
        player = self.player
        return dict(
            round_num=player.round_number,
            num_rounds=C.NUM_ROUNDS,
            # Ağ görselleştirmesi için
            **network_vars(player) 
        )

class Results(Page):
    def vars_for_template(self):
        player = self.player
        rate = self.session.config.get('real_world_currency_per_point', C.CONVERSION_RATE)

        rounds_data = player.in_all_rounds()
        cols = []
        cum_payoff_so_far = cu(0)

        # --- her tur için tablo kolonu üret ---
        for p_round in rounds_data:
            your_c = p_round.contribution if p_round.contribution is not None else 0

            closed_players = p_round.get_closed_neighborhood()
            neigh_size = len(closed_players)
            if neigh_size == 0:
                continue

            total_c = sum(
                (q.contribution if q.contribution is not None else 0)
                for q in closed_players
            )
            others_c = total_c - your_c

            mpcr = C.BETA / neigh_size

            endowment = C.ENDOWMENT  # cu
            keep = endowment - cu(your_c)

            payoff = p_round.payoff if p_round.payoff is not None else cu(0)

            public_return = cu(mpcr * total_c)

            cum_payoff_so_far += payoff

            cols.append(dict(
                round_num=p_round.round_number,
                endowment=endowment,
                your_contribution=your_c,
                keep=keep,

                others_contribution=others_c,
                total_contribution=total_c,

                beta=C.BETA,
                neighborhood_size=neigh_size,

                mpcr_str=f"{mpcr:.2f}",
                public_return_str=f"{public_return:.2f}",

                payoff_str=f"{payoff:.2f}",
                payoff_tl_str=f"{(payoff * rate):.2f}",

                cum_payoff_str=f"{cum_payoff_so_far:.2f}",
            ))

        # --- bu turun kapalı komşuluk bilgileri (özet + hesap paneli) ---
        closed_now = player.get_closed_neighborhood()
        neigh_size_now = len(closed_now)
        neigh_total_now = sum((q.contribution if q.contribution is not None else 0) for q in closed_now)

        neigh_nodes = []
        for q in closed_now:
            neigh_nodes.append(dict(
                idx=q.id_in_group,
                contribution=(q.contribution if q.contribution is not None else 0),
                is_you=(q.id_in_group == player.id_in_group),
            ))

        # --- doğal dil cümlesi ---
        sentence = "Henüz tamamlanmış tur bulunmamaktadır."
        if cols:
            last = cols[-1]
            sentence = (
                f"Bu turda {last['your_contribution']} jeton katkı yaptınız; "
                f"kapalı komşuluğunuzdaki (siz dahil {last['neighborhood_size']} kişi) toplam katkı "
                f"{last['total_contribution']} jeton oldu. "
                f"Bu toplama karşılık gelen MPCR ({last['mpcr_str']}) ile hesaplanan geri dönüş "
                f"{last['public_return_str']} jeton oldu. "
                f"Sizde kalan {last['keep']} jeton ile birlikte bu tur toplam kazancınız "
                f"{last['payoff_str']} jeton (≈ {last['payoff_tl_str']} TL)."
            )

        # --- TÜM GRUP NODE KATKILARI (3 kişi hep görünsün) ---
        all_nodes = []
        for q in player.group.get_players():
            all_nodes.append(dict(
                idx=q.id_in_group,
                contribution=(q.contribution if q.contribution is not None else 0),
                is_you=(q.id_in_group == player.id_in_group),
                role=q.network_role,
            ))

        # --- Instruction ile aynı görsel için nodes/edges ---
        nv = network_vars(player)  # {nodes:[...], edges:[...], ...} bekleniyor

        return dict(
            num_rounds=C.NUM_ROUNDS,
            round_num=player.round_number,
            rate=rate,

            cols=cols,
            this_round_sentence=sentence,

            # rol
            network_role=player.network_role,

            # kapalı komşuluk paneli (hesap)
            neigh_total_contribution=neigh_total_now,
            neigh_size=neigh_size_now,
            neigh_nodes=neigh_nodes,   # istersen bunu HTML'de kullanmayacaksın artık

            # ✅ TAM AĞ GÖRSELİ (3 node) — instruction ile aynı
            nodes=nv.get('nodes', []),
            edges=nv.get('edges', []),
            my_id=player.id_in_group,

            # ✅ Node katkıları listesi (3 kişi)
            all_nodes=all_nodes,
        )


class FinalResults(Page):
    def is_displayed(self):
        return self.player.round_number == C.NUM_ROUNDS

    def vars_for_template(self):
        player = self.player
        rate = self.session.config.get('real_world_currency_per_point', C.CONVERSION_RATE)
        participation_bonus = self.session.config.get('participation_fee', 0)

        # -----------------------------
        # 1) Turlar tablosu için COLS
        # -----------------------------
        cols = []
        cum_payoff_so_far = cu(0)

        for p_round in player.in_all_rounds():
            your_c = p_round.contribution if p_round.contribution is not None else 0

            closed_players = p_round.get_closed_neighborhood()
            neighborhood_size = len(closed_players)
            if neighborhood_size == 0:
                continue

            total_c = sum(
                (q.contribution if q.contribution is not None else 0)
                for q in closed_players
            )

            mpcr = C.BETA / neighborhood_size
            keep = C.ENDOWMENT - cu(your_c)

            payoff = p_round.payoff if p_round.payoff is not None else cu(0)
            public_return = cu(mpcr * total_c)

            cum_payoff_so_far += payoff

            cols.append(dict(
                round_num=p_round.round_number,
                your_contribution=your_c,
                total_contribution=total_c,
                keep=keep,
                public_return_str=f"{public_return:.2f}",
                payoff_str=f"{payoff:.2f}",
                cum_payoff_str=f"{cum_payoff_so_far:.2f}",
            ))

        # ----------------------------------------
        # 2) Toplam oyun kazancı / toplam ödeme
        # ----------------------------------------
        total_payoff_from_game = sum(
            p.payoff for p in player.in_all_rounds()
            if p.payoff is not None
        )

        total_tokens = total_payoff_from_game
        total_tl_from_game = total_tokens * rate
        grand_total_tl = total_tl_from_game + participation_bonus

        # ----------------------------------------
        # 3) retained_amount (HTML'de kullanılıyor)
        # ----------------------------------------
        retained_amount = player.participant.vars.get('retained_amount', 0)

        return dict(
            participant_code=player.participant.code,
            num_rounds=C.NUM_ROUNDS,
            rate=rate,
            endowment=C.ENDOWMENT,

            # ✅ FinalResults.html için gerekli tablo verisi
            cols=cols,

            # özetler
            total_tokens_str=f"{total_tokens:.2f}",
            total_tl_from_game_str=f"{total_tl_from_game:.2f}",
            participation_bonus_str=f"{participation_bonus:.2f}",
            grand_total_tl_str=f"{grand_total_tl:.2f}",

            # HTML'de var diye güvenli gönderiyoruz
            retained_amount=retained_amount,

            # opsiyonel
            network_role=player.network_role,
        )


# 8. Demographics 
class Demographics(Page):
    form_model = 'player'
    form_fields = [
        'age','gender','field_of_study','year_of_study',
        'cgpa','monthly_income','risk_attitude',
    ]
    def is_displayed(self): 
        return self.player.round_number == C.NUM_ROUNDS
    
    
class AltruismMeasure(Page):
    def is_displayed(self):
        return self.player.round_number == C.NUM_ROUNDS    
    form_model = 'player'
    form_fields = (
        ['svo_a1', 'svo_a2', 'svo_a3']
        + [f'pt_b{i}' for i in range(1, 11)]
        + ['alt_c1', 'alt_c2']
    )
    

# 9. ThankYou 
class ThankYou(Page):
    def is_displayed(self): 
        return self.player.round_number == C.NUM_ROUNDS

# --- Sayfa Sırası 
page_sequence = [
    Consent,
    Instructions,
    Contribution,
    WaitForAll,
    Results,
    FinalResults,
    Demographics,
    AltruismMeasure,
    ThankYou,
]