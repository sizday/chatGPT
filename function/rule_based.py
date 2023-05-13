import spacy
from spacy.matcher import Matcher
nlp = spacy.load('en_core_web_sm')


class RuleBasedExtractor:
    def __init__(self, text):
        self.text = text
        self.sentences = self._get_sentences()

    def _get_sentences(self):
        sentences = self.text.split('.')
        clear_sentences = [sent.strip() for sent in sentences if sent]
        return clear_sentences

    def get_result(self):
        results = []
        for sentence in self.sentences:
            subj, obj = self._get_entities(sentence)
            relation = self._get_relation(sentence)
            if subj and obj and relation:
                result = [subj, relation, obj]
                results.append(result)
        return results

    @staticmethod
    def _get_entities(sent):
        subj = ""
        obj = ""
        prv_tok_dep = ""  # dependency tag of previous token in the sentence
        prv_tok_text = ""  # previous token in the sentence
        prefix = ""
        modifier = ""

        for tok in nlp(sent):
            # if token is a punctuation mark then move on to the next token
            if tok.dep_ != "punct":
                # check: token is a compound word or not
                if tok.dep_ == "compound":
                    prefix = tok.text
                    # if the previous word was also a 'compound' then add the current word to it
                    if prv_tok_dep == "compound":
                        prefix = prv_tok_text + " " + tok.text

                # check: token is a modifier or not
                if tok.dep_.endswith("mod"):
                    modifier = tok.text
                    # if the previous word was also a 'compound' then add the current word to it
                    if prv_tok_dep == "compound":
                        modifier = prv_tok_text + " " + tok.text

                if tok.dep_.find("subj") != -1:
                    subj = modifier + " " + prefix + " " + tok.text
                    subj = subj.strip().replace('  ', ' ')
                    prefix = ""
                    modifier = ""

                if tok.dep_.find("obj") != -1:
                    obj = modifier + " " + prefix + " " + tok.text
                    obj = obj.strip().replace('  ', ' ')

                # update variables
                prv_tok_dep = tok.dep_
                prv_tok_text = tok.text

        return subj, obj

    @staticmethod
    def _get_relation(sent):
        doc = nlp(sent)

        # Matcher class object
        matcher = Matcher(nlp.vocab)

        # define the pattern
        pattern = [{'DEP': 'ROOT'},
                   {'DEP': 'prep', 'OP': "?"},
                   {'DEP': 'agent', 'OP': "?"},
                   {'POS': 'ADJ', 'OP': "?"}]

        matcher.add("matching_1", [pattern])

        matches = matcher(doc)
        k = len(matches) - 1

        span = doc[matches[k][1]:matches[k][2]]

        return span.text


if __name__ == "__main__":
    test_text = "Alex presents with complaint of allergies. The drawdown process is governed by astm standard d823."
    ext = RuleBasedExtractor(test_text)
    test_result = ext.get_result()
    print(test_result)
