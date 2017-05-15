import requests
from bs4 import BeautifulSoup
import bs4
import sqlite3
from typing import NewType, Callable, Set
import re

# Type alias
Url = str
Tag = NewType('Tag', bs4.element.Tag)

# Compiled regex
skill_star_re = re.compile(r"(?<=☆)\d")


class Skill:
    name: str
    effect: str
    category: str
    weapons = dict(map(lambda name, inheritable: (name, inheritable),
                       ['剣', '槍', '斧', '赤竜', '青竜', '緑竜', '弓', '暗器', '杖', '赤魔導書', '青魔導書', '緑魔導書'],
                       [False] * 15))
    moves = dict(map(lambda name, inheritable: (name, inheritable),
                       ['歩兵', '重装', '飛行', '騎馬'],
                       [False] * 5))

    def __init__(self):
        self.weapons = Skill.weapons.copy()
        self.moves = Skill.moves.copy()
        self.characters = {}


def fuga(tag_id: int) -> Callable[[Tag], bool]:
    def hoge(element: Tag) -> bool:
        return hasattr(element, 'get') and element.get('id') == str(tag_id)
    return hoge


def fetch_skill(url: Url):
    skill = Skill()

    soup = BeautifulSoup(requests.get(url).content, 'lxml')
    article = filter(lambda e: isinstance(e, bs4.element.Tag), soup.select('.article')[0].children)

    # 継承可能武器種・移動タイプを取得
    hoge = fuga(3)
    while not hoge(next(article)):
        pass

    first_element = next(article)
    if first_element.name == 'table':
        weapons = first_element
        for w in map(lambda img: img.get('alt').strip(), weapons.find_all('img')):
            skill.weapons[w] = True

        moves = next(article)
        for m in map(lambda img: img.get('alt').strip(), moves.find_all('img')):
            skill.moves[m] = True

    # 効果・分類を取得
    hoge = fuga(1)
    while not hoge(next(article)):
        pass

    effect_tags = map(lambda td: td.get_text().strip(), next(article).find_all('td'))
    skill.effect = next(effect_tags)
    skill.category = next(effect_tags)

    # 習得キャラを取得
    hoge = fuga(2)
    while not hoge(next(article)):
        pass

    character_tags = next(article).find_all('tr')[1:]
    for c in character_tags:
        key = c.img.get('alt')
        value = skill_star_re.search(c.text).group(0)
        skill.characters[key] = value

    return skill


def main() -> None:
    # conn = sqlite3.connect('altema.db')
    skill = fetch_skill("http://altema.jp/fe-heroes/skill/1714")
    print(skill)

main()