copy_corpus:t

node:IP*
query: (IP* idoms {1}P) AND (P idomsonly so-*) AND (P iprecedes ADV) AND ({3}ADV idomsonly {2}at-*)

extend_span{1, 2}:
add_internal_node{1, 2}: PP
add_internal_node{2, 2}: ADV
replace_label{3}: CP-ADV
