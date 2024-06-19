# B-Trees

**Just a friendly reminder**: the purpose of this document is to provide the details of my implementation. I don't think this document gives a well done explanation of a B-tree and its operations. Therefore, for those who aren't familiar with B-Trees, this document woudln't be of much help.

This implementation supports:

- Keys of any data types
- Traversal
- Even orders (the original specification only supports odd orders)

The implementation is yet to be verified/tested if it supports duplicate keys.

This implementation uses this definition of B-Trees:
A B-tree of order M is a tree that meets the following conditions:

1. Every node except the root has at least $[\frac{M-1}{2}]$ keys where $[x]$ denotes the floor of $x$.
2. Every node has at most M-1 keys and M children
3. The number of children in every node is one more than the number of keys
4. All leaves are at the same level.
5. The keys in each node are in ascending order.
6. All keys in the left subtree of a key $k$ is less than $k$ and all keys in the right subtree of $k$ are greater than $k$

## Insertion

As per the original specification, b-tree insertions only occur at the leaf level. To find the leaf the new key belongs in, we start at the root, and move down the tree to the leaf. Once a new key is inserted, the leaf may overflow (has one too many keys).

Suppose a tree of order $M$ has a node $N$ that is overflowing and let the following be the structure of $N$:
$$p_0, x_1, p_1, x_2, p_2, ..., x_i, p_i, ..., x_{M-1}, p_{M-1}$$
($x_k$ are keys and $p_k$ and children, and $x_i$ is the middle key).

To fix the tree, we perform a _split_ on $N$.

We move $x_i$ to the parent (create a parent beforehand if $N$ is the root node). 2 new nodes are then created and are assigned to be children $N$'s parent; one node is assigned to be the child to the left of $x_i$ in the parent, and the other is assigned to be the child to the right. The former node has the following structure:
$$p_0, x_1, p_1, x_2, p_2, ..., x_{i-1}, p_{i-1}$$
while the latter has the following structure:
$$p_i, x_{i+1}, p_{i+1}, x_{i+2}, p_{i+2}, ..., x_{M-1}, p_{M-1}$$

Since the parent of $N$ received a new key, it may overflow. In which case, we recurse.

## Removal

As per the original specification, the removal process starts by locating the key to be removed. Let $x_i$ be the key to be removed, $N$ be the node containing it and let the following be its structure:

$$p_0, x_1, p_1, x_2, p_2, ..., x_i, p_i, ..., x_m, p_m \text { where } m \le \text{order}-1$$

After locating $x_i$, we move to the left-most leaf of the sub-tree rooted at the node $p_i$ points to. Let this leaf be $L$.

$x_i$ in $N$ is then replaced by $x_0$ of $L$ and $x_0$ of $L$ is removed. The removal may cause the leaf to underflow (having one too few keys). In this case, more work needs to be done. Specifically, there are 3 scenarios. But, before we look at that, let's define what a _populous_ node means. A _populous_ node is a node whose number of keys is at least one more than the required minimum number of keys.

When encountering an underflowing node $N$, there are 3 scenarios:

1. The node has an **adjacent** sibling $S$ that is populous. Let the following be the structure of $N$: $$p_0, x_1, p_1, x_2, p_2, ..., x_m, p_m$$ and let the following be the structure of $S$: $$q_0, y_1, q_1, y_2, q_2, ..., y_n, q_n$$ There are 2 subcases:

   i. $S$ is a left sibling.
   Then, the parent of $N$ and $S$ has the following structure: $$..., p(S), k, p(N), ...$$ where $p(S)$ and $p(N)$ are pointers to $S$ and $N$, and $k$ is the key betweeen them.

   We construct a temporary node $T$ to have the following structure: $$q_0, y_1, q_1, y_2, q_2, ..., y_n, q_n, k, p_0, x_1, p_1, x_2, p_2, ..., x_m, p_m$$

   Let $b$ be the middle key of $T$. We now replace $k$ --- in the parent node --- with $b$, and restructure $S$ to contain the keys & children that are to the left --- in node $T$ --- of $b$ as well as restructure $N$ to contain the keys & children to the right --- in node $T$ --- of $b$.
   After this, it is guaranteed that the B-Tree is now valid, and we're finished.

   ii. $S$ is a right sibling. This case is basically the same as the above case, except the positions of $S$ and $N$ are swapped.

2. The node has no **adjacent** siblings that are populous.
   In this case, we also form a temporary node $T$ like case (1). Unlike case (1), however, after forming $T$, we remove the nodes $S$ and $N$ and remove key $k$ of the parent. Then, we assign $T$ as the new child of the parent. Specifically, if -- before the removal process -- the parent of $S$ and $N$ has the following structure: $$..., l_i, p_i, k, p_{i+1}, l_{i+2}, p_{i+2}, ... $$
   then, after removal, the parent looks like this:
   $$..., l*i, p_T, l*{i+2}, p\_{i+2}, ...$$
   ($p_T$ points to node T).

   Since the parent lost a key, it may underflow. So, we recurse.

3. $N$ is the root and has no keys. In this case, $N$ must have exactly 1 child. So, we appoint this child as the new root.
