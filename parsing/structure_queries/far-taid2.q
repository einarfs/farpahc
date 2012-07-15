copy_corpus:t

node:IP*
query: (IP* idoms {1}NP) AND (NP idoms {2}ADV) AND (ADV idomsonly tá-*|Tá-*) AND (ADV iprecedes NP*|NP-*) AND ({3}NP*|NP-* idoms C) AND ({4}C idoms ið-*)

delete_node{1}:
add_internal_node{2, 3}: ADVP-TMP
replace_label{3}: CP-REL
add_leaf_before{4}: (WADVP 0)
