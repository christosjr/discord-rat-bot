import random

CAT_EMOJIS = ["🐈", "🐱", "😺", "😸", "😻", "😼", "😽", "🙀", "😿", "😾"]
COLORS = ["White", "Black", "Gray", "Orange", "Brown", "Silver", "Cream", "Mixed"]

def random_cat_emoji():
    return random.choice(CAT_EMOJIS)

def color_options():
    return COLORS
