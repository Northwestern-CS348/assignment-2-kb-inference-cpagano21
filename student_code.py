import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################

        if isinstance(fact_or_rule, Fact):
                self.kb_remove(fact_or_rule)
        elif isinstance(fact_or_rule, Rule):
                self.kb_remove(fact_or_rule)


    def kb_remove(self, fact_or_rule):
        if fact_or_rule.supported_by:
            if fact_or_rule.asserted:
                # this must be a fact or rule that is both supported and asserted
                # therefore, must not remove from KB
                # return None
                fact_or_rule.asserted = False
                return
        if fact_or_rule.supports_facts:
            for y in fact_or_rule.supports_facts:
                y.supported_by.remove(fact_or_rule)
        if not fact_or_rule.supports_facts:
            for y in fact_or_rule.supports_facts:
                y.remove(fact_or_rule)
        if fact_or_rule.supports_rules:
            for y in fact_or_rule.supports_rules:
                y.supported_by.remove(fact_or_rule)
        if not fact_or_rule.supports_facts:
            for y in fact_or_rule.supports_facts:
                y.remove(fact_or_rule)



        

class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################

        ## 1. see if the fact statement is supported by 1+ rule through match function LHS = 0
        ## 2. if it is supported by 1 rule (len 1) then instantiate the fact to the rule
        ## 3. now there's a binding of the fact and rule, use this to create a new fact
        ## 4. if the fact statement is supported by more than 1 rule then create a new list, empty (statement =
        # instantiated list, bindings = match function)
        ## 5.
        bindings = match(fact.statement, rule.lhs[0])

        if bindings:
            supported_by_1 = [[rule, fact]]
            rhs_new = instantiate(rule.rhs, bindings)
            if len(rule.lhs) == 1:
                fact_new = Fact(rhs_new, supported_by=supported_by_1)

                kb.kb_assert(fact_new)
                rule.supports_facts.append(fact_new)
                fact.supports_facts.append(fact_new)

            else:
                lhs_new = []
                for x in rule.lhs[1: ]:
                    lhs_new.append(instantiate(x, bindings))

                rule_new = Rule([lhs_new, rhs_new], supported_by=supported_by_1)
                rule_new.supported_by = [[rule, fact]]

                kb.kb_assert(rule_new)
                fact.supports_rules.append(rule_new)
                rule.supports_rules.append(rule_new)
























