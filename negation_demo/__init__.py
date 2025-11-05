from otree.api import *
import random
import json
import math



doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'negation_demo'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3
    COST = 4
    INVALID_REWARD = 0
    SHOW_UP_FEE = 7
    ENDOWMENT = COST * 10
    CONVERSION_RATE = 4
    table_template = __name__ + '/table.html'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    valid_no = models.IntegerField()
    valid_actions = models.StringField()
    invalid_actions = models.StringField()
    possible_rewards = models.StringField()
    message = models.StringField(blank=True)
    message_cost = models.IntegerField()
    action = models.StringField(blank=True)
    reward = models.IntegerField()

class Player(BasePlayer):
    q1 = models.IntegerField(choices=[[1, 'True'], [0, 'False']], widget=widgets.RadioSelect, label='')
    q2 = models.IntegerField(choices=[[1, 'True'], [0, 'False']], widget=widgets.RadioSelect, label='')
    q3 = models.IntegerField(choices=[[1, 'True'], [0, 'False']], widget=widgets.RadioSelect, label='')
    q4 = models.IntegerField(choices=[[1, 'True'], [0, 'False']], widget=widgets.RadioSelect, label='')
    q5 = models.IntegerField(choices=[[1, 'True'], [0, 'False']], widget=widgets.RadioSelect, label='')
    play_round_number = models.IntegerField(initial=0)
    type = models.StringField()
    prob_5 = models.FloatField()
    RA_raw_responses = models.LongStringField()
    RA_chose_safe = models.BooleanField()
    RA_won_lottery = models.BooleanField()
    RA_payoff = models.FloatField()
    Q_gender = models.IntegerField(label="<h4>1. What is your gender?</h4>",
                                   choices=[[1, "Female"], [2, "Male"],
                                            [3, "Prefer not to answer"], [4, "Other (please specify)"]],
                                   widget=widgets.RadioSelect)
    Q_gender_other = models.StringField(blank=True)
    Q_eth_amnative = models.BooleanField(label="American Indian or Alaska Native", blank=True, initial=False)
    Q_eth_asian = models.BooleanField(label="Asian", blank=True, initial=False)
    Q_eth_black = models.BooleanField(label="Black or African American", blank=True, initial=False)
    Q_eth_pacific = models.BooleanField(label="Native Hawaiian or other Pacific Islander", blank=True, initial=False)
    Q_eth_white = models.BooleanField(label="White", blank=True, initial=False)
    Q_eth_other_option = models.BooleanField(label="Other (please specify)", blank=True, initial=False)
    Q_eth_prefer_not = models.BooleanField(label="Prefer not to answer", blank=True, initial=False)
    Q_eth_other = models.StringField(label="If other, please specify:", blank=True)
    Q_native_lang = models.StringField(label="<h4>3. What is your native or first language?</h4>")
    #Q_ethnicity = models.MultipleChoiceField(label="<h4>2. What is your ethnicity (select all that apply)?</h4>",
    #                                         choices=[[1, "American Indian or Alaska Native"], [2, "Asian"],
    #                                                  [3, "Black or African American"],
    #                                                  [4, "Native Hawaiian or other Pacific Islander"], [5, "White"],
    #                                                  [6, "Other (please specify)"], [7, "Prefer not to answer"]],
    #                                         widget=widgets.RadioSelect)
    #Q_native_lang = models.IntegerField(label="<h4>3. What is your native or first language?</h4>",
    #                                  choices=[[1, "English"], [2, "Spanish"],
    #                                           [3, "Chinese (Mandarin or Cantonese)"],
    #                                           [4, "Hindi or other South Asian language"], [5, "Korean"],
    #                                           [6, "Japanese"], [7, "Arabic"], [8, "Other (please specify)"]],
    #                                  widget=widgets.RadioSelect)
    #Q_native_lang_other = models.StringField(blank=True)
    Q_year = models.IntegerField(label="<h4>4. What is your year in school?</h4>",
                                 choices=[[1, "First-year"], [2, "Sophomore"],
                                          [3, "Junior"], [4, "Senior"], [5, "Prefer not to answer"], [6, "Other (please specify)"]],
                                 widget=widgets.RadioSelect)
    Q_year_other = models.StringField(blank=True)
    Q_major_busi = models.BooleanField(blank=True, initial = False)
    Q_major_econ = models.BooleanField(blank=True, initial=False)
    Q_major_eng = models.BooleanField(blank=True, initial=False)
    Q_major_hum = models.BooleanField(blank=True, initial=False)
    Q_major_sci = models.BooleanField(blank=True, initial=False)
    Q_major_sosci = models.BooleanField(blank=True, initial=False)
    Q_major_undeclared = models.BooleanField(blank=True, initial=False)
    Q_major_prefer_not = models.BooleanField(blank=True, initial=False)
    Q_major_other_option = models.BooleanField(blank=True, initial=False)
    Q_major_other = models.StringField(blank=True)
    #Q_major = models.IntegerField(label="<h4>5. What is your major? (select all that apply)</h4>",
    #                               choices=[[1, "Business"], [2, "Economics"],
    #                                        [3, "Engineering"], [4, "Humanities"], [5, "Science"], [6, "Social Science"], [7, "Undeclared"], [8, "Prefer not to answer"], [9, "Other (please specify)"]],
    #                               widget=widgets.RadioSelect)
    Q_comments = models.LongStringField(label="<h4>6. Please share any comments about today's study. This question is optional and will not affect your payment.</h4>", blank = True)

class Trial(ExtraModel):
    player = models.Link(Player)
    lottery_high_a = models.FloatField()
    lottery_low_a = models.FloatField()
    lottery_high_b = models.FloatField()
    lottery_low_b = models.FloatField()
    probability = models.IntegerField()
    chose_safe = models.BooleanField()
    randomly_chosen = models.BooleanField(initial=False)

# functions
def read_csv():
    import csv
    import random

    f = open(__name__ + '/lottery.csv', encoding='utf8')
    rows = list(csv.DictReader(f))

    #random.shuffle(rows)
    return rows

def creating_session(subsession):
    if subsession.round_number == 1:
        subsession.group_randomly()
    else:
        subsession.group_like_round(1)
    for i in subsession.get_players():
        i.prob_5 = round(subsession.session.config['prob_5'],2)
        if i.id_in_group == 1:
            i.type = "Sender"
        else:
            i.type = "Receiver"
        if i.round_number >= 2:
            i.play_round_number = i.round_number - 1
        stimuli = read_csv()
        for stim in stimuli:
            Trial.create(player=i, **stim)


# PAGES
class Instructions(Page):
    form_model = "player"
    form_fields = ["q1", "q2", "q3", "q4", "q5"]

    @staticmethod
    def error_message(player, values):
        solutions = dict(q1=1,
                         q2=1,
                         q3=1,
                         q4=0,
                         q5=0)
        error_messages = dict()
        for field_name in solutions:
            if values[field_name] != solutions[field_name]:
                error_messages[field_name] = 'Wrong answer'
        return error_messages

    def is_displayed(player: Player):
        return player.round_number == 1

    def vars_for_template(player: Player):
        return dict(
            possible_rewards = random.sample([40,50,60,70,80,90,100], 7),
            num_playrounds = C.NUM_ROUNDS - 1,
            num_players = player.session.num_participants,
            num_groups = int(player.session.num_participants/2),
            prob_2= round(1 - player.prob_5, 2)
        )

class StartWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group:Group):
        player = group.get_players()
        letters = ['A','B','C','D','E','F','G']
        rewards = [40,50,60,70,80,90,100]
        random_rewards = random.sample(rewards, 7)
        group.possible_rewards = json.dumps(random_rewards)
        if random.random() < player[0].prob_5:
            group.valid_no=5
        else:
            group.valid_no = 2
        if player[0].round_number == 2:
            valid = ['A','B','D','E','G']
        elif player[0].round_number == 3:
            valid = ['B','C']
        else:
            valid = random.sample(letters, group.valid_no)
        valid_sorted = sorted(valid)
        group.valid_actions = json.dumps(valid_sorted)
        invalid = sorted(list(set(letters) - set(valid)))
        group.invalid_actions = json.dumps(invalid)

class Sender(Page):
    form_model = "group"
    form_fields = ["message"]

    def vars_for_template(player: Player):
        group = player.group
        return dict(
            actions = ", ".join(['A','B','C','D','E','F','G']),
            valid_actions = json.loads(group.valid_actions),
            invalid_actions = json.loads(group.invalid_actions),
            prob_2 = round(1 - player.prob_5, 2)
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.type == "Sender"

class ReceiverWaitPage(WaitPage):
    body_text = "Waiting for the Sender's message."

    def is_displayed(player: Player):
        return player.type == "Receiver"

class Receiver(Page):
    form_model = "group"
    form_fields = ["action"]

    def vars_for_template(player: Player):
        group = player.group
        return dict(
            possible_rewards = json.loads(group.possible_rewards),
            prob_2=round(1 - player.prob_5, 2)
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.type == "Receiver"


class ResultsWaitPage(WaitPage):
    body_text = "Waiting for the Receiver's action."

    @staticmethod
    def after_all_players_arrive(group: Group):
        player_list = group.get_players()
        group.message_cost = max(0, len(group.message)-1) * C.COST
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        index = letters.index(group.action)
        if group.action in json.loads(group.valid_actions):
            group.reward = json.loads(group.possible_rewards)[index]
        else:
            group.reward = C.INVALID_REWARD
        for player in player_list:
            player.payoff = C.ENDOWMENT + group.reward - group.message_cost


class Results(Page):
    #def before_next_page(player: Player, timeout_happened):
    #    if player.round_number == C.NUM_ROUNDS:
    #        participant = player.participant
    #        selected_rounds = random.sample(range(2, C.NUM_ROUNDS + 1), 2)
    #        participant.selected_rounds = [selected_rounds[0]-1, selected_rounds[1]-1]
    #        p1 = player.in_round(selected_rounds[0]).payoff
    #        p2 = player.in_round(selected_rounds[1]).payoff
    #        participant.selected_payoffs = [p1, p2]
    #        participant.highest_payoff = max(p1, p2)
    #        participant.payoff = math.ceil(participant.highest_payoff / C.CONVERSION_RATE + C.SHOW_UP_FEE)

    def vars_for_template(player: Player):
        group = player.group
        return dict(
            actions=", ".join(['A', 'B', 'C', 'D', 'E', 'F', 'G']),
            valid_actions=json.loads(group.valid_actions),
            invalid_actions=json.loads(group.invalid_actions),
            valid_actions_string=", ".join(json.loads(group.valid_actions)),
            possible_rewards=json.loads(group.possible_rewards),
            prob_2=round(1 - player.prob_5, 2)
        )

class AllGroupsWaitPage(WaitPage):
    wait_for_all_groups = True
    body_text = "Waiting for all participants to finish this round."

class Questionnaire(Page):
    form_model = 'player'
    form_fields = ['Q_gender', 'Q_gender_other', 'Q_eth_amnative', 'Q_eth_asian', 'Q_eth_black', 'Q_eth_pacific', 'Q_eth_white', 'Q_eth_other_option', 'Q_eth_prefer_not', 'Q_eth_other',
                   'Q_native_lang', 'Q_year', 'Q_year_other', 'Q_major_busi', 'Q_major_econ', 'Q_major_eng', 'Q_major_hum', 'Q_major_sci', 'Q_major_sosci', 'Q_major_undeclared', 'Q_major_other',
                   'Q_major_other_option', 'Q_major_prefer_not', 'Q_comments']

    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

class Risk_preference(Page):
    form_model = 'player'
    form_fields = ['RA_raw_responses']

    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(trials=Trial.filter(player=player))

    @staticmethod
    def before_next_page(player: Player, timeout_happened):

        trials = Trial.filter(player=player)

        responses = json.loads(player.RA_raw_responses)
        for trial in trials:
            trial.chose_safe = responses["{} - {}".format(trial.id,trial.probability)]

        trial = random.choice(trials)
        trial.randomly_chosen = True
        player.RA_chose_safe = trial.chose_safe
        if player.RA_chose_safe:
            player.RA_won_lottery = (trial.probability / 100) > random.random()
            if player.RA_won_lottery:
                RA_payoff = trial.lottery_high_a
            else:
                RA_payoff = trial.lottery_low_a
        else:
            player.RA_won_lottery = (trial.probability / 100) > random.random()
            if player.RA_won_lottery:
                RA_payoff = trial.lottery_high_b
            else:
                RA_payoff = trial.lottery_low_b
        player.RA_payoff = RA_payoff
        participant = player.participant
        selected_rounds = random.sample(range(2, C.NUM_ROUNDS + 1), 2)
        participant.selected_rounds = [selected_rounds[0] - 1, selected_rounds[1] - 1]
        p1 = player.in_round(selected_rounds[0]).payoff
        p2 = player.in_round(selected_rounds[1]).payoff
        participant.selected_payoffs = [p1, p2]
        participant.highest_payoff = max(p1, p2)
        participant.payoff = math.ceil(participant.highest_payoff / C.CONVERSION_RATE + player.RA_payoff + C.SHOW_UP_FEE)

class FinalPayoff(Page):
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    def vars_for_template(player: Player):
        selected_rounds = player.participant.vars.get("selected_rounds", [])
        trials = Trial.filter(player=player, randomly_chosen=True)


        rounds_data = []
        for p in player.in_all_rounds():
            if p.round_number > 1:
                rounds_data.append({
                    'round_number': p.round_number-1,
                    'payoff': int(p.payoff),  # removes decimals if you’re using integer points
                    'is_selected': p.round_number - 1 in selected_rounds
                })
        return dict(
            rounds_data=rounds_data,
            max_round_payoff=player.participant.payoff - player.RA_payoff - C.SHOW_UP_FEE,
            trials=trials
        )


page_sequence = [Instructions, StartWaitPage, Sender, ReceiverWaitPage, Receiver, ResultsWaitPage, Results, AllGroupsWaitPage, Questionnaire, Risk_preference, FinalPayoff]
