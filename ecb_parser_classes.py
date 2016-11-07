from nltk.corpus import wordnet as wn
from collections import Counter
from collections import defaultdict
import operator


def possible_meanings(lexical_expression, pos=None):
    """
    given a lemma, return possible wordnet meanings
    if there is a space in the lemma, 
    also try with '-' instead of space
    
    :param str lexical_expression: e.g. 'house' or 'check in'
    :param str pos: kwarg, part of speech (n | v is taken into account)
    :rtype: set
    :return: set of nltk.corpus.reader.wordnet.Synset instances
    """
    if all([pos is not None,
            pos not in {'n', 'v'}]):
        return []
    
    if pos is not None:
        synsets = wn.synsets(lexical_expression, pos=pos)
    else:
        synsets = wn.synsets(lexical_expression)
    
    if all([not synsets,
            ' ' in lexical_expression]):
        with_hyphen = lexical_expression.replace(' ', '-')
        if pos is not None:
            synsets = wn.synsets(with_hyphen, pos=pos)
        else:
            synsets = wn.synsets(with_hyphen)
        
    return synsets 

class EventInstance:
    def __init__(self, event_instance_el):
        self.tag_descriptor = event_instance_el.get('TAG_DESCRIPTOR')
        self.instance_id = event_instance_el.get('instance_id')
        self.xml_tag = event_instance_el.tag
        self.event_mentions = set()

    @property
    def event_triggers(self):
        return [event_mention_el.event_trigger
                for event_mention_el in self.event_mentions]

    @property
    def num_event_mentions(self):
        return len(self.event_mentions)
    
    @property
    def distr_event_mentions(self):
        return Counter(self.event_triggers)
    
    @property
    def variance(self):
        return len(set(self.event_triggers))
    
    @property
    def possible_wn_synsets(self):
        scored_meanings = defaultdict(int)
        for (lex_expr, pos), freq in self.distr_event_mentions.items(): 
            meanings = possible_meanings(lex_expr, pos)
            if meanings:
                av_score = 1 / len(meanings)
                for _ in range(freq):
                    for meaning in meanings:
                        scored_meanings[meaning] += av_score

        max_score = max(scored_meanings.values())
        return {meaning for meaning, score in scored_meanings.items()
                if score == max_score}


class EventMention:
    def __init__(self,
                 event_instance_id,
                 token_objs,
                 doc_name,
                 doc_id,
                 m_id,
                 sentence):
        self.event_instance_id = event_instance_id
        self.token_objs = token_objs
        self.doc_name = doc_name
        self.doc_id = doc_id
        self.m_id = m_id
        self.sentence = sentence

    @property
    def event_trigger(self):
        guessed_pos = self.token_objs[0].pos
        trigger = ' '.join([token_obj.lemma
                           for token_obj in self.token_objs])
        return trigger, guessed_pos


class Token:
    def __init__(self, token_el):
        self.token = token_el.text
        self.t_id = int(token_el.get('t_id'))
        self.sentence = token_el.get('sentence')
        self.number = token_el.get('number')

    def set_lemma(self, lemma):
        self.lemma = lemma

    def set_pos(self, pos):
        self.pos = pos

class EventTrigger:
    def __init__(self, event_trigger):
        self.event_trigger = event_trigger
        self.event_instances = set()

    @property
    def event_instance_ids(self):
        return {event_instance_obj.instance_id
                for event_instance_obj in self.event_instances}
    @property
    def num_event_instances(self):
        return len(self.event_instances)
    
    @property
    def wn_polysemy(self):
        synsets = wn.synsets(self.event_trigger)
        return len(synsets)
