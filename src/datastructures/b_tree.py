"""This module provides the implementation of a B-Tree.

This module provides a simple implementation of B-Tree nodes and B-Trees. See
refs/btree.md for reference/more details.
"""
from typing import Any, Generator, Optional


class BTreeNode:
    """Represents a node in a b-tree

    This implementation of B-Trees support even orders, which isn't in the
    original specification

    Attributes
    ----------
    keys : list
        Represents keys of a b-tree node
    children : list of `BTreeNode`
        Represents the children of a b-tree node
    """

    def __init__(self, keys: Optional[list[Any]] = None, children: Optional[list['BTreeNode']] = None):
        self.keys = keys if keys is not None else []
        self.children = children if children is not None else []

    def is_internal(self) -> bool:
        """Checks if the node is an internal node

        Returns
        -------
        bool
            `True` if the node is an internal node; otherwise, `False`

        Notes
        -----
        Every node in the tree is an internal node, except the leaves.
        """
        return not self.is_leaf()

    def is_leaf(self) -> bool:
        """Checks if the node is a leaf node

        Returns
        -------
        bool
            `True` if the node is a leaf; otherwise, `False`
        """
        return len(self.children) == 0

    def insert_key(self, idx: int, key: Any) -> None:
        """Attempts to insert a new key into the node

        Parameters
        ----------
        idx : int
            The index at which `key` should be in the node's keys
        key : Any
            The key to be inserted
        """
        self.keys.insert(idx, key)

    def traverse_inorder(self) -> Generator[Any, None, None]:
        """Performs in-order traversal of the tree rooted at this node

        Yields
        ------
        key
            Every key of every node in ascending order
        """
        for i, c in enumerate(self.keys):
            if self.is_internal():
                yield from self.children[i].traverse_inorder()
            yield c
        if self.is_internal():
            yield from self.children[-1].traverse_inorder()


class BTree:
    """Represents a B-Tree

    This implementation of B-Trees support even orders, which isn't in the
    original specification

    Attributes
    ----------
    order : int
        Represents the order of the B-Tree
    root : BTreeNode
        The root node of the B-Tree
    """

    def __init__(self, order: int, root: Optional[BTreeNode] = None):
        self.order = order
        self.root = root

    def traverse_inorder(self) -> Generator[Any, None, None]:
        """Returns the inorder traversal of the B-Tree

        Yields
        -------
        keys
            The inorder traversal
        """
        if self.root:
            yield from self.root.traverse_inorder()

    def search(self, target: Any) -> Optional[BTreeNode]:
        """Searches for a key in a B-Tree

        Parameters
        ----------
        target : any
            The key to search for

        Returns
        -------
        BTreeNode
            The node containing the target key, if it exists, or None
            otherwise
        """
        if target is None:
            raise ValueError("Attempted to search for key `None`")

        curr_node = self.root
        while curr_node:
            curr_key_idx = 0
            while curr_key_idx < len(curr_node.keys)\
                    and target > curr_node.keys[curr_key_idx]:
                curr_key_idx += 1

            if curr_key_idx != len(curr_node.keys) \
                    and target == curr_node.keys[curr_key_idx]:
                return curr_node

            curr_node = curr_node.children[curr_key_idx]
        return None

    def insert(self, key: Any) -> None:
        """Inserts a key into the B-Tree

        Parameters
        ----------
        key
            The key to be inserted
        """
        if key is None:
            raise ValueError("Attempted to insert key `None`")

        if not self.root:
            self.root = BTreeNode([key])
            return

        # stores nodes that are on the path to the leaf that the insertion occurs
        # on. the items are 2-element tuples: the first element is the node
        # itself and the second element is the idx of the next node in this
        # node's list of children
        path = []

        curr_node = self.root
        while True:
            curr_key_idx = 0
            while curr_key_idx < len(curr_node.keys) \
                    and key > curr_node.keys[curr_key_idx]:
                curr_key_idx += 1

            # curr_key_idx is also the index -- in curr_node.children -- of the
            # child node to move to
            path.append((curr_node, curr_key_idx))
            if curr_node.is_leaf():
                break

            curr_node = curr_node.children[curr_key_idx]

        leaf, leaf_key_idx = path[-1]
        leaf.insert_key(leaf_key_idx, key)

        self._fix_insert(path)

    def _fix_insert(self, path: list[BTreeNode]) -> None:
        """Restructures the tree -- after inserting a key -- to maintain the
        B-Tree so that it remains valid

        Parameters
        ----------
        path : list of `BTreeNode`
            The nodes on the path to the leaf node (inclusive), where the new
            key was inserted. Each item is a two-element tuple: the first
            element is the node itself and the second element is the idx of the
            next node in this node's list of children

        Notes
        -----
        See refs/btree.md for more details
        """
        node_idx_in_path = len(path) - 1
        while node_idx_in_path >= 0:
            curr_node, _ = path[node_idx_in_path]
            if len(curr_node.keys) <= self.order - 1:
                return

            mid_key_idx = (self.order - 1) // 2

            left_node = BTreeNode(
                curr_node.keys[:mid_key_idx], curr_node.children[:(mid_key_idx+1)])
            right_node = BTreeNode(
                curr_node.keys[(mid_key_idx+1):], curr_node.children[(mid_key_idx+1):])

            if node_idx_in_path == 0:
                new_root = BTreeNode([curr_node.keys[mid_key_idx]], [
                                     left_node, right_node])
                self.root = new_root
            else:
                parent, idx_node_as_child = path[node_idx_in_path - 1]
                parent.insert_key(idx_node_as_child,
                                  curr_node.keys[mid_key_idx])

                parent.children[idx_node_as_child] = left_node
                parent.children.insert(idx_node_as_child + 1, right_node)

            node_idx_in_path -= 1

    def remove(self, key: Any) -> None:
        """Removes a key from the B-Tree

        Parameters
        ----------
        key
            The key to be removed
        """
        if key is None:
            raise ValueError("Attempted to remove key `None`")

        target_node = self.root
        path = [(target_node, None)]

        while target_node:
            target_node_key_idx = 0
            while target_node_key_idx < len(target_node.keys) \
                    and key > target_node.keys[target_node_key_idx]:
                target_node_key_idx += 1

            if target_node_key_idx < len(target_node.keys) \
                    and key == target_node.keys[target_node_key_idx]:
                break

            if target_node.is_internal():
                target_node = target_node.children[target_node_key_idx]
            else:
                target_node = None
            path.append((target_node, target_node_key_idx))

        if target_node is None:
            raise ValueError(f"Attempted to remove a non-existing key `{key}`")

        if target_node.is_internal():
            leaf = target_node.children[target_node_key_idx + 1]
            path.append((leaf, target_node_key_idx + 1))
            while leaf.is_internal():
                leaf = leaf.children[0]
                path.append((leaf, 0))

            target_node.keys[target_node_key_idx] = leaf.keys[0]
            del leaf.keys[0]
        else:
            del target_node.keys[target_node_key_idx]

        self._fix_remove(path)

    def _fix_remove(self, path: tuple[BTreeNode, int]) -> None:
        """Fixes the B-Tree after removals if necessary

        Parameters
        ----------
        path : tuple[BTreeNode, int]
            The path to the leaf whose key has just been deleted. The root is
            the first element in the tuple

        Notes
        -----
        See refs/btree.md for more details
        """
        curr_node_idx_in_path = len(path) - 1
        while curr_node_idx_in_path >= 0:
            curr_node, curr_node_child_idx = path[curr_node_idx_in_path]

            if curr_node is self.root and len(curr_node.children) == 1:
                self.root = curr_node.children[0]
                return
            if not self._is_node_underflowing(curr_node):
                return

            parent_curr_node, _ = path[curr_node_idx_in_path - 1]
            # `curr_node` has left siblings
            if curr_node_child_idx != 0:
                left_sibling = parent_curr_node.children[curr_node_child_idx - 1]
                if self._is_node_populous(left_sibling):
                    merged_keys = left_sibling.keys \
                        + [parent_curr_node.keys[curr_node_child_idx - 1]] \
                        + curr_node.keys
                    merged_children = left_sibling.children + curr_node.children

                    # merge keys
                    merged_keys_mid_idx = len(merged_keys)//2
                    parent_curr_node.keys[curr_node_child_idx - 1] = \
                        merged_keys[merged_keys_mid_idx]
                    left_sibling.keys = merged_keys[:merged_keys_mid_idx]
                    curr_node.keys = merged_keys[(merged_keys_mid_idx+1):]

                    left_sibling.children = merged_children[:(
                        merged_keys_mid_idx+1)]
                    curr_node.children = merged_children[(
                        merged_keys_mid_idx+1):]
                    break

            # `curr_node` has right siblings
            if curr_node_child_idx != len(parent_curr_node.children) - 1:
                right_sibling = parent_curr_node.children[curr_node_child_idx + 1]
                if self._is_node_populous(right_sibling):
                    merged_keys = curr_node.keys \
                        + [parent_curr_node.keys[curr_node_child_idx]] \
                        + right_sibling.keys
                    merged_children = curr_node.children + right_sibling.children

                    merged_keys_mid_idx = len(merged_keys) // 2

                    curr_node.keys = merged_keys[:merged_keys_mid_idx]
                    parent_curr_node.keys[curr_node_child_idx] = \
                        merged_keys[merged_keys_mid_idx]
                    right_sibling.keys = merged_keys[(merged_keys_mid_idx+1):]

                    curr_node.children = merged_children[:(
                        merged_keys_mid_idx+1)]
                    right_sibling.children = merged_children[(
                        merged_keys_mid_idx+1):]
                    break

            # if execution reaches this line, then `curr_node` either
            # 1. has no right siblings and the left sibling isn't populous or,
            # 2. has no left siblings and the right sibling isn't populous

            # case 1
            if curr_node_child_idx == len(parent_curr_node.children) - 1:
                merged_node = left_sibling
                del parent_curr_node.children[curr_node_child_idx]

                merged_node.keys.append(
                    parent_curr_node.keys.pop(curr_node_child_idx - 1))
                merged_node.keys.extend(curr_node.keys)
                merged_node.children.extend(curr_node.children)
            # case 2
            else:
                merged_node = curr_node
                del parent_curr_node.children[curr_node_child_idx + 1]
                merged_node.keys.append(
                    parent_curr_node.keys.pop(curr_node_child_idx))
                merged_node.keys.extend(right_sibling.keys)
                merged_node.children.extend(right_sibling.children)

            curr_node_idx_in_path -= 1

    def _is_node_underflowing(self, node: BTreeNode) -> bool:
        """Checks if the given node is underflowed

        An underflowed node is a node whose number of keys is just one less than
        the required minimum number of keys.

        Parameters
        ----------
        node : BTreeNode
            The node to check out

        Returns
        -------
        bool
            `True` if the node is underflowing; otherwise, `False`
        """
        if node is self.root:
            return False
        return len(node.keys) < (self.order - 1) // 2

    def _is_node_populous(self, node: BTreeNode) -> bool:
        """Checks if the given node is underflowed

        An populous node is a node whose number of keys is just two or more than
        the required minimum number of keys.

        Parameters
        ----------
        node : BTreeNode
            The node to check out

        Returns
        -------
        bool
            `True` if the node is populous; otherwise, `False`
        """
        if node is self.root:
            return False
        return len(node.keys) >= (self.order - 1) // 2 + 1
