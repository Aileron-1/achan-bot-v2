emote =  {
    'hololive': '<:holocredit:695430369171734588>',
    'credits': '<:holocredit:695430369171734588>',
    'asacoco': '<:asacoco:686976273020616775>',
    'yubi': '<:yubi:697112112362815598>',
    'coco': '<:Coco_Rawr:702478918711640074>',
    'w_heh': '<:Watame_Heh:702765327901130802>',
    'w_dc': '<:Watame_DC:694924345046466611>',
    'ac_tank': '<:asacoco_can:697622482466767001>',
    'rock': '<:janken_gu:697592125168287754>',
    'paper': '<:janken_pa:697592125734518826>',
    'scissors': '<:janken_choki:697592125885251585>',
    'nothing': '<:Nothing:694924319133794395>',
    'comet': '\U00002604',
    'ok': '\U0001F197',
    'no': '\U0000274C',
    'no2': '\U0001F6AB',
    'one': '<:number_1:698035272935538748>',
    'two': '<:number_2:698037325967654972>',
    'three': '<:number_3:698035292593979393>',
    'four': '<:number_4:702519821803323532>',
    'five': '<:number_5:702519821757055056>',
    'ovo': '<:Watame_OvO:702765327376973825>',
    'coco_smug': '<:Coco_Smug:702478918279495750>',
    'w_smug': '<:Watame_Smug:724530952331722843>',
    'left': '<:hitosashiyubiL:700574478689763328>',
    'right': '<:hitosashiyubiR:700574474705174648>',
    'xp_0': '<:xp_0:747591006832296017>',
    'xp_1': '<:xp_1:747591007079759892>',
    'xp_l_0': '<:xp_l_0:747591991583309996>',
    'xp_l_1': '<:xp_l_1:747591991499686080>',
    'xp_r_0': '<:xp_r_0:747591991231250433>',
    'xp_r_1': '<:xp_r_1:747591991583572070>',

}
currency_names = {
    'credits':'HoloCredits',
    'asacoco':'AsaCoco',
    'yubi':'Yubi'
}

def currency_str(currency_type, amount):
    return '%s**%s**'%(emote[currency_type], amount)