copy_corpus:t

node:IP*
query: ({1}NP* idoms P) AND (NP* idoms N-D) AND (P idoms av\$*) AND ({2}N-D idoms \$stað*)

replace_label{1}: PP
add_internal_node{2, 2}: NP
