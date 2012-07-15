node: IP*

copy_corpus: t

define: def/ICE.def

query: (ADJP* idomsonly {1}D-*|N-*|NS-*)

add_leaf_before{1}: (CODE *ZZZ_PROBABLY_NP*)
