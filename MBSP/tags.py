#### MEMORY BASED SHALLOW PARSER ######################################################################

# Copyright (c) 2003-2010 University of Antwerp, Belgium and Tilburg University, The Netherlands
# Vincent Van Asch <vincent.vanasch@ua.ac.be>, Tom De Smedt <tom@organisms.be>
# License: GNU General Public License, see LICENSE.txt

### TAGS #############################################################################################
# Penn Treebank II part-of-speech tags.
# The purpose of MBSP is to assign tags to words ("tokens") in a sentence.
# The tags have a standardized format and summarize information about the word's role in the sentence.
# A description and an example for each part-of-speech tag used in tagging and chunking:

word_tags = {
    "CC"   : ("conjunction, coordinating", "and, or, but"),
    "CD"   : ("cardinal number", "five, three, 13%"),
    "DT"   : ("determiner", "the, a, these"),
    "EX"   : ("existential there", "there were six boys"),
    "FW"   : ("foreign word", "mais"),
    "IN"   : ("conjunction, subordinating or preposition", "of, on, before, unless"),
    "JJ"   : ("adjective", "nice, easy, boring"),
    "JJR"  : ("adjective, comparative", "nicer, easier, more boring"),
    "JJS"  : ("adjective, superlative", "nicest, easiest, most boring"),
    "LS"   : ("list item marker", ""),
    "MD"   : ("verb, modal auxillary", "may, should, wouldn't"),
    "NN"   : ("noun, singular or mass", "tiger, chair, laughter"),
    "NNS"  : ("noun, plural", "tigers, chairs, insects"),
    "NNP"  : ("noun, proper singular", "Germany, God, Alice"),
    "NNPS" : ("noun, proper plural", "we met two Christmases ago"),
    "PDT"  : ("predeterminer", "both his children"),
    "PRP"  : ("pronoun, personal", "me, you, it"),
    "PRP$" : ("pronoun, possessive", "my, your, our"),
    "RB"   : ("adverb", "extremely, loudly, hard"),
    "RBR"  : ("adverb, comparative", "better"),
    "RBS"  : ("adverb, superlative", "best"),
    "RP"   : ("adverb, particle", "about, off, up"),
    "SYM"  : ("symbol", "%"),
    "TO"   : ("infinitival to", "what to do?"),
    "UH"   : ("interjection", "oh, oops, gosh"),
    "VB"   : ("verb, base form", "think"),
    "VBZ"  : ("verb, 3rd person singular present", "she thinks"),
    "VBP"  : ("verb, non-3rd person singular present", "I think"),
    "VBD"  : ("verb, past tense", "they talked"),
    "VBN"  : ("verb, past participle", "a sunken ship"),
    "VBG"  : ("verb, gerund or present participle", "programming is fun"),
    "WDT"  : ("wh-determiner", "which, whatever, whichever"),
    "WP"   : ("wh-pronoun, personal", "what, who, whom"),
    "WP$"  : ("wh-pronoun, possessive", "whose, whosever"),
    "WRB"  : ("wh-adverb", "where, when"),
    "."    : ("punctuation mark, sentence closer", ".;?*"),
    ","    : ("punctuation mark, comma", ","),
    ":"    : ("punctuation mark, colon", ":"),
    "("    : ("contextual separator, left paren", "("),
    ")"    : ("contextual separator, right paren", ")"),
}

chunk_tags = {
    "ADJP"   : ("adjective phrase (CC+RB+JJ)", "warm and cosy"),
    "ADVP"   : ("adverb phrase (RB)", "also"),
    "INTJ"   : ("interjection (UH)", "hello"),
    "NP"     : ("noun phrase (DT+RB+JJ+NN+PR)", "the strange bird"),
    "PP"     : ("prepositional phrase (TO+IN)", "in between"),
    "PRT"    : ("particle, category (RP)", "up the stairs"),
    "SBAR"   : ("subordinating conjunction (IN)", "while, whether, though"),
    "VP"     : ("verb phrase (RB+MD+VB)", "was looking"),
    # These are never generated by MBSP:
    "CONJP"  : ("conjunction phrase", ""),
    "FRAG"   : ("fragment", ""),
    "LST"    : ("list marker, includes surrounding punctuation", ""),
    "NAC"    : ("not a constituent; used to show the scope of certain prenominal modifiers within a NP", ""),
    "NX"     : ("used within certain complex NPs to mark the head of the NP", ""),
    "QP"     : ("quantifier phrase", ""),
    "RRC"    : ("reduced relative clause", ""),
    "UCP"    : ("unlike coordinated phrase", ""),
    "WHADJP" : ("wh-adjectival phrase containing a wh-adverb", "how hot"),
    "WHAVP"  : ("wh-adverb phrase", "how, why"),
    "WHNP"   : ("wh-noun phrase", "who, which book, whose daughter, none of which, how many leopards"),
    "WHPP"   : ("wh-prepositional phrase", "in which we trust, by whose authority"),
    "X"      : ("unknown", ""),
    # These are actually clause-level tags (http://bulba.sdsu.edu/jeanette/thesis/PennTags.html):
    "S"      : ("simple declarative clause", ""),
    "SBARQ"  : ("direct question introduced by a wh-word or a wh-phrase", ""),
    "SINV"   : ("inverted declarative sentence", ""),
    "SQ"     : ("inverted yes/no question", ""),  
}

function_tags = {
    "SBJ" : ("subject", ""),
    "OBJ" : ("object", ""),
    "PRD" : ("predicate", ""),
    "CLR" : ("closely related", ""),
    "DIR" : ("direction", "toward the exit"),
    "EXT" : ("extent"),
    "LOC" : ("location", ""),
    "PRN" : ("parenthetical", ""),
    "PRP" : ("purpose", ""),
}

def description(tag):
    """ Returns a (description, example)-tuple of the given part-of-speech tag.
    """
    tag = tag.upper()
    if tag in word_tags:
        return word_tags[tag]
    elif tag in chunk_tags:
        return chunk_tags[tag]
    elif tag in function_tags:
        return function_tags[tag]
    else:
        for k in chunk_tags.keys():
            # Find the chunk tag. 
            # We do startswith() as tags may look like "VP-1" instead of "VP".
            if tag.startswith(k):
                description, example = chunk_tags[k]
                # If the tag has an additional function (e.g. "PP-CLR" instead of "PP"), find that too.
                if len(tag) - len(k) > 3:
                    for k in function_tags.keys():
                        if k in tag:
                            description = function_tags[k][0] + " " + description
                            example = function_tags[k][1]
                            break
                return description, example
    return "", ""
