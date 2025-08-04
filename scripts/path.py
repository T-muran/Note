import datetime
import html
import logging
import posixpath
import pypinyin
import re

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import event_priority
from mkdocs.structure.files import File, Files
from mkdocs.structure.nav import Navigation
from mkdocs.structure.nav import Section
from mkdocs.structure.pages import Page
from mkdocs.utils import meta, get_relative_url
from string import ascii_letters
from typing import Callable, Union

class FileLinkNode(object):
    def __init__(self, file: File):
        self.file = file
        self.prev: FileLinkNode = None
        self.next: FileLinkNode = None

    # 将自己插入到 node 后面
    def insert_after(self, node: "FileLinkNode"):
        self.prev = node
        self.next = node.next
        if node.next:
            node.next.prev = self
        node.next = self

    def remove(self):
        if self.prev:
            self.prev.next = self.next
        if self.next:
            self.next.prev = self.prev

class FileLinkList(object):
    def __init__(self, file: File):
        self.file = file

        # 自己指向其他文章的链接
        # key 是其他文章的 src_uri
        # value 是插入到其他文章的 inverseLinks 中的节点
        self.links: dict[str, FileLinkNode] = {}

        # 其他文章指向自己的链接，使用有头结点的链表保存
        self.inverse_links = FileLinkNode(None)

    def clear_links(self):
        for l in self.links.values():
            l.remove()
        self.links.clear()

FOLDER_MD_VAULT = 'md_vault'
FOLDER_ATTACHMENT = 'attachments'
FOLDER_BLACKLIST = {
    '临时',
    'templates'
}

wiki_link_name_map: dict[str, File] = {}         # key 是文件名，有扩展名
wiki_link_path_map: dict[str, FileLinkList] = {} # key 是 src_uri
notes_sorted_by_date: list[File] = []            # 所有笔记，根据时间倒序保存
log = logging.getLogger('mkdocs.plugins')

def set_file_dest_uri(f: File, value: Union[str, Callable[[str], str]]):
    f.dest_uri = value if isinstance(value, str) else value(f.dest_uri)

    def delattr_if_exists(obj, attr):
        if hasattr(obj, attr):
            delattr(obj, attr)

    # 删掉 cached_property 的缓存
    delattr_if_exists(f, 'url')
    delattr_if_exists(f, 'abs_dest_path')
    
def process_md_note(f: File) -> bool:
    _, frontmatter = meta.get_data(f.content_string)

    # 如果不发布的话，不进行后面的检查
    if not frontmatter.get('publish', False):
        log.info('MD document \'%s\' is not published, skipping', f.src_uri)
        return False

    if 'date' not in frontmatter:
        log.error('MD document \'%s\' does not have a date', f.src_uri)
        return False

    date = frontmatter['date']

    if not isinstance(date, datetime.datetime):
        log.error('MD document \'%s\' has an invalid date', f.src_uri)
        return False

    if 'permalink' not in frontmatter:
        log.error('MD document \'%s\' does not have a permalink', f.src_uri)
        return False

    permalink = frontmatter['permalink']

    if not isinstance(permalink, str):
        log.error('MD document \'%s\' has an invalid permalink', f.src_uri)
        return False

    setattr(f, 'note_date', date)

    if not f.use_directory_urls:
        set_file_dest_uri(f, posixpath.join('p', permalink + '.html'))
    else:
        set_file_dest_uri(f, posixpath.join('p', permalink, 'index.html'))

    return True

@event_priority(100) # 放在最前面执行，不要处理其他插件生成的文件
def on_files(files: Files, config: MkDocsConfig):
    wiki_link_name_map.clear()
    wiki_link_path_map.clear()
    notes_sorted_by_date.clear()

    invalid_files: list[File] = []

    for f in files:
        path_names = f.src_uri.split('/')
        log.info('Processing %s', f.src_uri)

        # 忽略 obsidian-vault 文件夹以外的文件；路径中至少有一个斜杠，所以长度至少为 2
        if len(path_names) < 2 or path_names[0] != FOLDER_MD_VAULT:
            continue

        # 删除特定目录的文件；路径中至少有两个斜杠，所以长度至少为 3
        if len(path_names) < 3 or path_names[1] in FOLDER_BLACKLIST:
            invalid_files.append(f)
            continue

        if path_names[1] == FOLDER_ATTACHMENT:
            process_obsidian_attachment(f)
        elif f.is_documentation_page() and process_md_note(f):
            notes_sorted_by_date.append(f)
        else:
            invalid_files.append(f)
            continue

        wiki_link_name_map[posixpath.basename(f.src_uri)] = f
        wiki_link_path_map[f.src_uri] = FileLinkList(f)

    notes_sorted_by_date.sort(key=lambda f: f.note_date, reverse=True)
    log.info('Found %d valid documents', len(notes_sorted_by_date))

    for f in invalid_files:
        files.remove(f)

    return files