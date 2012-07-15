copy_corpus:t

node:IP*
query: (IP* idoms {1}NP*) AND (NP* idoms PRO-D) AND (PRO-D idomsonly tí-*|Tí-*) AND (NP* iprecedes C) AND ({2}C idoms at-*)

extend_span{1, 2}:
add_internal_node{1, 2}: PP
add_leaf_before{1, 2}: (P 0)
add_internal_node{2, 2}: CP-THT-PRN
