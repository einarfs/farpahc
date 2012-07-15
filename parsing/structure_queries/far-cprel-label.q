copy_corpus:t

define: def/verbtopic.def
node: IP*
query: 
({1}[1]NP* idoms {2}C) AND (C idoms sum-*)

replace_label{1}: CP-REL
add_leaf_before{2, 2}: (WNP 0)
