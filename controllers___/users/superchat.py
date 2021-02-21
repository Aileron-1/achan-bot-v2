from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime
import requests
from io import BytesIO
import asyncio
import aiohttp

class Superchat:
    def __init__(self):
        self.colours = ['blue', 'teal', 'yellow', 'orange', 'magenta']

    @staticmethod
    def wrap_text(text, width, font):
        text_lines = []
        text_line = []
        text = text.replace('\n', ' [br] ')
        words = text.split()
        font_size = font.getsize(text)

        for word in words:
            if word == '[br]':
                text_lines.append(' '.join(text_line))
                text_line = []
                continue
            text_line.append(word)
            w, h = font.getsize(' '.join(text_line))
            if w > width:
                text_line.pop()
                text_lines.append(' '.join(text_line))
                text_line = [word]

        if len(text_line) > 0:
            text_lines.append(' '.join(text_line))
        '''
        if len(text_lines) > 2:
            text_lines = text_lines[0:2]'''

        return '\n'.join(text_lines)

    def create_superchat(self, username, profilepic, amount, description):
        currency = 'H¥'
        # Determine sc type folder
        if len(description) > 0:
            overlay_path = "./resources/sc-reg/"  # Change to use relative to module later
        else:
            overlay_path = "./resources/sc-sml/"
        # Determine sc color file
        overlay_path += self.determine_color(int(amount))+'.png'

        # Load them up
        sc = Image.open(overlay_path)
        base = Image.new('RGBA',sc.size)

        prof = profilepic
        resized = prof.resize((36,36))

        base.paste(resized, (14, 7), resized)
        base.paste(sc,(0,0), sc)

        txt = Image.new('RGBA', base.size, (255,255,255,0))
        draw = ImageDraw.Draw(txt)
        font_reg = ImageFont.truetype("./resources/NotoSansCJKjp-Regular.otf", 14)
        font_bold = ImageFont.truetype("./resources/NotoSansCJKjp-Bold.otf", 15)

        draw.text((64, 4), username, font=font_reg, fill=(255,255,255,178))
        draw.text((64, 22), currency+amount, font=font_bold)
        draw.text((14, 54), self.wrap_text(description, 300, font_reg), font=font_reg, fill=(255,255,255,255))

        combined = Image.alpha_composite(base, txt)

        return combined

    @staticmethod
    def save(image):
        filename = 'out/'+datetime.now().strftime('%Y%m%d%H%M%S')+'.png'
        image.save(filename)
        return filename

    @staticmethod
    def determine_color(amount):
        color = 'blue'
        if amount < 300:
            color = 'blue'
        elif amount < 500:
            color = 'turquoise'
        elif amount < 1000:
            color = 'cyan'
        elif amount < 2000:
            color = 'yellow'
        elif amount < 5000:
            color = 'orange'
        elif amount < 10000:
            color = 'magenta'
        elif amount >= 10000:
            color = 'red'
        return color

    @asyncio.coroutine
    async def get_from_url(self, url):
        url = str(url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                img_data = await response.read()
                img = Image.open(BytesIO(img_data)).convert("RGBA")
                return img

if __name__ == '__main__':
    sc = Superchat()
    dl = sc.get_from_url('https://cdn.discordapp.com/emojis/292735742906728448.png')
    img = sc.create_superchat('Aileron', dl, '50', 'Otsukaresamadeshita!')
    img.show()
    #print(sc.save(img))
