node: IP*

copy_corpus: t

query: ([1]NP* iDoms N-*)
        AND ([1]NP* iDoms {1}PRO-*)
        AND (PRO-* iDoms *-minn|*-þinn|*-sinn|*-vor|mín*|tín*|sín*|mítt*|títt*|sítt*)

add_internal_node{1, 1}: NP-POS
