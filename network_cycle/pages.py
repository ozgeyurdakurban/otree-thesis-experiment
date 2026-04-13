# network_cycle/pages.py (DÜZELTİLMİŞ VE TAM HALİ)
from otree.api import *
from .models import C, Player, Group
from math import cos, sin, pi # Ağ görselleştirmesi için

# --- Ağ Görselleştirmesi için Yardımcı Fonksiyonlar ---
# (Bunlar Cycle'a özgüdür ve n=3 için tasarlanmıştır)

def _cycle_edges(n: int):
    """(1,2), (2,3), ..., (n,1) kenarlarını oluşturur."""
    edges = []
    for i in range(1, n + 1):
        source = i
        target = (i % n) + 1
        edges.append((source, target))
    return edges

def _regular_polygon_coords(n: int, r: float = 120.0, cx: float = 150.0, cy: float = 150.0):
    """Düzgün çokgen (n-gen) koordinatlarını hesaplar."""
    coords = []
    for k in range(n):
        # Açıları düzgün çokgen oluşturacak şekilde hesapla
        # -pi / 2 ekleyerek ilk noktanın (id=1) üste gelmesini sağlıyoruz
        theta = 2 * pi * k / n - pi / 2
        x = cx + r * cos(theta)
        y = cy + r * sin(theta)
        coords.append((x, y))
    return coords

def network_vars(player: Player):
    """HTML'de SVG çizimi için gerekli ağ değişkenlerini hazırlar."""
    n = C.PLAYERS_PER_GROUP
    you_idx = player.id_in_group
    
    # Modelden komşu ID'lerini al
    neighbor1_id = player.field_maybe_none('neighbor1_id_in_group')
    neighbor2_id = player.field_maybe_none('neighbor2_id_in_group')

    # Düğümleri (node) oluştur
    coords = _regular_polygon_coords(n)
    nodes = []
    for i in range(1, n + 1):
        nodes.append(dict(
            id=i, # Düğüm ID'si (1, 2, 3)
            x=round(coords[i - 1][0], 2), # X koordinatı
            y=round(coords[i - 1][1], 2), # Y koordinatı
            is_you=(i == you_idx) # Bu düğüm siz misiniz?
        ))

    # Kenarları (edge) oluştur
    edges = []
    raw_edges = _cycle_edges(n)
    for u, v in raw_edges:
         # Kenarları source/target formatında listeye ekle
         edges.append(dict(source=u, target=v))

    return dict(
        you_id=you_idx, # Sizin ID'niz
        neighbor1_id=neighbor1_id, # Komşu 1'in ID'si
        neighbor2_id=neighbor2_id, # Komşu 2'nin ID'si
        nodes=nodes, # Düğümlerin listesi (koordinatlar vb.)
        edges=edges # Kenarların listesi
    )
# --- Bitiş: Ağ Görselleştirme Fonksiyonları ---


# --- Sayfalar ---

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent_given']
    
    def is_displayed(self): 
        return self.player.round_number == 1
        
    def vars_for_template(self):
        return dict(
            participation_bonus=self.session.config.get('participation_fee', 0),
        )
    

class Instructions(Page):
    def is_displayed(self):
        return self.player.round_number == 1

    def vars_for_template(self):
        player = self.player
        group = player.group 
        group_size = C.PLAYERS_PER_GROUP
        # Cycle'da kapalı komşuluk boyutu (n=3)
        neighborhood_size = C.PLAYERS_PER_GROUP
        #  MPCR (Payoff kuralı için)
        mpcr = C.BETA / neighborhood_size
  
        # --- ÖRNEKLER       


        # Örnek 1: Herkes (3 kişi) 10 Katkı Yaparsa
        ex1_c = 10
        ex1_neighborhood_sum = ex1_c * neighborhood_size # 3 * 10 = 30
        ex1_keep = C.ENDOWMENT - ex1_c
        ex1_public_return = mpcr * ex1_neighborhood_sum # (1.2/3) * 30 = 12
        ex1_payoff = ex1_keep + ex1_public_return # 5 + 12 = 17

        # Örnek 2: Herkes (3 kişi) 0 Katkı Yaparsa
        ex2_c = 0
        ex2_neighborhood_sum = ex2_c * neighborhood_size # 0
        ex2_keep = C.ENDOWMENT - ex2_c
        ex2_public_return = mpcr * ex2_neighborhood_sum # 0
        ex2_payoff = ex2_keep + ex2_public_return # 15 + 0 = 15

        # Örnek 3: Siz 0, Diğerleri (2 komşu) 10 Katkı Yaparsa
        ex3_c = 0
        ex3_others_c = 10
        # Sizin komşuluğunuzdaki toplam = 0 (siz) + 10 (komşu 1) + 10 (komşu 2) = 20
        ex3_neighborhood_sum = ex3_c + (neighborhood_size - 1) * ex3_others_c 
        ex3_keep = C.ENDOWMENT - ex3_c
        ex3_public_return = mpcr * ex3_neighborhood_sum # (1.2/3) * 20 = 8
        ex3_payoff = ex3_keep + ex3_public_return # 15 + 8 = 23

        # Örnek 4: Siz 10, Diğerleri (2 komşu) 0 Katkı Yaparsa
        ex4_c = 10
        ex4_others_c = 0
        # Sizin komşuluğunuzdaki toplam = 10 (siz) + 0 (komşu 1) + 0 (komşu 2) = 10
        ex4_neighborhood_sum = ex4_c + (neighborhood_size - 1) * ex4_others_c 
        ex4_keep = C.ENDOWMENT - ex4_c
        ex4_public_return = mpcr * ex4_neighborhood_sum # (1.2/3) * 10 = 4
        ex4_payoff = ex4_keep + ex4_public_return # 5 + 4 = 9

        return dict(
            num_rounds=C.NUM_ROUNDS,
            endowment=C.ENDOWMENT,
            participation_bonus=self.session.config.get('participation_fee', 0),
            rate=self.session.config.get('real_world_currency_per_point', C.CONVERSION_RATE),
            beta=C.BETA,
            group_size=group_size,
            neighborhood_size=neighborhood_size, 
            mpcr_str=f"{mpcr:.2f}", 

            # Örnek değişkenleri
            ex1_c=ex1_c,
            ex1_neighborhood_sum=ex1_neighborhood_sum,
            ex1_keep=ex1_keep,
            ex1_public_return_str=f"{ex1_public_return:.2f}",
            ex1_payoff_str=f"{ex1_payoff:.2f}",

            ex2_c=ex2_c,
            ex2_neighborhood_sum=ex2_neighborhood_sum,
            ex2_keep=ex2_keep,
            ex2_public_return_str=f"{ex2_public_return:.2f}",
            ex2_payoff_str=f"{ex2_payoff:.2f}",

            ex3_c=ex3_c,
            ex3_others_c=ex3_others_c,
            ex3_neighborhood_sum_str=f"{ex3_neighborhood_sum:.2f}", 
            ex3_keep=ex3_keep,
            ex3_public_return_str=f"{ex3_public_return:.2f}",
            ex3_payoff_str=f"{ex3_payoff:.2f}",

            ex4_c=ex4_c,
            ex4_others_c=ex4_others_c,
            ex4_neighborhood_sum_str=f"{ex4_neighborhood_sum:.2f}", 
            ex4_keep=ex4_keep,
            ex4_public_return_str=f"{ex4_public_return:.2f}",
            ex4_payoff_str=f"{ex4_payoff:.2f}",

            # Ağ görselleştirmesi için
            **network_vars(player)
        )



class Contribution(Page):
    form_model = 'player'
    form_fields = ['contribution']

    def vars_for_template(self):
        player = self.player
        neighborhood_size = C.PLAYERS_PER_GROUP  # n=3 (cycle için burada 3)
        mpcr = C.BETA / neighborhood_size

        # Cycle konum bilgileri (template'teki you_idx/left_idx/right_idx için)
        n = C.PLAYERS_PER_GROUP
        you_idx = player.id_in_group
        left_idx = you_idx - 1 if you_idx > 1 else n
        right_idx = you_idx + 1 if you_idx < n else 1

        return dict(
            round_num=player.round_number,
            endowment=C.ENDOWMENT,
            beta=C.BETA,
            degree=player.degree,  # Bu 2 olmalı
            mpcr_str=f"{mpcr:.2f}",  
            group_size=C.PLAYERS_PER_GROUP,
            # contribution (IntegerField, None ise 0)
            contribution=player.field_maybe_none('contribution') or 0,
            neighborhood_size=neighborhood_size,  

            #  ağ konumu kartı + mini-cycle etiketi için
            you_idx=you_idx,
            left_idx=left_idx,
            right_idx=right_idx,


            # Ağ görselleştirmesi için
            **network_vars(player),
        )


class WaitForAll(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.set_payoffs() # models.py'daki network set_payoffs'u çağırır

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

        rounds = player.in_all_rounds()
        table_cols = []
        cum_payoff = 0

        # defaultlar (template asla patlamasın)
        neigh_nodes = []
        neigh_size = C.PLAYERS_PER_GROUP
        neigh_total_contribution = 0

        for rp in rounds:
            your_c = rp.contribution or 0

            try:
                neigh_players = rp.get_closed_neighborhood()
                neighborhood_size = len(neigh_players) or C.PLAYERS_PER_GROUP
                total_c = sum((pl.contribution or 0) for pl in neigh_players)
                others_c = total_c - your_c
            except Exception:
                neigh_players = []
                neighborhood_size = C.PLAYERS_PER_GROUP
                total_c = your_c
                others_c = 0

            mpcr = (C.BETA / neighborhood_size) if neighborhood_size > 0 else 0
            keep = C.ENDOWMENT - your_c
            public_return = mpcr * total_c

            payoff = rp.payoff or 0
            cum_payoff += payoff

            table_cols.append(dict(
                round_num=rp.round_number,
                endowment=C.ENDOWMENT,
                your_contribution=your_c,
                others_contribution=others_c,
                total_contribution=total_c,
                mpcr=mpcr,
                mpcr_str=f"{mpcr:.2f}",
                keep=keep,
                public_return=public_return,
                public_return_str=f"{public_return:.2f}",
                payoff=payoff,
                payoff_str=f"{payoff:.2f}",
                payoff_tl=payoff * rate,
                payoff_tl_str=f"{payoff * rate:.2f}",
                cum_payoff=cum_payoff,
                cum_payoff_str=f"{cum_payoff:.2f}",
                neighborhood_size=neighborhood_size,
                beta=C.BETA,
            ))

            # SADECE mevcut round için neigh_* üret (Results sayfasında gösterilecek olan)
            if rp.round_number == player.round_number:
                neigh_size = neighborhood_size
                neigh_total_contribution = total_c

                if neigh_players:
                    tmp = []
                    for pl in neigh_players:
                        tmp.append(dict(
                            idx=pl.id_in_group,
                            contribution=(pl.contribution or 0),
                            is_you=(pl.id_in_group == player.id_in_group),
                        ))
                    tmp.sort(key=lambda x: x["idx"])
                    neigh_nodes = tmp
                else:
                    neigh_nodes = [dict(idx=player.id_in_group, contribution=your_c, is_you=True)]

        sentence = "Henüz tamamlanmış tur bulunmamaktadır."
        if table_cols:
            last = table_cols[-1]
            sentence = (
                f"Bu turda {last['your_contribution']} jeton katkı yaptınız; "
                f"kapalı komşuluğunuzdaki (siz dahil {last['neighborhood_size']} kişi) toplam katkı {last['total_contribution']} jeton oldu. "
                f"Toplam katkı MPCR={last['mpcr_str']} ile çarpılarak size {last['public_return_str']} jetonluk bir geri dönüş sağladı. "
                f"Sizde kalan {last['keep']} jeton ile birlikte bu tur toplam kazancınız {last['payoff_str']} jeton (≈ {last['payoff_tl_str']} TL)."
            )

        return dict(
            num_rounds=C.NUM_ROUNDS,
            round_num=player.round_number,
            rate=rate,
            cols=table_cols,
            this_round_sentence=sentence,

            # ✅ template’in istediği isimlerle
            neigh_nodes=neigh_nodes,
            neigh_size=neigh_size,
            neigh_total_contribution=neigh_total_contribution,

            # varsa aynı kalsın
            beta=C.BETA,
            group_size=C.PLAYERS_PER_GROUP,

            **network_vars(player),
        )



class FinalResults(Page):
    def is_displayed(self):
        return self.player.round_number == C.NUM_ROUNDS

    def vars_for_template(self):
        player = self.player
        rate = self.session.config.get('real_world_currency_per_point', C.CONVERSION_RATE)
        participation_bonus = self.session.config.get('participation_fee', 0)

        rounds = player.in_all_rounds()
        cols = []
        cum_payoff = 0

        # Network (son tur, kapalı komşuluk) defaultlar
        neigh_nodes = []
        neigh_size = C.PLAYERS_PER_GROUP
        neigh_total_contribution = 0

        for rp in rounds:
            your_c = rp.contribution or 0

            # kapalı komşuluk toplamı (siz + iki komşu)
            try:
                neigh_players = rp.get_closed_neighborhood()
                neighborhood_size = len(neigh_players) or C.PLAYERS_PER_GROUP
                total_c = sum((pl.contribution or 0) for pl in neigh_players)
                others_c = total_c - your_c
            except Exception:
                neigh_players = []
                neighborhood_size = C.PLAYERS_PER_GROUP
                total_c = your_c
                others_c = 0

            mpcr = (C.BETA / neighborhood_size) if neighborhood_size > 0 else 0
            keep = C.ENDOWMENT - your_c

            public_return = mpcr * total_c
            payoff = rp.payoff or 0
            cum_payoff += payoff

            # Tablo kolonları (FinalResults.html ile uyumlu alan isimleri)
            cols.append(dict(
                round_num=rp.round_number,
                endowment=C.ENDOWMENT,
                your_contribution=your_c,
                others_contribution=others_c,
                total_contribution=total_c,
                neighborhood_size=neighborhood_size,
                beta=C.BETA,
                mpcr=mpcr,
                mpcr_str=f"{mpcr:.2f}",

                keep=keep,

                public_return=public_return,
                # ✅ jetonlar küsürsüz
                public_return_str=str(int(round(public_return))),

                payoff=payoff,
                payoff_str=str(int(round(payoff))),

                payoff_tl=payoff * rate,
                payoff_tl_str=str(int(round(payoff * rate))),

                cum_payoff=cum_payoff,
                cum_payoff_str=str(int(round(cum_payoff))),
            ))

            # Son tur için network değişkenleri (FinalResults sayfasında gösterilecek)
            if rp.round_number == C.NUM_ROUNDS:
                neigh_size = neighborhood_size
                neigh_total_contribution = total_c

                if neigh_players:
                    tmp = []
                    for pl in neigh_players:
                        tmp.append(dict(
                            idx=pl.id_in_group,
                            contribution=(pl.contribution or 0),
                            is_you=(pl.id_in_group == player.id_in_group),
                        ))
                    tmp.sort(key=lambda x: x["idx"])
                    neigh_nodes = tmp
                else:
                    neigh_nodes = [dict(
                        idx=player.id_in_group,
                        contribution=your_c,
                        is_you=True
                    )]

        # Oyun toplam kazancı (en güvenli: payoff'lardan)
        total_payoff_from_game = sum((p.payoff or 0) for p in rounds)
        total_tokens = total_payoff_from_game
        total_tl_from_game = total_tokens * rate
        grand_total_tl = total_tl_from_game + participation_bonus

        # Eğer FinalResults.html’de retained_amount kullanıyorsan:
        # config’te yoksa 0 döner (template patlamaz).
        retained_amount = self.session.config.get('retained_amount', 0)

        return dict(
            participant_code=player.participant.code,
            num_rounds=C.NUM_ROUNDS,
            rate=rate,
            cols=cols,

            # ödeme alanları (küsürsüz istersen int-round)
            total_tokens_str=str(int(round(total_tokens))),
            total_tl_from_game_str=str(int(round(total_tl_from_game))),
            participation_bonus_str=str(int(round(participation_bonus))),
            grand_total_tl_str=str(int(round(grand_total_tl))),
            retained_amount=str(int(round(retained_amount))),

            # ✅ FinalResults.html network alanları
            neigh_nodes=neigh_nodes,
            neigh_size=neigh_size,
            neigh_total_contribution=neigh_total_contribution,
        )


class Demographics(Page):
    form_model = 'player'
    form_fields = [
        'age',
        'gender',
        'field_of_study',
        'year_of_study',
        'cgpa',
        'monthly_income',
        'risk_attitude',
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
    
class ThankYou(Page):
    def is_displayed(self): 
        return self.player.round_number == C.NUM_ROUNDS

# --- Sayfa Sırası (Control ile aynı) ---
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