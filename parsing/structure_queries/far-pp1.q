copy_corpus:t

define: def/verbtopic.def
node: IP*
query: 
({1}[1]*P idoms ADV) AND (ADV idoms til-*) AND ([1]*P idoms {2}*-G)

replace_label{1}: PP
add_internal_node{2, 2}: NP
