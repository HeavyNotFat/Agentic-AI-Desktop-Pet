import unicodedata


def text_block_width(text) -> int:
    """Calculate the width of a text block"""
    width = 0
    for char in text:
        category = unicodedata.east_asian_width(char)
        if category in ('F', 'W'):
            width += 2
        elif category == 'A':
            width += 2
        else:
            width += 1
    return width


if __name__ == '__main__':
    print(text_block_width('hello world'))   #  11
    print(text_block_width('你好世界'))   # 8
    print(text_block_width(' '))  # 1
    print(text_block_width("1 + 1"))  # 5
