#!/usr/bin/python
# -*- coding:utf-8 -*-
# Author : Yam
# Data : 2021/3/2 21:49

# 全局宏定义

RED = 0
BLACK = 1

import matplotlib.pyplot as plt


class Node:
    def __init__(self, value, color=RED, parent=None):
        self.data = value
        self.left = None
        self.right = None
        self.parent = parent
        self.color = color

        # 用于画图的位置信息
        self.x = 0
        self.y = 0

    def __str__(self):
        return "{}(c:{})".format(self.data, self.getColor())

    def info(self):
        return "{}({})'s papa is {}, lc is {}, rc is {}.".format(
            self.data, self.getColor(),
            self.parent.data if self.parent else "None",
            self.left.data if self.left else "None",
            self.right.data if self.right else "None")

    def cc(self):
        """change color"""
        self.color ^= 1

    def getColor(self):
        return "k" if self.color else "r"

    def leftEdge(self):
        if self.left:
            return [self.x, self.left.x], [self.y, self.left.y]
        return None

    def rightEdge(self):
        if self.right:
            return [self.x, self.right.x], [self.y, self.right.y]
        return None


class Tree:
    def __init__(self):
        self.root = None

    def lineorder(self):
        """层序遍历"""
        from collections import deque

        que = deque()
        que.append(self.root)

        while que:
            current = que[0]
            print(current.info())
            if current.left:
                que.append(current.left)
            if current.right:
                que.append(current.right)
            que.popleft()

    def inorder(self, current, nodes=None, height=0):
        if current is None:
            return

        self.inorder(current.left, nodes, height=height + 1)

        # 当前结点的操作
        if nodes:
            nodes["len"] += 1
            current.x = nodes["len"]
            current.y = height
            node = [current.x, current.y, current.data]
            nodes[current.getColor()].append(node)
        else:
            print(current.info())

        self.inorder(current.right, nodes, height=height + 1)

        if nodes:
            if current.left:
                nodes["edges"].append(current.leftEdge())
            if current.right:
                nodes["edges"].append(current.rightEdge())

        return

    def plot(self, save=False, lw=2, s=1000, fontsize=15):
        """画出红黑树图像"""
        nodes = {"len": 0, "k": [], "r": [], "edges": []}
        # 中序遍历获得结点
        self.inorder(self.root, nodes)

        # 打印边
        for x, y in nodes["edges"]:
            plt.plot(x, y, color="k", linewidth=lw, zorder=0)

        # 打印红色结点
        for color in ["r", "k"]:
            colordict = {"r": "#ff9999", "k": "#cfcfcf"}
            for node in nodes[color]:
                plt.scatter(node[0], node[1], s=s, c=colordict[color],
                            alpha=1, edgecolors='k', zorder=2)
                plt.text(node[0], node[1], node[2], c="k", fontsize=fontsize,
                         horizontalalignment='center',
                         verticalalignment='center')

        # 扩大画布
        deepthr = max(nodes["r"], key=lambda x: x[1])
        deepthk = max(nodes["k"], key=lambda x: x[1])
        deepth = max(deepthk, deepthr)[1]
        plt.axis('off')
        plt.xlim((-1, nodes["len"] + 1))
        plt.ylim((deepth + 2, -1))

        if save:
            plt.savefig("./RBTree.png")

        plt.show()


class RBTree(Tree):
    def rotateR(self, N):
        """
        右旋
            P                   P
             \                   \
            --N--               --A--
           /     \    -->      /     \
          A       B           AL      N
         / \                         / \
        AL  AR                      AR  B
        """
        assert N.left, "{} with no left child".format(str(N))

        A = N.left
        A.parent = N.parent
        if not N.parent:  # 如果N的父节点不存在
            self.root = A  # A 是新的根结点
        elif N.parent.left is N:  # N原来是左孩子
            N.parent.left = A
        elif N.parent.right is N:  # N原来是右孩子
            N.parent.right = A

        # 挂上 AR
        if A.right:
            A.right.parent = N
        N.left = A.right

        # A,N父子关系
        N.parent = A
        A.right = N

    def rotateL(self, N):
        """
        左旋
            P                   P
             \                   \
            --N--               --B--
           /     \    -->      /     \
          A       B           N       BR
                 / \         / \
                BL  BR      A  BL    

        """

        assert N.right, "{} with no right child".format(str(N))

        B = N.right
        B.parent = N.parent

        if not N.parent:  # 如果N的父节点不存在
            self.root = B  # A 是新的根结点
        elif N.parent.left is N:  # N原来是左孩子
            N.parent.left = B
        elif N.parent.right is N:  # N原来是右孩子
            N.parent.right = B

        # 挂上 BL
        if B.left:
            B.left.parent = N
        N.right = B.left

        # B, N父子关系
        N.parent = B
        B.left = N

    def insert(self, value):
        """插入操作"""

        new_node = Node(value)

        # 寻找插入位置并插入，用 ptr 指向新插入的结点
        ptr = self.root
        papa = None
        while ptr:
            papa = ptr
            if new_node.data <= papa.data:
                ptr = papa.left
            else:
                ptr = papa.right

        if not papa:
            # papa 为空，没进入while 循环，即根结点为空
            self.root = new_node
            new_node.color = BLACK
            return
        else:
            # 插入结点
            if new_node.data <= papa.data:
                papa.left = new_node
            else:
                papa.right = new_node
            new_node.parent = papa

        self.insert_fixup(new_node)

    def insert_fixup(self, current):
        """调整current（红结点）"""
        papa = current.parent

        # 如果current是红结点，并且papa也是红结点
        while papa and papa.color == RED:
            grandpa = papa.parent

            if grandpa.left is papa:
                #  papa(r) <- grandpa
                uncle = grandpa.right

                if uncle and uncle.color == RED:
                    #  papa(r) <- grandpa -> uncle(r)
                    # 变色
                    papa.cc()
                    uncle.cc()
                    grandpa.cc()
                    current = grandpa
                    continue
                if papa.right is current:
                    #          grandpa(b)
                    #         /       \
                    #    papa(r)     None or Black Node
                    #       \
                    #       current(r)
                    self.rotateL(papa)
                    papa, current = current, papa

                #          grandpa(b)
                #         /       \
                #    papa(r)     None or Black Node
                #      /
                # current(r)
                self.rotateR(grandpa)
                grandpa.cc()
                papa.cc()
                #          papa(b)
                #         /      \
                # current(r)     grandpa(r)

            else:  # grandpa -> papa(r)
                uncle = grandpa.left
                if uncle and uncle.color == RED:
                    # uncle(r) <- grandpa -> papa(r)
                    papa.cc()
                    uncle.cc()
                    grandpa.cc()
                    current = grandpa
                    continue

                if papa.left is current:
                    #    grandpa(b)
                    #   /       \
                    #  ^        papa(r)
                    #           /
                    #      current(r)
                    self.rotateR(papa)
                    papa, current = current, papa
                    #    grandpa(b)
                    #   /       \
                    #  ^        papa(r)
                    #            \
                    #            current(r)

                self.rotateL(grandpa)
                grandpa.cc()
                papa.cc()
                #        papa(b)
                #       /      \
                # grandpa(r)   current(r)
        # 确保根结点是黑色
        self.root.color = BLACK


if __name__ == '__main__':
    rbt = RBTree()

    values = [9, 5, 4, 6, 2, 8, 7, 3, 1, 0]
    for v in values:
        rbt.insert(v)
    rbt.plot(save=True)
