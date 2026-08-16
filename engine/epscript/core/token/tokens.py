# -*- coding: utf-8 -*-

# 关键
KWLIST_EN = [
    "var",  # 0
    "true",   # 1
    "false",   # 2
    "null",   # 3
    "if",   # 4
    "else",   # 5
    "function",   # 6
    "for",   # 7
    "from",   # 8
    "to",   # 9
    "step",   # 10
    "while",   # 11
    "break",  # 12
    "continue",  # 13
    "return",   # 14
]
KWLIST_ZH = [
    "设置",
    "真",
    "假",
    "空",
    "如果",
    "否则",
    "函数",
    "循环",
    "从",
    "到",
    "每次",
    "重复当",
    "停止",
    "跳过",
    "返回",
]

# 数据结构
STRING = "STRING"
INT = "INTEGER"
FLOAT = "FLOAT"
LIST = "LIST"
# 特殊数据结构
LAZY = "LAZY"    # 懒加载
VARIABLE = "VARIABLE"
KEYWORD = "KEYWORD"
# 标志
LEFT_PARENT = "LEFT_PARENT"  # (
RIGHT_PARENT = "RIGHT_PARENT"  # )
LEFT_BRACKET = "LEFT_BRACKET"  # [
RIGHT_BRACKET = "RIGHT_BRACKET"   # ]
LEFT_FLAG = "LEFT_FLAG"    # {
RIGHT_FLAG = "RIGHT_FLAG"   # }
# 符号
COMMA = "COMMA"  # ,
PLUS = "PLUS"  # +
MINUS = "MINUS"  # -
MULTIPLY = "MULTIPLY"  # *
DIVIDE = "DIVIDE"  # /
MOD = "MOD"  # %
POW = "POW"  # **
COPY = "COPY_VALUE"   # =
EQUAL = "EQUAL_TO"   # ==
GREATER = "GREETER"   # >
GREATER_EQUAL = "GREETER_EQUAL"  # >=
LESSER = "LESSER"  # <
LESSER_EQUAL = "LESSER_EQUAL"  # <=
NOT_EQUAL = "NOT_EQUAL"  # !=
AND = "AND"  # &
OR = "OR"  # |
NOT = "NOT"   # !
ONION = "ONION"  # :
DOT = "DOT"  # .

EOF = "EOF"
NEWLINE = "NEWLINE"
