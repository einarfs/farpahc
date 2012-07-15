node: IP*

copy_corpus: t

define: def/ICE.def

query: (IP-IMP* iDoms {1}VBP*|VBD*|DOP*|DOD*|MDP*|MDD*|RDP*|RDD*|BEP*|BED*|HVP*|HVD*)

add_leaf_before{1}: (CODE *ZZZ_BAD_IMPERATIVE*)
