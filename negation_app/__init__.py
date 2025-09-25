from otree.api import *
import random
import json



doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'negation_app'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 10
    COST = 2
    INVALID_REWARD = 0
    SHOW_UP_FEE = 10


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    valid_no = models.IntegerField()
    valid_actions = models.StringField()
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

# functions
def creating_session(subsession):
    if subsession.round_number == 1:
        subsession.group_randomly()
    else:
        subsession.group_like_round(1)
    for i in subsession.get_players():
        i.prob_5 = subsession.session.config['prob_5']
        if i.id_in_group == 1:
            i.type = "Sender"
        else:
            i.type = "Receiver"
        if i.round_number >= 2:
            i.play_round_number = i.round_number - 1


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
            num_groups = int(player.session.num_participants/2)
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
            valid = random.sample(letters, group.valid_no)
            valid_sorted = sorted(valid)
            group.valid_actions = json.dumps(valid_sorted)
        else:
            group.valid_no = 2
            valid = random.sample(letters, group.valid_no)
            valid_sorted = sorted(valid)
            group.valid_actions = json.dumps(valid_sorted)

class Sender(Page):
    form_model = "group"
    form_fields = ["message"]

    def vars_for_template(player: Player):
        group = player.group
        return dict(
            valid_actions = ", ".join(json.loads(group.valid_actions)),
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
            possible_rewards = json.loads(group.possible_rewards)
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
            player.payoff = group.reward - group.message_cost


class Results(Page):
    def before_next_page(player: Player, timeout_happened):
        if player.round_number == C.NUM_ROUNDS:
            participant = player.participant
            selected_rounds = random.sample(range(2, C.NUM_ROUNDS + 1), 2)
            participant.selected_rounds = [selected_rounds[0]-1, selected_rounds[1]-1]
            p1 = player.in_round(selected_rounds[0]).payoff
            p2 = player.in_round(selected_rounds[1]).payoff
            participant.selected_payoffs = [p1, p2]
            participant.payoff = max(p1, p2) + C.SHOW_UP_FEE

    def vars_for_template(player: Player):
        group = player.group
        return dict(
            valid_actions = ", ".join(json.loads(group.valid_actions)),
            possible_rewards=json.loads(group.possible_rewards)
        )

class FinalPayoff(Page):
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Instructions, StartWaitPage, Sender, ReceiverWaitPage, Receiver, ResultsWaitPage, Results, FinalPayoff]
