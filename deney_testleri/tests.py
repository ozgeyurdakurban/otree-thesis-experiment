from otree.api import Bot, Submission, SubmissionMustFail
from . import *

def contrib(r, pid):
    return (r * 3 + pid * 5) % 16

class PlayerBot(Bot):
    def play_round(self):
        p = self.player
        r = p.round_number
        if r == 1:
            yield SubmissionMustFail(Consent, {})
            yield Consent, dict(consent_given=True)
        if (r - 1) % C.ROUNDS_PER_BLOCK == 0:
            t = p.group.network_type
            page = dict(control=InstructionsControl, cycle=InstructionsCycle, star=InstructionsStar)[t]
            yield page
        if r == 1:
            yield SubmissionMustFail(Contribution, dict(contribution=16))
            yield SubmissionMustFail(Contribution, dict(contribution=-1))
        yield Contribution, dict(contribution=contrib(r, p.id_in_group))
        yield Results
        if r == C.NUM_ROUNDS:
            yield Demographics, dict(age="21–23", gender="Kadın", field_of_study="Sayısal (STEM)",
                year_of_study="3. sınıf", cgpa="3.00–3.49", monthly_income="10.001–30.000 TL",
                risk_attitude="Az risk alırım")
            d = {f'pt_b{i}': 4 for i in range(1, 11)}
            d.update(charity_d1=30, alt_c1=5, alt_c2=6, svo_a1='A', svo_a2='B', svo_a3='C')
            yield SubmissionMustFail(AltruismMeasure, dict(d, charity_d1=101))
            yield AltruismMeasure, d
            yield FinalResults
            yield PaymentInfo
            yield ThankYou

