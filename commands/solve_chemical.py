from Core.core import *
from commands.stupidAI.tools import ChemicalEquations as Ce
from bs4 import BeautifulSoup as bs
from PIL import Image
import io
import requests
import tempfile


def dothis(msg: Message):
    img, url = Ce.solve_equation(Ce.is_equation(msg.text))
    if img and url:
        ff = requests.get(img)
        img = Image.open(io.BytesIO(ff.content))
        w, h = img.size
        if w / h < 20:
            hn = w // 20 + 20
            a = Image.new('RGB', (w, hn), (255, 255, 255))
            a.paste(img, (0, (hn - h) // 2))
            img = a
        f = tempfile.NamedTemporaryFile(
            dir='temp\\', suffix='.png', delete=False,)
        f.close()
        img.save(f.name, 'PNG')
        photo = msg.cls.upload_photo(f.name, msg.userid)
        os.remove(f.name)
        res = requests.get(url)
        res.encoding = 'utf-8'
        text = bs(res.content, 'html.parser').find(
            'div', {'class': 'reactBody'}).contents[0].strip()
        print(text, photo)
        return text, photo
    else:
        return 'Реакции не найдено'


def main():
    return ("solve_chemical",
            "solchem",
            dothis,
            'solchem {химическое уравнение}\nРешить зимическое уравнение',
            0,
            None,
            'решение химических уравнений'), None, None
