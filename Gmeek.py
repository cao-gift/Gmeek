# -*- coding: utf-8 -*-
import os
import re
import json
import time
import datetime
import shutil
import urllib
import requests
import argparse
import html
import hashlib
import struct
from concurrent.futures import ThreadPoolExecutor
from github import Github
from xpinyin import Pinyin
from feedgen.feed import FeedGenerator
from jinja2 import Environment, FileSystemLoader
from transliterate import translit
from collections import OrderedDict
######################################################################################
i18n={"Search":"Search","switchTheme":"switch theme","home":"home","comments":"comments","run":"run ","days":" day(s)","Previous":"Previous","Next":"Next"}
i18nCN={"Search":"搜索","switchTheme":"切换主题","home":"首页","comments":"评论","run":"网站运行 ","days":" 天","Previous":"上一页","Next":"下一页"}
i18nRU={"Search":"Поиск","switchTheme": "Сменить тему","home":"Главная","comments":"Комментарии ","run":" работает ","days":" дней","Previous":"Предыдущая","Next":"Следующая"}
IconBase={
    "post":"M0 3.75C0 2.784.784 2 1.75 2h12.5c.966 0 1.75.784 1.75 1.75v8.5A1.75 1.75 0 0 1 14.25 14H1.75A1.75 1.75 0 0 1 0 12.25Zm1.75-.25a.25.25 0 0 0-.25.25v8.5c0 .138.112.25.25.25h12.5a.25.25 0 0 0 .25-.25v-8.5a.25.25 0 0 0-.25-.25ZM3.5 6.25a.75.75 0 0 1 .75-.75h7a.75.75 0 0 1 0 1.5h-7a.75.75 0 0 1-.75-.75Zm.75 2.25h4a.75.75 0 0 1 0 1.5h-4a.75.75 0 0 1 0-1.5Z",
    "link":"m7.775 3.275 1.25-1.25a3.5 3.5 0 1 1 4.95 4.95l-2.5 2.5a3.5 3.5 0 0 1-4.95 0 .751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018 1.998 1.998 0 0 0 2.83 0l2.5-2.5a2.002 2.002 0 0 0-2.83-2.83l-1.25 1.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042Zm-4.69 9.64a1.998 1.998 0 0 0 2.83 0l1.25-1.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-1.25 1.25a3.5 3.5 0 1 1-4.95-4.95l2.5-2.5a3.5 3.5 0 0 1 4.95 0 .751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018 1.998 1.998 0 0 0-2.83 0l-2.5 2.5a1.998 1.998 0 0 0 0 2.83Z",
    "about":"M10.561 8.073a6.005 6.005 0 0 1 3.432 5.142.75.75 0 1 1-1.498.07 4.5 4.5 0 0 0-8.99 0 .75.75 0 0 1-1.498-.07 6.004 6.004 0 0 1 3.431-5.142 3.999 3.999 0 1 1 5.123 0ZM10.5 5a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z",
    "sun":"M8 10.5a2.5 2.5 0 100-5 2.5 2.5 0 000 5zM8 12a4 4 0 100-8 4 4 0 000 8zM8 0a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0V.75A.75.75 0 018 0zm0 13a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 018 13zM2.343 2.343a.75.75 0 011.061 0l1.06 1.061a.75.75 0 01-1.06 1.06l-1.06-1.06a.75.75 0 010-1.06zm9.193 9.193a.75.75 0 011.06 0l1.061 1.06a.75.75 0 01-1.06 1.061l-1.061-1.06a.75.75 0 010-1.061zM16 8a.75.75 0 01-.75.75h-1.5a.75.75 0 010-1.5h1.5A.75.75 0 0116 8zM3 8a.75.75 0 01-.75.75H.75a.75.75 0 010-1.5h1.5A.75.75 0 013 8zm10.657-5.657a.75.75 0 010 1.061l-1.061 1.06a.75.75 0 11-1.06-1.06l1.06-1.06a.75.75 0 011.06 0zm-9.193 9.193a.75.75 0 010 1.06l-1.06 1.061a.75.75 0 11-1.061-1.06l1.06-1.061a.75.75 0 011.061 0z",
    "moon":"M9.598 1.591a.75.75 0 01.785-.175 7 7 0 11-8.967 8.967.75.75 0 01.961-.96 5.5 5.5 0 007.046-7.046.75.75 0 01.175-.786zm1.616 1.945a7 7 0 01-7.678 7.678 5.5 5.5 0 107.678-7.678z",
    "search":"M15.7 13.3l-3.81-3.83A5.93 5.93 0 0 0 13 6c0-3.31-2.69-6-6-6S1 2.69 1 6s2.69 6 6 6c1.3 0 2.48-.41 3.47-1.11l3.83 3.81c.19.2.45.3.7.3.25 0 .52-.09.7-.3a.996.996 0 0 0 0-1.41v.01zM7 10.7c-2.59 0-4.7-2.11-4.7-4.7 0-2.59 2.11-4.7 4.7-4.7 2.59 0 4.7 2.11 4.7 4.7 0 2.59-2.11 4.7-4.7 4.7z",
    "rss":"M2.002 2.725a.75.75 0 0 1 .797-.699C8.79 2.42 13.58 7.21 13.974 13.201a.75.75 0 0 1-1.497.098 10.502 10.502 0 0 0-9.776-9.776.747.747 0 0 1-.7-.798ZM2.84 7.05h-.002a7.002 7.002 0 0 1 6.113 6.111.75.75 0 0 1-1.49.178 5.503 5.503 0 0 0-4.8-4.8.75.75 0 0 1 .179-1.489ZM2 13a1 1 0 1 1 2 0 1 1 0 0 1-2 0Z",
    "upload":"M2.75 14A1.75 1.75 0 0 1 1 12.25v-2.5a.75.75 0 0 1 1.5 0v2.5c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25v-2.5a.75.75 0 0 1 1.5 0v2.5A1.75 1.75 0 0 1 13.25 14Z M11.78 4.72a.749.749 0 1 1-1.06 1.06L8.75 3.811V9.5a.75.75 0 0 1-1.5 0V3.811L5.28 5.78a.749.749 0 1 1-1.06-1.06l3.25-3.25a.749.749 0 0 1 1.06 0l3.25 3.25Z",
    "github":"M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z",
    "home":"M6.906.664a1.749 1.749 0 0 1 2.187 0l5.25 4.2c.415.332.657.835.657 1.367v7.019A1.75 1.75 0 0 1 13.25 15h-3.5a.75.75 0 0 1-.75-.75V9H7v5.25a.75.75 0 0 1-.75.75h-3.5A1.75 1.75 0 0 1 1 13.25V6.23c0-.531.242-1.034.657-1.366l5.25-4.2Zm1.25 1.171a.25.25 0 0 0-.312 0l-5.25 4.2a.25.25 0 0 0-.094.196v7.019c0 .138.112.25.25.25H5.5V8.25a.75.75 0 0 1 .75-.75h3.5a.75.75 0 0 1 .75.75v5.25h2.75a.25.25 0 0 0 .25-.25V6.23a.25.25 0 0 0-.094-.195Z",
    "sync":"M1.705 8.005a.75.75 0 0 1 .834.656 5.5 5.5 0 0 0 9.592 2.97l-1.204-1.204a.25.25 0 0 1 .177-.427h3.646a.25.25 0 0 1 .25.25v3.646a.25.25 0 0 1-.427.177l-1.38-1.38A7.002 7.002 0 0 1 1.05 8.84a.75.75 0 0 1 .656-.834ZM8 2.5a5.487 5.487 0 0 0-4.131 1.869l1.204 1.204A.25.25 0 0 1 4.896 6H1.25A.25.25 0 0 1 1 5.75V2.104a.25.25 0 0 1 .427-.177l1.38 1.38A7.002 7.002 0 0 1 14.95 7.16a.75.75 0 0 1-1.49.178A5.5 5.5 0 0 0 8 2.5Z",
    "copy":"M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 0 1 0 1.5h-1.5a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-1.5a.75.75 0 0 1 1.5 0v1.5A1.75 1.75 0 0 1 9.25 16h-7.5A1.75 1.75 0 0 1 0 14.25Z M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0 1 14.25 11h-7.5A1.75 1.75 0 0 1 5 9.25Zm1.75-.25a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-7.5a.25.25 0 0 0-.25-.25Z",
    "check":"M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"
}
######################################################################################
class GMEEK():
    def __init__(self,options):
        self.options=options
        
        self.root_dir='docs/'
        self.static_dir='static/'
        self.post_folder='post/'
        self.backup_dir='backup/'
        self.post_dir=self.root_dir+self.post_folder
        self.cache_dir=os.environ.get("GMEEK_CACHE_DIR", os.path.join(os.path.expanduser("~"), ".cache", "gmeek"))
        self.markdown_cache_dir=os.path.join(self.cache_dir, "markdown-v1")
        self.image_cache_dir=os.path.join(self.cache_dir, "image-dimensions-v1")
        os.makedirs(self.markdown_cache_dir, exist_ok=True)
        os.makedirs(self.image_cache_dir, exist_ok=True)

        user = Github(self.options.github_token)
        self.repo = self.get_repo(user, options.repo_name)
        self.feed = FeedGenerator()
        self.oldFeedString=''

        self.labelColorDict=json.loads('{}')
        for label in self.repo.get_labels():
            self.labelColorDict[label.name]='#'+label.color
        print(self.labelColorDict)
        self.defaultConfig()
        
    def cleanFile(self):
        workspace_path = os.environ.get('GITHUB_WORKSPACE')
        if os.path.exists(workspace_path+"/"+self.backup_dir):
            shutil.rmtree(workspace_path+"/"+self.backup_dir)

        if os.path.exists(workspace_path+"/"+self.root_dir):
            shutil.rmtree(workspace_path+"/"+self.root_dir)

        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)
            
        if os.path.exists(self.root_dir):
            shutil.rmtree(self.root_dir)

        os.mkdir(self.backup_dir)
        os.mkdir(self.root_dir)
        os.mkdir(self.post_dir)

        if os.path.exists(self.static_dir):
            for item in os.listdir(self.static_dir):
                src = os.path.join(self.static_dir, item)
                dst = os.path.join(self.root_dir, item)
                if os.path.isfile(src):
                    shutil.copy(src, dst)
                    print(f"Copied {item} to docs")
                elif os.path.isdir(src):
                    shutil.copytree(src, dst)
                    print(f"Copied directory {item} to docs")
        else:
            print("static does not exist")

    def defaultConfig(self):
        dconfig={"singlePage":[],"startSite":"","filingNum":"","onePageListNum":15,"commentLabelColor":"#006b75","yearColorList":["#bc4c00", "#0969da", "#1f883d", "#A333D0"],"i18n":"CN","themeMode":"manual","dayTheme":"light","nightTheme":"dark","urlMode":"pinyin","script":"","style":"","head":"","indexScript":"","indexStyle":"","bottomText":"","showPostSource":1,"iconList":{},"UTC":+8,"rssSplit":"sentence","exlink":{},"needComment":1,"allHead":"","imageCaptcha":0}
        config=json.loads(open('config.json', 'r', encoding='utf-8').read())
        self.blogBase={**dconfig,**config}.copy()
        self.blogBase["postListJson"]=json.loads('{}')
        self.blogBase["singeListJson"]=json.loads('{}')
        self.blogBase["labelColorDict"]=self.labelColorDict
        if "displayTitle" not in self.blogBase:
            self.blogBase["displayTitle"]=self.blogBase["title"]

        if "faviconUrl" not in self.blogBase:
            self.blogBase["faviconUrl"]=self.blogBase["avatarUrl"]

        if "ogImage" not in self.blogBase:
            self.blogBase["ogImage"]=self.blogBase["avatarUrl"]

        if "primerCSS" not in self.blogBase:
            self.blogBase["primerCSS"]="<link href='https://mirrors.sustech.edu.cn/cdnjs/ajax/libs/Primer/21.0.7/primer.css' rel='stylesheet' />"

        if "homeUrl" not in self.blogBase:
            if str(self.repo.name).lower() == (str(self.repo.owner.login) + ".github.io").lower():
                self.blogBase["homeUrl"] = f"https://{self.repo.name}"
            else:
                self.blogBase["homeUrl"] = f"https://{self.repo.owner.login}.github.io/{self.repo.name}"
        print("GitHub Pages URL: ", self.blogBase["homeUrl"])

        if self.blogBase["i18n"]=="CN":
            self.i18n=i18nCN
        elif self.blogBase["i18n"]=="RU":
            self.i18n=i18nRU
        else:
            self.i18n=i18n
        
        self.TZ=datetime.timezone(datetime.timedelta(hours=self.blogBase["UTC"]))

    def get_repo(self,user:Github, repo:str):
        return user.get_repo(repo)

    def markdown2html(self, mdstr):
        cache_key=hashlib.sha256(("gfm-v1\0"+mdstr).encode("utf-8")).hexdigest()
        cache_file=os.path.join(self.markdown_cache_dir, cache_key+".html")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    print("markdown cache hit: {}".format(cache_key[:12]))
                    return f.read()
            except OSError:
                pass

        payload = {"text": mdstr, "mode": "gfm"}
        headers = {"Authorization": "token {}".format(self.options.github_token)}
        try:
            response = requests.post("https://api.github.com/markdown", json=payload, headers=headers, timeout=(5, 30))
            response.raise_for_status()  # Raises an exception if status code is not 200
            output=response.text
            temp_file=cache_file+".{}.tmp".format(os.getpid())
            try:
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(output)
                os.replace(temp_file, cache_file)
            except OSError:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            return output
        except requests.RequestException as e:
            raise Exception("markdown2html error: {}".format(e))

    def imageDimensionsFromBytes(self, data):
        if len(data)>=24 and data.startswith(b"\x89PNG\r\n\x1a\n"):
            return struct.unpack(">II", data[16:24])
        if len(data)>=10 and data[:6] in (b"GIF87a", b"GIF89a"):
            return struct.unpack("<HH", data[6:10])
        if len(data)>=30 and data.startswith(b"RIFF") and data[8:12]==b"WEBP":
            if data[12:16]==b"VP8X":
                return (1+int.from_bytes(data[24:27], "little"), 1+int.from_bytes(data[27:30], "little"))
            if data[12:16]==b"VP8L" and data[20:21]==b"/":
                bits=int.from_bytes(data[21:25], "little")
                return ((bits & 0x3fff)+1, ((bits >> 14) & 0x3fff)+1)
            frame_header=data.find(b"\x9d\x01\x2a", 16)
            if frame_header!=-1 and len(data)>=frame_header+7:
                width, height=struct.unpack("<HH", data[frame_header+3:frame_header+7])
                return (width & 0x3fff, height & 0x3fff)
        if len(data)>=4 and data.startswith(b"\xff\xd8"):
            offset=2
            sof_markers={0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf}
            while offset+4<=len(data):
                if data[offset]!=0xff:
                    offset+=1
                    continue
                marker=data[offset+1]
                offset+=2
                if marker in (0xd8,0xd9) or 0xd0<=marker<=0xd7:
                    continue
                if offset+2>len(data):
                    break
                segment_length=struct.unpack(">H", data[offset:offset+2])[0]
                if segment_length<2 or offset+segment_length>len(data):
                    break
                if marker in sof_markers and segment_length>=7:
                    height, width=struct.unpack(">HH", data[offset+3:offset+7])
                    return (width, height)
                offset+=segment_length
        return None

    def getCachedImageDimensions(self, url):
        cache_key=hashlib.sha256(url.encode("utf-8")).hexdigest()
        cache_file=os.path.join(self.image_cache_dir, cache_key+".json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    dimensions=json.load(f)
                if isinstance(dimensions, list) and len(dimensions)==2:
                    return (int(dimensions[0]), int(dimensions[1]))
            except (OSError, ValueError, TypeError):
                pass
        return None

    def cacheImageDimensions(self, url, dimensions):
        cache_key=hashlib.sha256(url.encode("utf-8")).hexdigest()
        cache_file=os.path.join(self.image_cache_dir, cache_key+".json")
        temp_file=cache_file+".{}.tmp".format(os.getpid())
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(list(dimensions), f)
            os.replace(temp_file, cache_file)
        except OSError:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def getImageDimensions(self, urls):
        for url in urls:
            cached=self.getCachedImageDimensions(url)
            if cached:
                return cached

        for url in urls:
            if not re.match(r"^https?://", url, flags=re.IGNORECASE):
                continue
            try:
                with requests.get(
                    url,
                    headers={"Range":"bytes=0-262143", "Accept-Encoding":"identity"},
                    stream=True,
                    timeout=(3, 8)
                ) as response:
                    response.raise_for_status()
                    data=b""
                    for chunk in response.iter_content(chunk_size=32768):
                        data+=chunk
                        if len(data)>=262144:
                            break
                dimensions=self.imageDimensionsFromBytes(data)
                if dimensions and dimensions[0]>0 and dimensions[1]>0:
                    for candidate in urls:
                        self.cacheImageDimensions(candidate, dimensions)
                    return dimensions
            except requests.RequestException:
                continue
        return None

    def optimizePostImages(self, post_body):
        image_tags=list(re.finditer(r"<img\b[^>]*>", post_body, flags=re.IGNORECASE))
        if not image_tags:
            return post_body

        def get_attr(tag, name):
            match=re.search(r"\s"+re.escape(name)+r"\s*=\s*([\"'])(.*?)\1", tag, flags=re.IGNORECASE|re.DOTALL)
            return html.unescape(match.group(2)) if match else ""

        image_urls={}
        for match in image_tags:
            tag=match.group(0)
            if re.search(r"\swidth\s*=", tag, flags=re.IGNORECASE) and re.search(r"\sheight\s*=", tag, flags=re.IGNORECASE):
                continue
            urls=[]
            for name in ("data-canonical-src", "src"):
                url=get_attr(tag, name)
                if url and url not in urls:
                    urls.append(url)
            if urls:
                image_urls[tuple(urls)]=None

        if image_urls:
            with ThreadPoolExecutor(max_workers=min(8, len(image_urls))) as executor:
                dimensions=executor.map(self.getImageDimensions, image_urls.keys())
                image_urls=dict(zip(image_urls.keys(), dimensions))

        image_index=0
        def add_attributes(match):
            nonlocal image_index
            tag=match.group(0)
            is_priority=image_index==0
            image_index+=1
            attributes=[]
            if not re.search(r"\sloading\s*=", tag, flags=re.IGNORECASE):
                attributes.append('loading="{}"'.format("eager" if is_priority else "lazy"))
            if not re.search(r"\sdecoding\s*=", tag, flags=re.IGNORECASE):
                attributes.append('decoding="async"')
            if not re.search(r"\sfetchpriority\s*=", tag, flags=re.IGNORECASE):
                attributes.append('fetchpriority="{}"'.format("high" if is_priority else "low"))
            if not (re.search(r"\swidth\s*=", tag, flags=re.IGNORECASE) and re.search(r"\sheight\s*=", tag, flags=re.IGNORECASE)):
                urls=[]
                for name in ("data-canonical-src", "src"):
                    url=get_attr(tag, name)
                    if url and url not in urls:
                        urls.append(url)
                dimensions=image_urls.get(tuple(urls))
                if dimensions:
                    if not re.search(r"\swidth\s*=", tag, flags=re.IGNORECASE):
                        attributes.append('width="{}"'.format(dimensions[0]))
                    if not re.search(r"\sheight\s*=", tag, flags=re.IGNORECASE):
                        attributes.append('height="{}"'.format(dimensions[1]))
            if not attributes:
                return tag
            if tag.endswith("/>"):
                return tag[:-2]+" "+" ".join(attributes)+" />"
            return tag[:-1]+" "+" ".join(attributes)+">"

        return re.sub(r"<img\b[^>]*>", add_attributes, post_body, flags=re.IGNORECASE)

    def protectPostImages(self, post_body):
        tiny_pixel="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="

        def get_attr(tag, name):
            match=re.search(r"\s"+re.escape(name)+r"\s*=\s*([\"'])(.*?)\1", tag, flags=re.IGNORECASE|re.DOTALL)
            return html.unescape(match.group(2)) if match else ""

        def remove_attr(tag, name):
            pattern=r"\s+"+re.escape(name)+r"\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)"
            return re.sub(pattern, "", tag, flags=re.IGNORECASE|re.DOTALL)

        def protect_image(match):
            tag=match.group(0)
            original_src=(
                get_attr(tag, "data-esa-orig-src")
                or get_attr(tag, "data-canonical-src")
                or get_attr(tag, "src")
            )
            original_srcset=get_attr(tag, "data-esa-orig-srcset") or get_attr(tag, "srcset")

            for name in ("src", "srcset", "data-esa-orig-src", "data-esa-orig-srcset", "data-esa-img-locked"):
                tag=remove_attr(tag, name)

            attributes=[
                'src="{}"'.format(tiny_pixel),
                'data-esa-img-locked="1"'
            ]
            if original_src:
                attributes.append('data-esa-orig-src="{}"'.format(html.escape(original_src, quote=True)))
            if original_srcset:
                attributes.append('data-esa-orig-srcset="{}"'.format(html.escape(original_srcset, quote=True)))

            if tag.endswith("/>"):
                return tag[:-2]+" "+" ".join(attributes)+" />"
            return tag[:-1]+" "+" ".join(attributes)+">"

        return re.sub(r"<img\b[^>]*>", protect_image, post_body, flags=re.IGNORECASE)

    def renderHtml(self,template,blogBase,postListJson,htmlDir,icon):
        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        template = env.get_template(template)
        output = template.render(blogBase=blogBase,postListJson=postListJson,i18n=self.i18n,IconList=icon)
        f = open(htmlDir, 'w', encoding='UTF-8')
        f.write(output)
        f.close()

    def createPostHtml(self,issue):
        mdFileName=re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', issue["postTitle"])
        f = open(self.backup_dir+mdFileName+".md", 'r', encoding='UTF-8')
        post_body=self.markdown2html(f.read())
        f.close()
        postBase=self.blogBase.copy()

        if '<math-renderer' in post_body:
            post_body=re.sub(r'<math-renderer.*?>','',post_body)
            post_body=re.sub(r'</math-renderer>','',post_body)
            issue["script"]=issue["script"]+'<script>MathJax = {tex: {inlineMath: [["$", "$"]]}};</script><script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'
        
        if '<p class="markdown-alert-title">' in post_body:
            issue["style"]=issue["style"]+'<style>.markdown-alert{padding:0.5rem 1rem;margin-bottom:1rem;border-left:.25em solid var(--borderColor-default,var(--color-border-default));}.markdown-alert .markdown-alert-title {display:flex;font-weight:var(--base-text-weight-medium,500);align-items:center;line-height:1;}.markdown-alert>:first-child {margin-top:0;}.markdown-alert>:last-child {margin-bottom:0;}</style>'
            alerts = {
                'note': 'accent',
                'tip': 'success',
                'important': 'done',
                'warning': 'attention',
                'caution': 'danger'
            }

            for alert, style in alerts.items():
                if f'markdown-alert-{alert}' in post_body:
                    issue["style"] += (
                        f'<style>.markdown-alert.markdown-alert-{alert} {{'
                        f'border-left-color:var(--borderColor-{style}-emphasis, var(--color-{style}-emphasis));'
                        f'background-color:var(--color-{style}-subtle);}}'
                        f'.markdown-alert.markdown-alert-{alert} .markdown-alert-title {{'
                        f'color: var(--fgColor-{style},var(--color-{style}-fg));}}</style>'
                    )

        if '<code class="notranslate">Gmeek-html' in post_body:
            post_body = re.sub(r'<code class="notranslate">Gmeek-html(.*?)</code>', lambda match: html.unescape(match.group(1)), post_body, flags=re.DOTALL)

        post_body=self.optimizePostImages(post_body)
        protect_images=(
            self.blogBase.get("imageCaptcha", 0)==1
            and issue["labels"][0] not in self.blogBase["singlePage"]
        )
        if protect_images:
            post_body=self.protectPostImages(post_body)

        postBase["postTitle"]=issue["postTitle"]
        postBase["postUrl"]=self.blogBase["homeUrl"]+"/"+issue["postUrl"]
        postBase["description"]=issue["description"]
        postBase["ogImage"]=issue["ogImage"]
        postBase["postBody"]=post_body
        postBase["commentNum"]=issue["commentNum"]
        postBase["style"]=issue["style"]
        postBase["script"]=issue["script"]
        postBase["head"]=issue["head"]
        postBase["top"]=issue["top"]
        postBase["postSourceUrl"]=issue["postSourceUrl"]
        postBase["repoName"]=options.repo_name
        
        if issue["labels"][0] in self.blogBase["singlePage"]:
            postBase["bottomText"]=''

        if '<pre class="notranslate">' in post_body:
            keys=['sun','moon','sync','home','github','copy','check']
            if '<div class="highlight' in post_body:
                postBase["highlight"]=1
            else:
                postBase["highlight"]=2
        else:
            keys=['sun','moon','sync','home','github']
            postBase["highlight"]=0

        postIcon=dict(zip(keys, map(IconBase.get, keys)))
        self.renderHtml('post.html',postBase,{},issue["htmlDir"],postIcon)
        print("create postPage title=%s file=%s " % (issue["postTitle"],issue["htmlDir"]))

    def createPlistHtml(self):
        self.blogBase["postListJson"]=dict(sorted(self.blogBase["postListJson"].items(),key=lambda x:(x[1]["top"],x[1]["createdAt"]),reverse=True))#使列表由时间排序
        keys=list(OrderedDict.fromkeys(['sun', 'moon','sync', 'search', 'rss', 'upload', 'post'] + self.blogBase["singlePage"]))
        plistIcon={**dict(zip(keys, map(IconBase.get, keys))),**self.blogBase["iconList"]}
        keys=['sun','moon','sync','home','search','post']
        tagIcon=dict(zip(keys, map(IconBase.get, keys)))

        postNum=len(self.blogBase["postListJson"])
        pageFlag=0
        while True:
            topNum=pageFlag*self.blogBase["onePageListNum"]
            print("topNum=%d postNum=%d"%(topNum,postNum))
            if postNum<=self.blogBase["onePageListNum"]:
                if pageFlag==0:
                    onePageList=dict(list(self.blogBase["postListJson"].items())[:postNum])
                    htmlDir=self.root_dir+"index.html"
                    self.blogBase["prevUrl"]="disabled"
                    self.blogBase["nextUrl"]="disabled"
                else:
                    onePageList=dict(list(self.blogBase["postListJson"].items())[topNum:topNum+postNum])
                    htmlDir=self.root_dir+("page%d.html" % (pageFlag+1))
                    if pageFlag==1:
                        self.blogBase["prevUrl"]="/index.html"
                    else:
                        self.blogBase["prevUrl"]="/page%d.html" % pageFlag
                    self.blogBase["nextUrl"]="disabled"

                self.renderHtml('plist.html',self.blogBase,onePageList,htmlDir,plistIcon)
                print("create "+htmlDir)
                break
            else:
                onePageList=dict(list(self.blogBase["postListJson"].items())[topNum:topNum+self.blogBase["onePageListNum"]])
                postNum=postNum-self.blogBase["onePageListNum"]
                if pageFlag==0:
                    htmlDir=self.root_dir+"index.html"
                    self.blogBase["prevUrl"]="disabled"
                    self.blogBase["nextUrl"]="/page2.html"
                else:
                    htmlDir=self.root_dir+("page%d.html" % (pageFlag+1))
                    if pageFlag==1:
                        self.blogBase["prevUrl"]="/index.html"
                    else:
                        self.blogBase["prevUrl"]="/page%d.html" % pageFlag
                    self.blogBase["nextUrl"]="/page%d.html" % (pageFlag+2)

                self.renderHtml('plist.html',self.blogBase,onePageList,htmlDir,plistIcon)
                print("create "+htmlDir)

            pageFlag=pageFlag+1

        self.renderHtml('tag.html',self.blogBase,onePageList,self.root_dir+"tag.html",tagIcon)
        print("create tag.html")

    def createFeedXml(self):
        self.blogBase["postListJson"]=dict(sorted(self.blogBase["postListJson"].items(),key=lambda x:x[1]["createdAt"],reverse=False))#使列表由时间排序
        feed = FeedGenerator()
        feed.title(self.blogBase["title"])
        feed.description(self.blogBase["subTitle"])
        feed.link(href=self.blogBase["homeUrl"])
        feed.image(url=self.blogBase["avatarUrl"],title="avatar", link=self.blogBase["homeUrl"])
        feed.copyright(self.blogBase["title"])
        feed.managingEditor(self.blogBase["title"])
        feed.webMaster(self.blogBase["title"])
        feed.ttl("60")

        for num in self.blogBase["singeListJson"]:
            item=feed.add_item()
            item.guid(self.blogBase["homeUrl"]+"/"+self.blogBase["singeListJson"][num]["postUrl"],permalink=True)
            item.title(self.blogBase["singeListJson"][num]["postTitle"])
            item.description(self.blogBase["singeListJson"][num]["description"])
            item.link(href=self.blogBase["homeUrl"]+"/"+self.blogBase["singeListJson"][num]["postUrl"])
            item.pubDate(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(self.blogBase["singeListJson"][num]["createdAt"])))

        for num in self.blogBase["postListJson"]:
            item=feed.add_item()
            item.guid(self.blogBase["homeUrl"]+"/"+self.blogBase["postListJson"][num]["postUrl"],permalink=True)
            item.title(self.blogBase["postListJson"][num]["postTitle"])
            item.description(self.blogBase["postListJson"][num]["description"])
            item.link(href=self.blogBase["homeUrl"]+"/"+self.blogBase["postListJson"][num]["postUrl"])
            item.pubDate(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(self.blogBase["postListJson"][num]["createdAt"])))

        if self.oldFeedString!='':
            feed.rss_file(self.root_dir+'new.xml')
            newFeed=open(self.root_dir+'new.xml','r',encoding='utf-8')
            new=newFeed.read()
            newFeed.close()

            new=re.sub(r'<lastBuildDate>.*?</lastBuildDate>','',new)
            old=re.sub(r'<lastBuildDate>.*?</lastBuildDate>','',self.oldFeedString)
            os.remove(self.root_dir+'new.xml')
            
            if new==old:
                print("====== rss xml no update ======")
                feedFile=open(self.root_dir+'rss.xml',"w")
                feedFile.write(self.oldFeedString)
                feedFile.close()
                return

        print("====== create rss xml ======")
        feed.rss_file(self.root_dir+'rss.xml')

    def addOnePostJson(self,issue):
        if len(issue.labels)>=1:
            if issue.labels[0].name in self.blogBase["singlePage"]:
                listJsonName='singeListJson'
                htmlFile='{}.html'.format(self.createFileName(issue,useLabel=True))
                gen_Html = self.root_dir+htmlFile
            else:
                listJsonName='postListJson'
                htmlFile='{}.html'.format(self.createFileName(issue))
                gen_Html = self.post_dir+htmlFile

            postNum="P"+str(issue.number)
            self.blogBase[listJsonName][postNum]=json.loads('{}')
            self.blogBase[listJsonName][postNum]["htmlDir"]=gen_Html
            self.blogBase[listJsonName][postNum]["labels"]=[label.name for label in issue.labels]
            self.blogBase[listJsonName][postNum]["postTitle"]=issue.title
            self.blogBase[listJsonName][postNum]["postUrl"]=urllib.parse.quote(gen_Html[len(self.root_dir):])

            self.blogBase[listJsonName][postNum]["postSourceUrl"]="https://github.com/"+options.repo_name+"/issues/"+str(issue.number)
            self.blogBase[listJsonName][postNum]["commentNum"]=issue.get_comments().totalCount

            if issue.body==None:
                self.blogBase[listJsonName][postNum]["description"]=''
                self.blogBase[listJsonName][postNum]["wordCount"]=0
            else:
                self.blogBase[listJsonName][postNum]["wordCount"]=len(issue.body)
                if self.blogBase["rssSplit"]=="sentence":
                    if self.blogBase["i18n"]=="CN":
                        period="。"
                    else:
                        period="."
                else:
                    period=self.blogBase["rssSplit"]
                self.blogBase[listJsonName][postNum]["description"]=issue.body.split(period)[0].replace("\"", "\'")+period
                
            self.blogBase[listJsonName][postNum]["top"]=0
            for event in issue.get_events():
                if event.event=="pinned":
                    self.blogBase[listJsonName][postNum]["top"]=1
                elif event.event=="unpinned":
                    self.blogBase[listJsonName][postNum]["top"]=0

            try:
                postConfig=json.loads(issue.body.split("\r\n")[-1:][0].split("##")[1])
                print("Has Custom JSON parameters")
                print(postConfig)
            except:
                postConfig={}

            if "timestamp" in postConfig:
                self.blogBase[listJsonName][postNum]["createdAt"]=postConfig["timestamp"]
            else:
                self.blogBase[listJsonName][postNum]["createdAt"]=int(time.mktime(issue.created_at.timetuple()))
            
            if "style" in postConfig:
                self.blogBase[listJsonName][postNum]["style"]=self.blogBase["style"]+str(postConfig["style"])
            else:
                self.blogBase[listJsonName][postNum]["style"]=self.blogBase["style"]

            if "script" in postConfig:
                self.blogBase[listJsonName][postNum]["script"]=self.blogBase["script"]+str(postConfig["script"])
            else:
                self.blogBase[listJsonName][postNum]["script"]=self.blogBase["script"]

            if "head" in postConfig:
                self.blogBase[listJsonName][postNum]["head"]=self.blogBase["head"]+str(postConfig["head"])
            else:
                self.blogBase[listJsonName][postNum]["head"]=self.blogBase["head"]

            if "ogImage" in postConfig:
                self.blogBase[listJsonName][postNum]["ogImage"]=postConfig["ogImage"]
            else:
                self.blogBase[listJsonName][postNum]["ogImage"]=self.blogBase["ogImage"]

            thisTime=datetime.datetime.fromtimestamp(self.blogBase[listJsonName][postNum]["createdAt"])
            thisTime=thisTime.astimezone(self.TZ)
            thisYear=thisTime.year
            self.blogBase[listJsonName][postNum]["createdDate"]=thisTime.strftime("%Y-%m-%d")
            self.blogBase[listJsonName][postNum]["dateLabelColor"]=self.blogBase["yearColorList"][int(thisYear)%len(self.blogBase["yearColorList"])]

            mdFileName=re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', issue.title)
            f = open(self.backup_dir+mdFileName+".md", 'w', encoding='UTF-8')
            
            if issue.body==None:
                f.write('')
            else:
                f.write(issue.body)
            f.close()
            return listJsonName

    def runAll(self):
        print("====== start create static html ======")
        self.cleanFile()

        issues=self.repo.get_issues()
        for issue in issues:
            self.addOnePostJson(issue)

        for issue in self.blogBase["postListJson"].values():
            self.createPostHtml(issue)

        for issue in self.blogBase["singeListJson"].values():
            self.createPostHtml(issue)

        self.createPlistHtml()
        self.createFeedXml()
        print("====== create static html end ======")

    def runOne(self,number_str):
        print("====== start create static html ======")
        issue=self.repo.get_issue(int(number_str))
        if issue.state == "open":
            listJsonName=self.addOnePostJson(issue)
            self.createPostHtml(self.blogBase[listJsonName]["P"+number_str])
            self.createPlistHtml()
            self.createFeedXml()
            print("====== create static html end ======")
        else:
            print("====== issue is closed ======")

    def createFileName(self,issue,useLabel=False):
        if useLabel==True:
            fileName=issue.labels[0].name
        else:
            if self.blogBase["urlMode"]=="issue":
                fileName=str(issue.number)
            elif self.blogBase["urlMode"]=="ru_translit": 
                fileName=str(translit(issue.title, language_code='ru', reversed=True)).replace(' ', '-')
            else:
                fileName=Pinyin().get_pinyin(issue.title)
        
        fileName=re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', fileName)
        return fileName

######################################################################################
parser = argparse.ArgumentParser()
parser.add_argument("github_token", help="github_token")
parser.add_argument("repo_name", help="repo_name")
parser.add_argument("--issue_number", help="issue_number", default=0, required=False)
options = parser.parse_args()

blog=GMEEK(options)

if not os.path.exists("blogBase.json"):
    print("blogBase is not exists, runAll")
    blog.runAll()
else:
    if os.path.exists(blog.root_dir+'rss.xml'):
        oldFeedFile=open(blog.root_dir+'rss.xml','r',encoding='utf-8')
        blog.oldFeedString=oldFeedFile.read()
        oldFeedFile.close()
    if options.issue_number=="0" or options.issue_number=="":
        print("issue_number=='0', runAll")
        blog.runAll()
    else:
        f=open("blogBase.json","r")
        print("blogBase is exists and issue_number!=0, runOne")
        oldBlogBase=json.loads(f.read())
        for key, value in oldBlogBase.items():
            blog.blogBase[key] = value
        f.close()
        blog.blogBase["labelColorDict"]=blog.labelColorDict
        blog.runOne(options.issue_number)

listFile=open("blogBase.json","w")
listFile.write(json.dumps(blog.blogBase))
listFile.close()

commentNumSum=0
wordCount=0
print("====== create postList.json file ======")
blog.blogBase["postListJson"]=dict(sorted(blog.blogBase["postListJson"].items(),key=lambda x:x[1]["createdAt"],reverse=True))#使列表由时间排序
for i in blog.blogBase["postListJson"]:
    del blog.blogBase["postListJson"][i]["description"]
    del blog.blogBase["postListJson"][i]["postSourceUrl"]
    del blog.blogBase["postListJson"][i]["htmlDir"]
    del blog.blogBase["postListJson"][i]["createdAt"]
    del blog.blogBase["postListJson"][i]["script"]
    del blog.blogBase["postListJson"][i]["style"]
    del blog.blogBase["postListJson"][i]["top"]
    del blog.blogBase["postListJson"][i]["ogImage"]

    if 'head' in blog.blogBase["postListJson"][i]:
        del blog.blogBase["postListJson"][i]["head"]

    if 'commentNum' in blog.blogBase["postListJson"][i]:
        commentNumSum=commentNumSum+blog.blogBase["postListJson"][i]["commentNum"]
        del blog.blogBase["postListJson"][i]["commentNum"]

    if 'wordCount' in blog.blogBase["postListJson"][i]:
        wordCount=wordCount+blog.blogBase["postListJson"][i]["wordCount"]
        del blog.blogBase["postListJson"][i]["wordCount"]

blog.blogBase["postListJson"]["labelColorDict"]=blog.labelColorDict

docListFile=open(blog.root_dir+"postList.json","w")
docListFile.write(json.dumps(blog.blogBase["postListJson"]))
docListFile.close()

if os.environ.get('GITHUB_EVENT_NAME')!='schedule':
    print("====== update readme file ======")
    workspace_path = os.environ.get('GITHUB_WORKSPACE')
    readme="# %s :link: %s \r\n" % (blog.blogBase["title"],blog.blogBase["homeUrl"])
    readme=readme+"### :page_facing_up: [%d](%s/tag.html) \r\n" % (len(blog.blogBase["postListJson"])-1,blog.blogBase["homeUrl"])
    readme=readme+"### :speech_balloon: %d \r\n" % commentNumSum
    readme=readme+"### :hibiscus: %d \r\n" % wordCount
    readme=readme+"### :alarm_clock: %s \r\n" % datetime.datetime.now(blog.TZ).strftime('%Y-%m-%d %H:%M:%S')
    readme=readme+"### Powered by :heart: [Gmeek](https://github.com/Meekdai/Gmeek)\r\n"
    readmeFile=open(workspace_path+"/README.md","w")
    readmeFile.write(readme)
    readmeFile.close()
######################################################################################
