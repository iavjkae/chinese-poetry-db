# ChinesePoetryDB

一个将 [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) 仓库的古诗文数据输出到数据库的小工具

## 局限性

当前仅支持SQLite 数据库，但可以轻松扩展到其他数据库

支持输出的诗集

+ 曹操诗集
+ 楚辞
+ 纳兰性德
+ 全唐诗
+ 诗经
+ 水墨唐诗
+ 宋词
+ 五代诗词
+ 元曲
+ 唐诗三百首
+ 宋词三百首

输出的数据表格式

表名 `poetry`

| 列名    | 说明 |
| ------- | ---- |
| title   | 标题 |
| content | 内容 |
| author  | 作者 |
| dynasty | 朝代 |

## 快速开始

仓库将 `chinese-poetry` 作为submodule 包含了，没发现 `chinese-poetry`有比较靠谱的分支或tag来标识版本，所以默认使用 `chinese-poetry` 的`master` 分支了，这可能会导致兼容问题，当然，也可以下载 `chinese-poetry` 项目，指定路径使用。

```bash

# 初始化子模块
git submodule init

```

```bash

# 安装依赖
pip install -r requirements.txt

```

```bash

# 唐诗三百首 输出到 peotry.db
python3 main.py -a 唐诗三百首

# 指定 输出 db文件
python3 main.py -a 唐诗三百首 -o p.db

# 输出多个诗集
python3 main.py -a 唐诗三百首 -a 宋词三百首

# 输出全部诗集
python3 main.py -A
# 或
python3 main.py --all

# 指定 chinese-poetry 路径
python3 main.py --path "path to chinese-poetry"

# 更多食用方法
python3 main.py -h

```

## 可能下一步的改进?

+ 支持更多数据库
+ 支持自定义输出数据表的格式
+ 尽可能输出更多信息 比如作者信息
+ ....

可能性很小

## 感谢

[chinese-poetry](https://github.com/chinese-poetry/chinese-poetry)
[zhconv](https://github.com/gumblex/zhconv)
[peewee](https://github.com/coleifer/peewee)
