import json

import zhconv
import re
import os
import argparse

from peewee import *


class PoetryModel:
    def __init__(self, title, content, author, dynasty):
        self.title = title
        self.content = content
        self.author = author
        self.dynasty = dynasty


class PoetryExtratorDef:
    def __init__(
        self, matcher, titleGetter, contentGetter, authorGetter, dynastyGetter, name
    ):
        self.matcher_ = matcher
        self.titleGetter_ = titleGetter
        self.contentGetter_ = contentGetter
        self.authorGetter_ = authorGetter
        self.dynastyGetter_ = dynastyGetter
        self.name_ = name

    def match(self, path):
        return self.matcher_(path)

    def name(self):
        return self.name_

    def createPoetry(self, data):
        return PoetryModel(
            self.titleGetter_(data),
            self.contentGetter_(data),
            self.authorGetter_(data),
            self.dynastyGetter_(data),
        )


caocaoDef = PoetryExtratorDef(
    lambda path: path.endswith("caocao.json"),
    lambda item: item["title"],
    lambda item: "\n".join(list(item["paragraphs"])),
    lambda _: "曹操",
    lambda _: "三国",
    "曹操诗集",
)


chuciDef = PoetryExtratorDef(
    lambda path: path.endswith("chuci.json"),
    lambda item: item["title"],
    lambda item: "\n".join(list(item["content"])),
    lambda item: item["author"],
    lambda _: "战国",
    "楚辞",
)


nalanDef = PoetryExtratorDef(
    lambda path: path.endswith("纳兰性德.json"),
    lambda item: item["title"],
    lambda item: "\n".join(list(item["para"])),
    lambda item: item["author"],
    lambda _: "清",
    "纳兰性德",
)


peotryTangDef = PoetryExtratorDef(
    lambda path: re.match(r".*全唐诗[/\\]poet\.tang\.\d+\.json", path) != None
    or path.endswith("唐诗三百首.json"),
    lambda item: item["title"],
    lambda item: "\n".join(list(item["paragraphs"])),
    lambda item: item["author"],
    lambda _: "唐",
    "全唐诗",
)


peotrySongDef = PoetryExtratorDef(
    lambda path: re.match(r".*全唐诗[/\\]poet\.song\.\d+\.json", path) != None,
    lambda item: item["title"],
    lambda item: "\n".join(list(item["paragraphs"])),
    lambda item: item["author"],
    lambda _: "宋",
    "全唐诗",
)


shijingDef = PoetryExtratorDef(
    lambda path: path.endswith("shijing.json"),
    lambda item: item["title"],
    lambda item: "\n".join(list(item["content"])),
    lambda _: "",
    lambda _: "",
    "诗经",
)

peotrySong300Def = PoetryExtratorDef(
    lambda path: path.endswith("宋词三百首.json"),
    lambda item: item["rhythmic"],
    lambda item: "\n".join(list(item["paragraphs"])),
    lambda item: item["author"],
    lambda _: "宋",
    "宋词三百首",
)

peotryTang300Def = PoetryExtratorDef(
    lambda path: path.endswith("唐诗三百首.json"),
    lambda item: item["title"],
    lambda item: "\n".join(list(item["paragraphs"])),
    lambda item: item["author"],
    lambda _: "唐",
    "唐诗三百首",
)

shijingDef = PoetryExtratorDef(
    lambda path: path.endswith("shijing.json"),
    lambda item: item["title"],
    lambda item: "\n".join(list(item["content"])),
    lambda _: "",
    lambda _: "",
    "诗经",
)

peotryShuiMoTangDef = PoetryExtratorDef(
    lambda path: path.endswith("shuimotangshi.json"),
    lambda item: item["title"],
    lambda item: "\n".join(list(item["paragraphs"])),
    lambda item: item["author"],
    lambda _: "唐",
    "水墨唐诗",
)


peotrySongCiDef = PoetryExtratorDef(
    lambda path: path.endswith("宋词三百首.json")
    or re.match(r".*宋词[/\\]ci\.song\.\d+\.json", path) != None,
    lambda item: item["rhythmic"],
    lambda item: "\n".join(list(item["paragraphs"])),
    lambda item: item["author"],
    lambda _: "宋",
    "宋词",
)

peotryHuaJianJiDef = PoetryExtratorDef(
    lambda path: re.match(r".*huajianji-[\d+x]-juan\.json", path) != None,
    lambda item: item["rhythmic"],
    lambda item: "\n".join(list(item["paragraphs"])),
    lambda item: item["author"],
    lambda _: "五代",
    "五代诗词",
)

peotryNangTangDef = PoetryExtratorDef(
    lambda path: re.match(r".*nangtang[/\\]poetrys\.json", path) != None,
    lambda item: item["rhythmic"],
    lambda item: "\n".join(list(item["paragraphs"])),
    lambda item: item["author"],
    lambda _: "五代 南唐",
    "五代诗词",
)

peotryYuanQuDef = PoetryExtratorDef(
    lambda path: path.endswith("yuanqu.json"),
    lambda item: item["title"],
    lambda item: "\n".join(list(item["paragraphs"])),
    lambda item: item["author"],
    lambda _: "元",
    "元曲",
)


# global sqlite db
db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db


class PoetryDbModel(BaseModel):
    class Meta:
        table_name = "poetry"

    id = BigAutoField()
    title = CharField()
    content = CharField()
    author = CharField()
    dynasty = CharField()


def convert_chinese_poetry(poetry: PoetryDbModel,lang: str) -> PoetryDbModel:
    return PoetryDbModel(
        title=zhconv.convert(poetry.title, lang),
        content=zhconv.convert(poetry.content, lang),
        author=zhconv.convert(poetry.author, lang),
        dynasty=zhconv.convert(poetry.dynasty, lang),
    )


def iter_json_file(path):
    files = os.walk(path)
    for dir, _, filenames in files:
        for name in filenames:
            if name.lower().endswith(".json"):
                yield dir + os.sep + name


def get_json_elements(path):
    with open(path, encoding="utf-8") as json_file:
        return json.load(json_file)


def iter_poetry(defs: list[PoetryExtratorDef], path: str):
    for file in iter_json_file(path):
        for d in defs:
            if d.match(file):
                for item in get_json_elements(file):
                    try:
                        yield d.createPoetry(item)
                    except:
                        print("load %s failed from path %s" % (item, file))
                break


if __name__ == "__main__":
    all_defs = [
        caocaoDef,
        chuciDef,
        nalanDef,
        peotryTangDef,
        peotrySongDef,
        shijingDef,
        peotryShuiMoTangDef,
        peotrySongCiDef,
        peotryHuaJianJiDef,
        peotryNangTangDef,
        peotryYuanQuDef,
        peotryTang300Def,
        peotrySong300Def
    ]

    def_names = "\n".join(map(lambda i:i.name(), list(all_defs)))

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="chinese-poetry",help="path of chinese-poetry repository")
    parser.add_argument("-o","--outdb", default="poetry.db",help="name of output database")
    parser.add_argument("-b","--batch", default=1000, type=int, help="batch size")
    parser.add_argument("-l","--lang", default="zh-cn", help="convert poetry,all possible values: zh-cn(default), zh-tw, zh-hk, zh-sg, zh-hans, zh-hant")
    parser.add_argument("-a","--append-poetry",action="append", help="add poetry to db. poetry list: %s" % def_names)
    parser.add_argument("-C","--clear",action="store_true",default=False,help="delete the database file if exists")
    parser.add_argument("-A","--all",action="store_true",default=False,help="add all poetry to db")
    args = parser.parse_args()

    defs = []

    if args.all:
        defs = all_defs
    else:
        for poetry in args.append_poetry:
            for def_ in all_defs:
                if def_.name() == poetry and def_.name() not in defs:
                    defs.append(def_)

    if len(defs) <= 0:
        print("No poetry found !, Please use -a or --append-poetry to add the collection of poems you want to save in the database")
        print("all poems: %s" % def_names)

    if args.clear and os.path.exists(args.outdb):
        os.remove(args.outdb)

    db.init(args.outdb)
    db.connect()
    db.create_tables([PoetryDbModel])

    batch_buff = []
    for p in iter_poetry(defs,args.path):
        batch_buff.append(convert_chinese_poetry(p,args.lang))
        if len(batch_buff) >= args.batch:
            with db.atomic():
                PoetryDbModel.bulk_create(batch_buff, args.batch)
            batch_buff.clear()

    # remain buff
    if len(batch_buff) > 0:
        with db.atomic():
            PoetryDbModel.bulk_create(batch_buff, args.batch)
        batch_buff.clear()

    db.close()
    print("complete!")
