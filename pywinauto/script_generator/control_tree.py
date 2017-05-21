from collections import deque

from .. import findbestmatch
from ..base_wrapper import BaseWrapper


class ControlTreeNode(object):
    def __init__(self, ctrl, names, rect):
        self.ctrl = ctrl
        self.names = names
        self.rect = rect

        self.depth = 0
        self.parent = None
        self.children = []

    def __str__(self):
        return '{}, {}, depth={}'.format(self.names, self.rect, self.depth)


class ControlTree(object):
    def __init__(self, ctrl):
        if isinstance(ctrl, BaseWrapper):
            self.ctrl = ctrl
        else:
            raise TypeError('ctrl must be a wrapped control')
        self.root = None
        self.root_name = ""
        self.rebuild()

    def rebuild(self):
        """Create tree structure"""
        # Create a list of this control and all its descendants
        all_ctrls = [self.ctrl, ] + self.ctrl.descendants()
        txt_ctrls = [ctrl for ctrl in all_ctrls if ctrl.can_be_label and ctrl.is_visible() and ctrl.window_text()]

        root_names = findbestmatch.get_control_names(self.ctrl, all_ctrls, txt_ctrls)
        self.root = ControlTreeNode(self.ctrl, root_names, self.ctrl.rectangle())
        self.root_name = [name for name in root_names if len(name) > 0 and " " not in name][-1]

        def go_deep_down_the_tree(parent_node, child_ctrls, current_depth=1):
            if len(child_ctrls) == 0:
                return

            for ctrl in child_ctrls:
                if ctrl not in all_ctrls:
                    continue

                ctrl_names = findbestmatch.get_control_names(ctrl, all_ctrls, txt_ctrls)
                ctrl_rect = ctrl.rectangle()

                ctrl_node = ControlTreeNode(ctrl, ctrl_names, ctrl_rect)
                ctrl_node.depth = current_depth
                ctrl_node.parent = parent_node
                parent_node.children.append(ctrl_node)

                go_deep_down_the_tree(ctrl_node, ctrl.children(), current_depth + 1)

        go_deep_down_the_tree(self.root, self.ctrl.children())

    def iterate_dfs(self, node=None):
        """Iterate tree in pre-order depth-first search order"""
        if node is None:
            node = self.root
        yield node
        for child in node.children:
            for n in self.iterate_dfs(child):
                yield n

    def iterate_bfs(self, node=None):
        """Iterate tree in pre-order breadth-first search order"""
        if node is None:
            node = self.root
        queue = deque([node])
        while queue:
            current_node = queue.popleft()
            yield current_node
            for child in current_node.children:
                queue.extend([child])

    def print_tree(self):
        for node in self.iterate_dfs():
            print('{0}{1}'.format("   | " * node.depth, node))

    def node_from_point(self, point):
        res = None
        for node in self.iterate_bfs():
            if node.rect.contains(point):
                res = node
        return res
