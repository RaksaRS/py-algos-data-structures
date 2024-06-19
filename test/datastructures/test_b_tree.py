import random
import pytest
from algosdatastructures.src.datastructures.b_tree import BTree, BTreeNode

_SEED_RANDOM = 1
_ORDERS_TO_TEST = list(range(3,18))


def test_tree_initialization():
    tree = BTree(3)

    assert tree.root is None


def test_btree_traversal():
    random.seed(_SEED_RANDOM)
    keys = list(range(1000))
    random.shuffle(keys)

    tree = BTree(11)
    for k in keys:
        tree.insert(k)

    prev = None
    for k in tree.traverse_inorder():
        assert prev is None or k > prev
        prev = k


def test_btree_search():
    random.seed(_SEED_RANDOM)
    keys = list(range(1000))
    random.shuffle(keys)

    tree = BTree(11)
    for k in keys:
        tree.insert(k)

    for k in keys:
        assert k in tree.search(k).keys


class TestBTreeInsert:
    KEYS_COUNT_FOR_BULK_INSERT_TEST = 1 << 16 - 1

    SAMPLE_VALS = [19, 12, 17, 5, 16, 3, 2, 14, 0, 9, 1, 13, 18, 7, 11, 4, 8]


    def test_null_insertion_into_empty_tree(self):
        tree = BTree(5)

        with pytest.raises(ValueError):
            tree.insert(None)
        assert tree.root is None


    @pytest.mark.parametrize('order', _ORDERS_TO_TEST)
    def test_single_insert_in_empty_tree_should_create_root(self, order):
        tree = BTree(order)

        tree.insert(1)

        assert tree.root
        assert len(tree.root.keys) == 1
        assert tree.root.keys[0] == 1
        assert len(tree.root.children) == 0


    @pytest.mark.parametrize('order', _ORDERS_TO_TEST)
    def test_when_insert_keys_out_of_order_to_fill_root_expect_sorted_keys(self, order):
        # This test inserts keys into the root node to the maximum number of
        # keys allowed and
        tree = BTree(order)
        vals = TestBTreeInsert.SAMPLE_VALS[:(order-1)]

        for i in range(order - 1):
            tree.insert(vals[i])

        assert tree.root.keys == sorted(vals)
        assert len(tree.root.children) == 0


    @pytest.mark.parametrize('order', _ORDERS_TO_TEST)
    def test_given_filled_root_when_insert_into_root_expect_root_split(self, order):
        # Filled root means a root node with the number of keys
        # equal to the maximum number of keys allowed
        root = BTreeNode(sorted( TestBTreeInsert.SAMPLE_VALS[:(order-1)] ))
        tree = BTree(order,root)

        tree.insert( TestBTreeInsert.SAMPLE_VALS[order-1] )

        assert len(tree.root.keys) == 1
        assert len(tree.root.children) == 2
        assert len(tree.root.children[0].children) == 0
        assert len(tree.root.children[1].children) == 0
        _BTreeAssert.assert_btree_properties(tree)


    @pytest.mark.parametrize('order', _ORDERS_TO_TEST)
    def test_given_root_with_2_children_when_insert_expect_insert_at_leaf(self, order):
        # Arrange
        tree = BTree(order)
        for i in range(order):  # Inserts just enough for root to split
            tree.insert( TestBTreeInsert.SAMPLE_VALS[i] )
        left_child_keys_before_act = tree.root.children[0].keys.copy()
        right_child_keys_before_act = tree.root.children[1].keys.copy()

        # Act
        new_val = min(TestBTreeInsert.SAMPLE_VALS) - 1
        tree.insert(new_val)

        # Assert
        assert len(tree.root.keys) == 1
        assert tree.root.children[0].keys == [new_val] + left_child_keys_before_act
        assert tree.root.children[1].keys == right_child_keys_before_act
        assert tree.root.children[0].children == []
        assert tree.root.children[1].children == []
        _BTreeAssert.assert_btree_properties(tree)


    def test_insert_splits_filled_leaf_in_tree_of_height_1(self):
        # Arrange
        tree = BTree(5)
        for i in range(1,8):
            tree.insert(i)

        # Act
        tree.insert(8)

        # Assert
        assert len(tree.root.children) == 3
        for c in tree.root.children:
            assert c.children == []
        assert tree.root.keys == [3,6]
        assert tree.root.children[0].keys == [1,2]
        assert tree.root.children[1].keys == [4,5]
        assert tree.root.children[2].keys == [7,8]


    def test_insert_splits_filled_leaf_and_filled_root_in_tree_of_height_1(self):
        # Arrange : Root has 5 children; the first 4 have 2 keys each, whereas
        # the 5th children has 4 keys. Total # keys = 4 + 4*2 + 4 = 16
        tree = BTree(5)
        for i in range(1,17):
            tree.insert(i)

        # Act
        tree.insert(17)

        # Assert : asserts tree now has height=2 and that btree properties are
        # stil maintained
        assert tree.root.children[0].children != []
        _BTreeAssert.assert_btree_properties(tree)


    def test_insert_recursively_splits_leaf_to_direct_child_of_root_in_tree_of_height_2(self):
        # Arrange : Root has 2 children. The left child has 3 children, where
        # each has 2 keys. The right child has 5 children. All grandchildren
        # except the rightmost one, have 2 keys each. The rightmost grandchild
        # has 4 keys.
        tree = BTree(5)
        for i in range(1,27):
            tree.insert(i)

        # Act : Splits the right most leaf, and consequently splits its parent,
        # which is a direct child of root
        tree.insert(28)

        # Assert
        _BTreeAssert.assert_btree_properties(tree)


    @pytest.mark.parametrize('order', _ORDERS_TO_TEST)
    def test_bulk_inserts(self, order):
        tree = BTree(order)
        keys_count = TestBTreeInsert.KEYS_COUNT_FOR_BULK_INSERT_TEST
        keys = list(range(keys_count))
        random.seed(_SEED_RANDOM)
        random.shuffle(keys)

        for k in keys:
            tree.insert(k)

        _BTreeAssert.assert_btree_properties(tree)


class TestBTreeRemove:
    KEYS_COUNT_IN_TREE_IN_BULK_REMOVAL_TEST = 1 << 16 - 1
    NUM_KEYS_TO_REMOVE_IN_BULK_REMOVAL_TEST = 1 << 7 - 1

    def test_null_removal(self):
        tree = BTree(5)

        for i in range(4):
            tree.insert(i)

        with pytest.raises(ValueError):
            tree.remove(None)

    def test_remove_non_existing_key(self):
        tree = BTree(7)

        with pytest.raises(ValueError):
            tree.remove(9)

    def test_root_removal_from_tree_with_root_only(self):
        order = 7
        tree = BTree(order)
        for i in range(1, order):
            tree.insert(i)

        tree.remove(2)

        assert tree.root.keys == [i for i in range(1, order) if i != 2]
        assert tree.root.children == []

    def test_no_fixing_removals_on_tree_of_height_1_and_has_3_nodes(self):
        tree = BTree(5)
        for i in range(3, 8):
            tree.insert(i)
        tree.insert(1)
        tree.insert(2)
        tree.insert(8)
        tree.insert(9)

        tree.remove(4)
        tree.remove(1)
        tree.remove(8)

        assert tree.root.keys == [5]
        assert len(tree.root.children) == 2
        assert tree.root.children[0].keys == [2,3]
        assert tree.root.children[1].keys == [6,7,9]
        assert len(tree.root.children[0].children) == 0
        assert len(tree.root.children[1].children) == 0

    def test_removal_fixes_by_merging_once_in_tree_of_height_1(self):
        tree = BTree(7)
        for i in range(1, 12):
            tree.insert(i)

        tree.remove(9)

        root = tree.root
        assert root.keys == [4]
        assert len(root.children) == 2
        assert root.children[0].keys == [1,2,3]
        assert root.children[1].keys == [5,6,7,8,10,11]
        assert root.children[0].children == []
        assert root.children[1].children == []

    def test_removal_fixes_by_merging_twice_in_tree_of_height_2(self):
        tree = BTree(5)
        for i in range(1, 27):
            tree.insert(i)
        root_keys_count = len(tree.root.keys)

        tree.remove(25)

        assert len(tree.root.keys) == root_keys_count - 1
        assert len(tree.root.children[-1].keys) == 4
        _BTreeAssert.assert_btree_properties(tree)

    def test_removal_fixes_once_by_borrowing_in_tree_of_height_1(self):
        ...

    def test_removal_fixes_twice_by_borrowing_in_tree_of_height_2(self):
        ...

    def test_removal_fixes_twice_by_borrowing_first_then_by_merging_in_tree_of_height_2(self):
        ...

    def test_removal_fixes_once_creates_new_root_in_tree_of_height_1(self):
        ...

    @pytest.mark.parametrize('order', [6,7])
    def test_bulk_removal(self, order):
        # Arrange
        tree = BTree(order)
        keys = list(range(TestBTreeRemove.KEYS_COUNT_IN_TREE_IN_BULK_REMOVAL_TEST))
        random.seed(_SEED_RANDOM)
        random.shuffle(keys)
        for k in keys:
            tree.insert(k)

        # Act
        random.seed(_SEED_RANDOM)
        keys_to_remove = random.sample(keys, \
                            TestBTreeRemove.NUM_KEYS_TO_REMOVE_IN_BULK_REMOVAL_TEST)

        for k in keys_to_remove:
            tree.remove(k)
            _BTreeAssert.assert_btree_properties(tree)

        # Assert
        _BTreeAssert.assert_btree_properties(tree)


class _BTreeAssert:
    """Provides static methods for asserting various properties of B-trees
    """
    @staticmethod
    def assert_btree_properties(tree):
        """Validates properties of a B-Tree
        """
        _BTreeAssert.assert_ordered_keys(tree.root)
        _BTreeAssert.assert_count_keys_and_children(tree.root, tree)
        _BTreeAssert.assert_descandants_keys_range(tree.root)
        _BTreeAssert.assert_leaves_level_equal(tree.root)

    @staticmethod
    def assert_count_keys_and_children(node: BTreeNode, tree: BTree):
        """Asserts keys count and children count (of all nodes in the subtree
        rooted at the given node) are correct

        This method asserts that:
        - The keys/children count are less than the maximum keys/children count
        - The no. of keys are one less than the no. of children
        """
        assert len(node.keys) < tree.order
        assert len(node.children) <= tree.order

        if node.is_internal():
            assert len(node.children) - len(node.keys) == 1

        for c in node.children:
            _BTreeAssert.assert_count_keys_and_children(c, tree)

    @staticmethod
    def assert_leaves_level_equal(node: BTreeNode):
        """Asserts all leaves (in the subtree rooted at the given node) are at
        the same depth

        Notes
        -----
        This method first finds the depth of the left-most leaf. Then, it looks
        at all leaves and asserts that the depths of those leaves are the same
        as the depth of the left-most leaf.
        """
        # Arrange phase : Find depth of left-most leaf
        depth_left_leaf = 0
        pointer = node
        while len(pointer.children) != 0:
            pointer = pointer.children[0]
            depth_left_leaf += 1

        # Act & Assert phase : Find & assert all leaves height are = depth_left_leaf
        def visit_leaf_and_assert_depth(n : BTreeNode,
                                        n_depth : int,
                                        target_leaf_depth : int):
            """A recursive function that asserts that leaves of the subtree
            rooted at the given node are at the given target depth.

            If the given node is an internal node, the function recurses on all
            children. If -- instead -- the given node is a leaf, the function
            checks if its depth is equal to the target leaf depth.

            Parameters
            ----------
            n : BTreeNode
                The node being visited
            n_depth : int
                The depth of node `n`
            target_leaf_depth : int
                The leaf depth that would be asserted against the actual leaves'
                depths
            """
            if n.is_leaf():
                assert n_depth == target_leaf_depth
                return True
            for c in n.children:
                assert visit_leaf_and_assert_depth(c, n_depth+1, target_leaf_depth)
            return True
        assert visit_leaf_and_assert_depth(node, 0, depth_left_leaf)

    @staticmethod
    def assert_descandants_keys_range(node: BTreeNode, lower=None, upper=None):
        """Asserts that the keys in the subtree rooted at the given node, are in
        the given min-max range
        """
        for key_idx, key in enumerate(node.keys):
            if key_idx >= 1:
                assert node.keys[key_idx - 1] <= key
            if lower:
                assert key >= lower
            if upper:
                assert key <= upper

        for idx_child in range(len(node.children)):
            child_subtree_min = node.keys[idx_child - 1] if idx_child > 1 else lower
            child_subtree_max = node.keys[idx_child] if idx_child < len(
                node.keys) else upper
            _BTreeAssert.assert_descandants_keys_range(\
                node.children[idx_child], child_subtree_min, child_subtree_max)

    @staticmethod
    def assert_ordered_keys(node : BTreeNode):
        """Assserts that the keys in the subtree rooted at the given node, are
        ascendingly ordered
        """
        for i in range(1, len(node.keys)):
            assert node.keys[i] >= node.keys[i-1]
        for c in node.children:
            _BTreeAssert.assert_ordered_keys(c)
