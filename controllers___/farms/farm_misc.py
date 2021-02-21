from ..misc import emote
import datetime

def convert_price(list_of_prices):
    credits_cost = 0
    asacoco_cost = 0
    yubi_cost = 0
    for price in list_of_prices:
        if price.type == 'credits':
            credits_cost += price.amount
        if price.type == 'asacoco':
            asacoco_cost += price.amount
        if price.type == 'yubi':
            yubi_cost += price.amount
    return credits_cost, asacoco_cost, yubi_cost

def display_price(cost):
    """ Returns readable string ver of price.
        Does not show if 0
    """
    credits_cost, asacoco_cost, yubi_cost = cost
    to_display = ''
    if credits_cost != 0:
        to_display += '%s%s' % (emote['credits'], credits_cost)
    if asacoco_cost != 0:
        if to_display != '':  # if there already is text, then add a comma
            to_display += ', '
        to_display += '%s%s' % (emote['asacoco'], asacoco_cost)
    if yubi_cost != 0:
        if to_display != '':
            to_display += ', '
        to_display += '%s%s' % (emote['yubi'], yubi_cost)
    return to_display

def seconds_to_hm(seconds):
    td_in_seconds = seconds
    hours, remainder = divmod(td_in_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    if minutes < 10:
        minutes = "0{}".format(minutes)
    if seconds < 10:
        seconds = "0{}".format(seconds)
    return "{}:{}:{}".format(hours, minutes, seconds)

def generate_crop_info(crop_data, crop, with_name=True):
    cost = display_price(convert_price(crop.cost))
    product = display_price(convert_price(crop.product))
    time = seconds_to_hm(crop_data[crop.id-1].grow_time)
    crop_info = ''
    if with_name:
        crop_info = '*%s* \n' % crop.name
    crop_info += '`Grow time:` %s \n`Cost:` %s \n`Product:` %s' % (time, cost, product)
    if crop.reusable:
        crop_info += ' *(reusable)*'
    return crop_info
