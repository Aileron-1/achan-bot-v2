from .misc import emote

def generate_xp_bar(amount, maximum, *, xp_length=10):
    """ Generates a string containing emotes to represent a fraction.
    """
    filled = round(amount / maximum * xp_length)
    out = ''
    for i in range(xp_length):
        if i < filled:
            if i == 0:
                out += emote['xp_l_1']
            elif i == xp_length - 1:
                out += emote['xp_r_1']
            else:
                out += emote['xp_1']
        else:
            if i == 0:
                out += emote['xp_l_0']
            elif i == xp_length-1:
                out += emote['xp_r_0']
            else:
                out += emote['xp_0']
    return out

def calculate_level(total_xp):
    levels = 0
    xp = total_xp
    while xp - to_next_level(levels) >= 0:
        xp -= to_next_level(levels)
        levels += 1
    return levels

def calculate_xp_breakpoint(level):
    """ Get the xp, without remainder
    """
    xp = 0
    for i in range(level):
        xp += to_next_level(i)
    return xp

def to_next_level(current_level):
    formula = 8 * current_level * (45 + (5 * current_level))
    return round(formula / 100) * 100

if __name__ == '__main__':
    for i in range(30):
        print('level', calculate_level(i*100), i*100)