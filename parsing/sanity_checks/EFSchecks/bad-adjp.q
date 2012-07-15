node: $ROOT|IP*

copy_corpus: t

query: (ADJP* idomsonly {1}ADV|ADVR|ADVS)

add_leaf_before{1}: (CODE *ZZZ_ADVP*)
