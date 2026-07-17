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
import math
import calendar
from concurrent.futures import ThreadPoolExecutor
from github import Github
from github.GithubException import GithubException
from xpinyin import Pinyin
from feedgen.feed import FeedGenerator
from jinja2 import Environment, FileSystemLoader
from transliterate import translit
from collections import OrderedDict
######################################################################################
i18n={"Search":"Search","switchTheme":"switch theme","home":"home","comments":"comments","run":"run ","days":" day(s)","Previous":"Previous","Next":"Next","Archive":"Archive","published":"Published","updated":"Updated","author":"Author","wordCount":"Words","readingTime":"Reading time","minRead":"min read","related":"Related posts","previousPost":"Previous post","nextPost":"Next post","loading":"Loading","loadFailed":"Search data failed to load","noResults":"No matching posts"}
i18nCN={"Search":"搜索","switchTheme":"切换主题","home":"首页","comments":"评论","run":"网站运行 ","days":" 天","Previous":"上一页","Next":"下一页","Archive":"归档","published":"发布于","updated":"更新于","author":"作者","wordCount":"字数","readingTime":"阅读时长","minRead":"分钟","related":"相关文章","previousPost":"上一篇","nextPost":"下一篇","loading":"正在加载文章索引…","loadFailed":"文章索引加载失败，请稍后重试。","noResults":"没有找到匹配的文章"}
i18nRU={"Search":"Поиск","switchTheme": "Сменить тему","home":"Главная","comments":"Комментарии ","run":" работает ","days":" дней","Previous":"Предыдущая","Next":"Следующая","Archive":"Архив","published":"Опубликовано","updated":"Обновлено","author":"Автор","wordCount":"Слов","readingTime":"Время чтения","minRead":"мин","related":"Похожие записи","previousPost":"Предыдущая запись","nextPost":"Следующая запись","loading":"Загрузка…","loadFailed":"Не удалось загрузить поиск","noResults":"Ничего не найдено"}
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
    "archive":"M1.75 1h12.5C15.216 1 16 1.784 16 2.75v1.5c0 .698-.409 1.3-1 1.582v7.418A1.75 1.75 0 0 1 13.25 15H2.75A1.75 1.75 0 0 1 1 13.25V5.832A1.751 1.751 0 0 1 0 4.25v-1.5C0 1.784.784 1 1.75 1ZM2.5 6v7.25c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25V6Zm-.75-3.5a.25.25 0 0 0-.25.25v1.5c0 .138.112.25.25.25h12.5a.25.25 0 0 0 .25-.25v-1.5a.25.25 0 0 0-.25-.25Zm3.5 5.75a.75.75 0 0 1 .75-.75h4a.75.75 0 0 1 0 1.5H6a.75.75 0 0 1-.75-.75Z",
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
        if workspace_path and os.path.exists(workspace_path+"/"+self.backup_dir):
            shutil.rmtree(workspace_path+"/"+self.backup_dir)

        if workspace_path and os.path.exists(workspace_path+"/"+self.root_dir):
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
        dconfig={"schemaVersion":2,"singlePage":[],"startSite":"","filingNum":"","onePageListNum":15,"commentLabelColor":"#006b75","yearColorList":["#bc4c00", "#0969da", "#1f883d", "#A333D0"],"i18n":"CN","themeMode":"manual","dayTheme":"light","nightTheme":"dark","urlMode":"pinyin","script":"","style":"","head":"","indexScript":"","indexStyle":"","bottomText":"","showPostSource":1,"iconList":{},"UTC":+8,"rssSplit":"sentence","exlink":{},"needComment":1,"allHead":"","imageCaptcha":0,"author":"","draftLabel":"draft","readingWordsPerMinute":400,"relatedPostsNum":3,"archivePage":1,"pwa":0,"pwaRecentPosts":5,"pwaAssets":[],"pwaIconSizes":"any","themeColor":"#0969da","backgroundColor":"#ffffff"}
        config=json.loads(open('config.json', 'r', encoding='utf-8').read())
        self.blogBase={**dconfig,**config}.copy()
        self.blogBase["postListJson"]=json.loads('{}')
        self.blogBase["singeListJson"]=json.loads('{}')
        self.blogBase["labelColorDict"]=self.labelColorDict
        if "displayTitle" not in self.blogBase:
            self.blogBase["displayTitle"]=self.blogBase["title"]

        if not self.blogBase["author"]:
            self.blogBase["author"]=self.blogBase["displayTitle"]

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
        self.blogBase["homeUrl"]=self.blogBase["homeUrl"].rstrip('/')
        self.blogBase["ogImage"]=self.absoluteUrl(self.blogBase["ogImage"])
        print("GitHub Pages URL: ", self.blogBase["homeUrl"])

        if self.blogBase["i18n"]=="CN":
            self.i18n=i18nCN
        elif self.blogBase["i18n"]=="RU":
            self.i18n=i18nRU
        else:
            self.i18n=i18n
        
        self.TZ=datetime.timezone(datetime.timedelta(hours=self.blogBase["UTC"]))
        self.now=int(time.time())
        self.blogBase["previewMode"]=bool(getattr(self.options, "preview", False))

    def get_repo(self,user:Github, repo:str):
        return user.get_repo(repo)

    def absoluteUrl(self, value):
        if not value:
            return self.blogBase["homeUrl"]
        if re.match(r"^https?://", str(value), flags=re.IGNORECASE):
            return str(value)
        return urllib.parse.urljoin(self.blogBase["homeUrl"]+"/", str(value).lstrip('/'))

    def timestampFromValue(self, value, default=0):
        if value in (None, ""):
            return default
        if isinstance(value, (int, float)):
            return int(value)
        value=str(value).strip()
        if re.match(r"^-?\d+(?:\.\d+)?$", value):
            return int(float(value))
        try:
            normalized=value[:-1]+"+00:00" if value.endswith(("Z", "z")) else value
            parsed=datetime.datetime.fromisoformat(normalized)
            if parsed.tzinfo is None:
                parsed=parsed.replace(tzinfo=self.TZ)
            return int(parsed.timestamp())
        except (TypeError, ValueError, OverflowError):
            print("Invalid publish timestamp: {}".format(value))
            return default

    def timestampFromGithub(self, value):
        if value is None:
            return self.now
        if value.tzinfo is not None:
            return int(value.timestamp())
        return calendar.timegm(value.utctimetuple())

    def isoDate(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).isoformat().replace("+00:00", "Z")

    def parsePostConfig(self, body):
        if not body:
            return {}, body or ""
        lines=body.splitlines()
        for index in range(len(lines)-1, -1, -1):
            stripped=lines[index].strip()
            if stripped=="":
                continue
            if not stripped.startswith("##"):
                break
            try:
                postConfig=json.loads(stripped[2:].strip())
                if isinstance(postConfig, dict):
                    content="\n".join(lines[:index]+lines[index+1:]).strip()
                    print("Has Custom JSON parameters")
                    print(postConfig)
                    return postConfig, content
            except (json.JSONDecodeError, TypeError):
                break
        return {}, body

    def plainText(self, markdown):
        text=re.sub(r"```[^\r\n]*[\r\n]?", " ", markdown or "")
        text=text.replace("```", " ")
        text=re.sub(r"`([^`]*)`", r"\1", text)
        text=re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
        text=re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
        text=re.sub(r"<[^>]+>", " ", text)
        text=re.sub(r"^\s{0,3}(?:#{1,6}|>|[-+*]|\d+[.)])\s*", "", text, flags=re.MULTILINE)
        text=re.sub(r"[*_~]+", "", text)
        return re.sub(r"\s+", " ", html.unescape(text)).strip()

    def createDescription(self, plain_text):
        if not plain_text:
            return ""
        if self.blogBase["rssSplit"]=="sentence":
            period="。" if self.blogBase["i18n"]=="CN" else "."
        else:
            period=str(self.blogBase["rssSplit"])
        description=plain_text.split(period)[0]
        if period and len(description)<len(plain_text):
            description+=period
        return description[:240]

    def issuePublication(self, issue, postConfig=None):
        postConfig=postConfig or self.parsePostConfig(issue.body)[0]
        labels=[label.name for label in issue.labels]
        draftLabel=str(self.blogBase.get("draftLabel", "")).strip()
        publishValue=postConfig.get("publishAt")
        publishAt=self.timestampFromValue(publishValue, 0)
        invalidSchedule=publishValue not in (None, "") and publishAt<=0
        isDraft=bool(draftLabel and draftLabel in labels)
        isFuture=bool(publishAt and publishAt>self.now)
        isOpen=getattr(issue, "state", "open")=="open"
        return {
            "public": bool(labels and isOpen and not isDraft and not isFuture and not invalidSchedule),
            "draft": isDraft,
            "future": isFuture,
            "invalidSchedule": invalidSchedule,
            "publishAt": publishAt
        }

    def shouldIncludeIssue(self, issue, postConfig=None):
        publication=self.issuePublication(issue, postConfig)
        if publication["public"]:
            return True, publication
        previewNumber=str(getattr(self.options, "issue_number", "0"))
        isRequested=str(issue.number)==previewNumber
        if getattr(self.options, "preview", False) and isRequested and getattr(issue, "state", "open")=="open" and len(issue.labels)>=1:
            publication["preview"]=True
            return True, publication
        return False, publication

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

    def preparePostRelationships(self):
        posts=list(self.blogBase["postListJson"].values())
        posts.sort(key=lambda item:item["createdAt"])
        relatedLimit=max(0, int(self.blogBase.get("relatedPostsNum", 3)))
        for index, issue in enumerate(posts):
            issue["previousPost"]=None
            issue["nextPost"]=None
            if index>0:
                previous=posts[index-1]
                issue["previousPost"]={"postTitle":previous["postTitle"],"postUrl":previous["postUrl"]}
            if index+1<len(posts):
                nextPost=posts[index+1]
                issue["nextPost"]={"postTitle":nextPost["postTitle"],"postUrl":nextPost["postUrl"]}

            currentLabels=set(issue["labels"])
            candidates=[]
            for candidate in posts:
                if candidate is issue:
                    continue
                commonLabels=len(currentLabels.intersection(candidate["labels"]))
                if commonLabels==0:
                    continue
                candidates.append((
                    -commonLabels,
                    abs(issue["createdAt"]-candidate["createdAt"]),
                    -candidate["createdAt"],
                    candidate
                ))
            candidates.sort(key=lambda item:item[:3])
            issue["relatedPosts"]=[
                {"postTitle":item[3]["postTitle"],"postUrl":item[3]["postUrl"]}
                for item in candidates[:relatedLimit]
            ]

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
            and not issue.get("isSinglePage", False)
        )
        if protect_images:
            post_body=self.protectPostImages(post_body)

        isSinglePage=issue.get("isSinglePage", False)
        postBase["isArticle"]=not isSinglePage
        postBase["isPreview"]=issue.get("isPreview", False)
        postBase["robots"]="noindex,nofollow" if (postBase["isPreview"] or self.blogBase.get("previewMode")) else "index,follow"
        postBase["postTitle"]=issue["postTitle"]
        postBase["postUrl"]=self.absoluteUrl(issue["postUrl"])
        postBase["canonicalUrl"]=postBase["postUrl"]
        postBase["description"]=issue["description"]
        postBase["ogImage"]=self.absoluteUrl(issue["ogImage"])
        postBase["postBody"]=post_body
        postBase["commentNum"]=issue["commentNum"]
        postBase["style"]=issue["style"]
        postBase["script"]=issue["script"]
        postBase["head"]=issue["head"]
        postBase["top"]=issue["top"]
        postBase["postSourceUrl"]=issue["postSourceUrl"]
        postBase["repoName"]=self.options.repo_name
        postBase["labels"]=issue["labels"]
        postBase["author"]=issue["author"]
        postBase["wordCount"]=issue["wordCount"]
        postBase["readingTime"]=issue["readingTime"]
        postBase["createdDate"]=issue["createdDate"]
        postBase["updatedDate"]=issue["updatedDate"]
        postBase["datePublished"]=issue["datePublished"]
        postBase["dateModified"]=issue["dateModified"]
        postBase["previousPost"]=issue.get("previousPost")
        postBase["nextPost"]=issue.get("nextPost")
        postBase["relatedPosts"]=issue.get("relatedPosts", [])
        postBase["articleJsonLd"]={
            "@context":"https://schema.org",
            "@type":"BlogPosting",
            "headline":issue["postTitle"],
            "description":issue["description"],
            "image":postBase["ogImage"],
            "datePublished":issue["datePublished"],
            "dateModified":issue["dateModified"],
            "mainEntityOfPage":{"@type":"WebPage","@id":postBase["postUrl"]},
            "author":{"@type":"Person","name":issue["author"]},
            "publisher":{"@type":"Organization","name":self.blogBase["title"],"logo":{"@type":"ImageObject","url":self.absoluteUrl(self.blogBase["avatarUrl"])}}
        }
        
        if isSinglePage:
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

        if self.blogBase.get("archivePage", 1)==1:
            keys.append('archive')

        postIcon=dict(zip(keys, map(IconBase.get, keys)))
        self.renderHtml('post.html',postBase,{},issue["htmlDir"],postIcon)
        print("create postPage title=%s file=%s " % (issue["postTitle"],issue["htmlDir"]))

    def createPlistHtml(self):
        self.blogBase["postListJson"]=dict(sorted(self.blogBase["postListJson"].items(),key=lambda x:(x[1]["top"],x[1]["createdAt"]),reverse=True))#使列表由时间排序
        for fileName in os.listdir(self.root_dir):
            if re.match(r"^page\d+\.html$", fileName):
                os.remove(os.path.join(self.root_dir, fileName))
        keys=list(OrderedDict.fromkeys(['sun', 'moon','sync', 'search', 'rss', 'upload', 'post', 'archive'] + self.blogBase["singlePage"]))
        plistIcon={**dict(zip(keys, map(IconBase.get, keys))),**self.blogBase["iconList"]}
        keys=['sun','moon','sync','home','search','post','archive']
        tagIcon=dict(zip(keys, map(IconBase.get, keys)))
        self.blogBase["robots"]="noindex,nofollow" if self.blogBase.get("previewMode") else "index,follow"

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

                pagePath=htmlDir[len(self.root_dir):]
                self.blogBase["canonicalUrl"]=self.blogBase["homeUrl"]+("/" if pagePath=="index.html" else "/"+pagePath)
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

                pagePath=htmlDir[len(self.root_dir):]
                self.blogBase["canonicalUrl"]=self.blogBase["homeUrl"]+("/" if pagePath=="index.html" else "/"+pagePath)
                self.renderHtml('plist.html',self.blogBase,onePageList,htmlDir,plistIcon)
                print("create "+htmlDir)

            pageFlag=pageFlag+1

        self.blogBase["canonicalUrl"]=self.blogBase["homeUrl"]+"/tag.html"
        self.blogBase["robots"]="noindex,nofollow" if self.blogBase.get("previewMode") else "noindex,follow"
        self.renderHtml('tag.html',self.blogBase,onePageList,self.root_dir+"tag.html",tagIcon)
        print("create tag.html")

        if self.blogBase.get("archivePage", 1)==1:
            self.createArchiveHtml(tagIcon)

    def createArchiveHtml(self, icon):
        archive=OrderedDict()
        posts=sorted(self.blogBase["postListJson"].values(),key=lambda item:item["createdAt"],reverse=True)
        for issue in posts:
            year=issue["createdDate"][:4]
            archive.setdefault(year, []).append(issue)
        archiveBase=self.blogBase.copy()
        archiveBase["canonicalUrl"]=self.blogBase["homeUrl"]+"/archive.html"
        archiveBase["robots"]="noindex,nofollow" if self.blogBase.get("previewMode") else "index,follow"
        archiveBase["archive"]=archive
        self.renderHtml('archive.html',archiveBase,{},self.root_dir+"archive.html",icon)
        print("create archive.html")

    def createFeedXml(self):
        self.blogBase["postListJson"]=dict(sorted(self.blogBase["postListJson"].items(),key=lambda x:x[1]["createdAt"],reverse=False))#使列表由时间排序
        feed = FeedGenerator()
        feed.title(self.blogBase["title"])
        feed.description(self.blogBase["subTitle"])
        feed.link(href=self.blogBase["homeUrl"])
        feed.image(url=self.absoluteUrl(self.blogBase["avatarUrl"]),title="avatar", link=self.blogBase["homeUrl"])
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

    def sitePath(self, value=""):
        basePath=urllib.parse.urlsplit(self.blogBase["homeUrl"]).path.rstrip('/')
        value=str(value or "").lstrip('/')
        return (basePath+"/"+value) if value else (basePath+"/")

    def createRobotsTxt(self):
        if self.blogBase.get("previewMode"):
            content="User-agent: *\nDisallow: /\n"
        else:
            content="User-agent: *\nAllow: /\nSitemap: {}/sitemap.xml\n".format(self.blogBase["homeUrl"])
        with open(self.root_dir+"robots.txt", "w", encoding="utf-8", newline="\n") as robotsFile:
            robotsFile.write(content)

    def createSitemapXml(self):
        entries={}
        publicPosts=[item for item in self.blogBase["postListJson"].values() if not item.get("isPreview")]
        publicPages=[item for item in self.blogBase["singeListJson"].values() if not item.get("isPreview")]
        latest=max([item["updatedAt"] for item in publicPosts+publicPages] or [self.now])
        entries[self.blogBase["homeUrl"]+"/"]=self.isoDate(latest)[:10]
        if self.blogBase.get("archivePage", 1)==1:
            entries[self.blogBase["homeUrl"]+"/archive.html"]=self.isoDate(latest)[:10]
        for fileName in os.listdir(self.root_dir):
            if re.match(r"^page\d+\.html$", fileName):
                entries[self.blogBase["homeUrl"]+"/"+fileName]=self.isoDate(latest)[:10]
        for issue in publicPages+publicPosts:
            entries[self.absoluteUrl(issue["postUrl"])]=issue["updatedDate"]

        lines=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for url, lastmod in entries.items():
            lines.append("  <url><loc>{}</loc><lastmod>{}</lastmod></url>".format(html.escape(url), lastmod))
        lines.append('</urlset>')
        with open(self.root_dir+"sitemap.xml", "w", encoding="utf-8", newline="\n") as sitemapFile:
            sitemapFile.write("\n".join(lines)+"\n")

    def pwaAssetPaths(self):
        paths={self.sitePath(),self.sitePath("index.html"),self.sitePath("manifest.webmanifest")}
        recentPosts=sorted(
            [item for item in self.blogBase["postListJson"].values() if not item.get("isPreview")],
            key=lambda item:item["createdAt"],
            reverse=True
        )[:max(0, int(self.blogBase.get("pwaRecentPosts", 5)))]
        for issue in recentPosts:
            paths.add(self.sitePath(issue["postUrl"]))

        configured=list(self.blogBase.get("pwaAssets", []))
        configured.extend([self.blogBase.get("avatarUrl", ""),self.blogBase.get("faviconUrl", "")])
        for field in ("primerCSS","allHead","script","indexScript"):
            configured.extend(re.findall(r"(?:src|href)\s*=\s*['\"]([^'\"]+)['\"]", str(self.blogBase.get(field, "")), flags=re.IGNORECASE))
        homeOrigin=urllib.parse.urlsplit(self.blogBase["homeUrl"]).netloc
        for asset in configured:
            if not asset or str(asset).startswith(("data:", "//")):
                continue
            parsed=urllib.parse.urlsplit(str(asset))
            if parsed.scheme and parsed.netloc!=homeOrigin:
                continue
            if parsed.scheme:
                paths.add(parsed.path+(('?'+parsed.query) if parsed.query else ''))
            elif str(asset).startswith('/'):
                paths.add(str(asset))
            else:
                paths.add(self.sitePath(asset))
        return sorted(paths)

    def createPwaFiles(self):
        icon=self.blogBase.get("pwaIcon") or self.blogBase.get("faviconUrl") or self.blogBase.get("avatarUrl")
        manifest={
            "name":self.blogBase["title"],
            "short_name":self.blogBase["displayTitle"],
            "description":self.blogBase["subTitle"],
            "start_url":self.sitePath(),
            "scope":self.sitePath(),
            "display":"standalone",
            "background_color":self.blogBase["backgroundColor"],
            "theme_color":self.blogBase["themeColor"],
            "icons":[{"src":icon,"sizes":self.blogBase.get("pwaIconSizes", "any"),"type":"image/webp" if str(icon).lower().endswith(".webp") else "image/png"}]
        }
        with open(self.root_dir+"manifest.webmanifest", "w", encoding="utf-8", newline="\n") as manifestFile:
            json.dump(manifest, manifestFile, ensure_ascii=False, indent=2)
            manifestFile.write("\n")

        assets=self.pwaAssetPaths()
        versionData=[(item["postUrl"],item["updatedAt"]) for item in self.blogBase["postListJson"].values()]
        versionData.extend(assets)
        cacheVersion=hashlib.sha256(json.dumps(versionData, sort_keys=True).encode("utf-8")).hexdigest()[:12]
        serviceWorker="""const CACHE_NAME = {cache_name};
const PRECACHE_URLS = {assets};
const HOME_URL = {home_url};

self.addEventListener('install', event => {{
  event.waitUntil((async () => {{
    const cache = await caches.open(CACHE_NAME);
    await Promise.all(PRECACHE_URLS.map(async url => {{
      try {{
        const response = await fetch(url, {{cache: 'reload'}});
        if (response.ok) await cache.put(url, response);
      }} catch (error) {{
        console.warn('[Gmeek PWA] precache failed:', url);
      }}
    }}));
    await self.skipWaiting();
  }})());
}});

self.addEventListener('activate', event => {{
  event.waitUntil((async () => {{
    const names = await caches.keys();
    await Promise.all(names.filter(name => name.startsWith('gmeek-') && name !== CACHE_NAME).map(name => caches.delete(name)));
    await self.clients.claim();
  }})());
}});

self.addEventListener('fetch', event => {{
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;
  event.respondWith((async () => {{
    const cached = await caches.match(request);
    if (request.mode === 'navigate') {{
      try {{
        const response = await fetch(request);
        if (response.ok) (await caches.open(CACHE_NAME)).put(request, response.clone());
        return response;
      }} catch (error) {{
        return cached || caches.match(HOME_URL);
      }}
    }}
    if (cached) {{
      event.waitUntil(fetch(request).then(async response => {{
        if (response.ok) (await caches.open(CACHE_NAME)).put(request, response.clone());
      }}).catch(() => undefined));
      return cached;
    }}
    const response = await fetch(request);
    if (response.ok && ['script','style','font'].includes(request.destination)) {{
      (await caches.open(CACHE_NAME)).put(request, response.clone());
    }}
    return response;
  }})());
}});
""".format(
            cache_name=json.dumps("gmeek-"+cacheVersion),
            assets=json.dumps(assets, ensure_ascii=False),
            home_url=json.dumps(self.sitePath())
        )
        with open(self.root_dir+"sw.js", "w", encoding="utf-8", newline="\n") as serviceWorkerFile:
            serviceWorkerFile.write(serviceWorker)

    def createSiteFiles(self):
        self.createRobotsTxt()
        self.createSitemapXml()
        if self.blogBase.get("pwa", 0)==1 and not self.blogBase.get("previewMode"):
            self.createPwaFiles()
        else:
            for fileName in ("manifest.webmanifest", "sw.js"):
                path=self.root_dir+fileName
                if os.path.exists(path):
                    os.remove(path)

    def addOnePostJson(self,issue,postConfig=None,publication=None):
        if len(issue.labels)<1:
            return None
        postConfig, contentBody=self.parsePostConfig(issue.body) if postConfig is None else (postConfig, self.parsePostConfig(issue.body)[1])
        publication=publication or self.issuePublication(issue, postConfig)
        labels=[label.name for label in issue.labels]
        singleLabel=next((label for label in labels if label in self.blogBase["singlePage"]), None)
        if singleLabel:
            listJsonName='singeListJson'
            htmlFile='{}.html'.format(self.createFileName(issue,useLabel=True,labelName=singleLabel))
            gen_Html = self.root_dir+htmlFile
        else:
            listJsonName='postListJson'
            htmlFile='{}.html'.format(self.createFileName(issue))
            gen_Html = self.post_dir+htmlFile

        postNum="P"+str(issue.number)
        issueJson=json.loads('{}')
        self.blogBase[listJsonName][postNum]=issueJson
        issueJson["htmlDir"]=gen_Html
        issueJson["labels"]=labels
        issueJson["isSinglePage"]=bool(singleLabel)
        issueJson["isPreview"]=bool(publication.get("preview", False))
        issueJson["postTitle"]=issue.title
        issueJson["postUrl"]=urllib.parse.quote(gen_Html[len(self.root_dir):])
        issueJson["postSourceUrl"]="https://github.com/"+self.options.repo_name+"/issues/"+str(issue.number)
        issueJson["commentNum"]=issue.get_comments().totalCount

        plainText=self.plainText(contentBody)
        issueJson["description"]=self.createDescription(plainText)
        issueJson["searchText"]=plainText
        issueJson["wordCount"]=len(contentBody or "")
        wordsPerMinute=max(1, int(self.blogBase.get("readingWordsPerMinute", 400)))
        issueJson["readingTime"]=max(1, int(math.ceil(issueJson["wordCount"]/wordsPerMinute)))
        issueJson["author"]=str(postConfig.get("author") or self.blogBase.get("author") or getattr(issue.user, "login", ""))

        issueJson["top"]=0
        for event in issue.get_events():
            if event.event=="pinned":
                issueJson["top"]=1
            elif event.event=="unpinned":
                issueJson["top"]=0

        createdAt=self.timestampFromValue(postConfig.get("timestamp"), 0)
        if not createdAt:
            createdAt=publication.get("publishAt") or self.timestampFromGithub(issue.created_at)
        updatedValue=postConfig.get("updatedAt", postConfig.get("updated", postConfig.get("updateTimestamp")))
        updatedAt=self.timestampFromValue(updatedValue, self.timestampFromGithub(issue.updated_at))
        updatedAt=max(createdAt, updatedAt)
        issueJson["createdAt"]=createdAt
        issueJson["updatedAt"]=updatedAt
        issueJson["publishAt"]=publication.get("publishAt", 0)
        issueJson["datePublished"]=self.isoDate(createdAt)
        issueJson["dateModified"]=self.isoDate(updatedAt)

        issueJson["style"]=self.blogBase["style"]+str(postConfig.get("style", ""))
        issueJson["script"]=self.blogBase["script"]+str(postConfig.get("script", ""))
        issueJson["head"]=self.blogBase["head"]+str(postConfig.get("head", ""))
        issueJson["ogImage"]=postConfig.get("ogImage", self.blogBase["ogImage"])

        createdTime=datetime.datetime.fromtimestamp(createdAt, self.TZ)
        updatedTime=datetime.datetime.fromtimestamp(updatedAt, self.TZ)
        issueJson["createdDate"]=createdTime.strftime("%Y-%m-%d")
        issueJson["updatedDate"]=updatedTime.strftime("%Y-%m-%d")
        issueJson["dateLabelColor"]=self.blogBase["yearColorList"][int(createdTime.year)%len(self.blogBase["yearColorList"])]

        mdFileName=re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', issue.title)
        with open(self.backup_dir+mdFileName+".md", 'w', encoding='UTF-8') as backupFile:
            backupFile.write(issue.body or '')
        return listJsonName

    def runAll(self):
        print("====== start create static html ======")
        self.cleanFile()

        issues=self.repo.get_issues(state="open")
        for issue in issues:
            postConfig=self.parsePostConfig(issue.body)[0]
            include, publication=self.shouldIncludeIssue(issue, postConfig)
            if include:
                self.addOnePostJson(issue,postConfig,publication)

        self.preparePostRelationships()
        for issue in self.blogBase["postListJson"].values():
            self.createPostHtml(issue)

        for issue in self.blogBase["singeListJson"].values():
            self.createPostHtml(issue)

        self.createPlistHtml()
        self.createFeedXml()
        self.createSiteFiles()
        print("====== create static html end ======")

    def removePost(self, number_str):
        postNum="P"+str(number_str)
        removed=False
        for listJsonName in ("postListJson", "singeListJson"):
            issue=self.blogBase[listJsonName].pop(postNum, None)
            if not issue:
                continue
            removed=True
            htmlDir=issue.get("htmlDir")
            if htmlDir and os.path.exists(htmlDir):
                os.remove(htmlDir)
            mdFileName=re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', issue.get("postTitle", ""))
            backupPath=self.backup_dir+mdFileName+".md"
            if os.path.exists(backupPath):
                os.remove(backupPath)
        return removed

    def runOne(self,number_str):
        print("====== start create static html ======")
        try:
            issue=self.repo.get_issue(int(number_str))
        except GithubException as error:
            if error.status not in (404, 410):
                raise
            issue=None

        self.removePost(number_str)
        if issue is not None:
            postConfig=self.parsePostConfig(issue.body)[0]
            include, publication=self.shouldIncludeIssue(issue, postConfig)
            if include:
                self.addOnePostJson(issue,postConfig,publication)
            else:
                print("====== issue is not publicly publishable ======")
        else:
            print("====== issue was deleted ======")

        self.preparePostRelationships()
        for post in self.blogBase["postListJson"].values():
            self.createPostHtml(post)
        for singlePage in self.blogBase["singeListJson"].values():
            self.createPostHtml(singlePage)
        self.createPlistHtml()
        self.createFeedXml()
        self.createSiteFiles()
        print("====== create static html end ======")

    def createFileName(self,issue,useLabel=False,labelName=None):
        if useLabel==True:
            fileName=labelName or issue.labels[0].name
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
def writeBuildState(blog):
    with open("blogBase.json", "w", encoding="utf-8") as listFile:
        json.dump(blog.blogBase, listFile, ensure_ascii=False)

    print("====== create postList.json file ======")
    sortedPosts=dict(sorted(blog.blogBase["postListJson"].items(),key=lambda item:item[1]["createdAt"],reverse=True))
    searchFields=("postTitle","postUrl","labels","description","searchText","createdDate","updatedDate","dateLabelColor","author","readingTime")
    searchIndex={}
    for postNum, issue in sortedPosts.items():
        searchIndex[postNum]={key:issue.get(key) for key in searchFields}
    searchIndex["labelColorDict"]=blog.labelColorDict
    with open(blog.root_dir+"postList.json", "w", encoding="utf-8") as docListFile:
        json.dump(searchIndex, docListFile, ensure_ascii=False, separators=(",", ":"))

    commentNumSum=sum(issue.get("commentNum", 0) for issue in sortedPosts.values())
    wordCount=sum(issue.get("wordCount", 0) for issue in sortedPosts.values())
    workspace_path=os.environ.get('GITHUB_WORKSPACE')
    if os.environ.get('GITHUB_EVENT_NAME')!='schedule' and workspace_path and not blog.blogBase.get("previewMode"):
        print("====== update readme file ======")
        readme="# %s :link: %s \r\n" % (blog.blogBase["title"],blog.blogBase["homeUrl"])
        readme=readme+"### :page_facing_up: [%d](%s/tag.html) \r\n" % (len(sortedPosts),blog.blogBase["homeUrl"])
        readme=readme+"### :speech_balloon: %d \r\n" % commentNumSum
        readme=readme+"### :hibiscus: %d \r\n" % wordCount
        readme=readme+"### :alarm_clock: %s \r\n" % datetime.datetime.now(blog.TZ).strftime('%Y-%m-%d %H:%M:%S')
        readme=readme+"### Powered by :heart: [Gmeek](https://github.com/Meekdai/Gmeek)\r\n"
        with open(workspace_path+"/README.md", "w", encoding="utf-8") as readmeFile:
            readmeFile.write(readme)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    parser.add_argument("--issue_number", help="issue_number", default="0", required=False)
    parser.add_argument("--preview", help="include the requested draft or scheduled issue in a noindex preview build", action="store_true")
    options = parser.parse_args()

    blog=GMEEK(options)
    oldBlogBase=None
    if os.path.exists("blogBase.json"):
        with open("blogBase.json", "r", encoding="utf-8") as stateFile:
            oldBlogBase=json.load(stateFile)
        if os.path.exists(blog.root_dir+'rss.xml'):
            with open(blog.root_dir+'rss.xml','r',encoding='utf-8') as oldFeedFile:
                blog.oldFeedString=oldFeedFile.read()

    needsFullBuild=(
        oldBlogBase is None
        or options.issue_number in ("0", "")
        or oldBlogBase.get("schemaVersion", 0)!=blog.blogBase["schemaVersion"]
    )
    if needsFullBuild:
        print("blogBase is missing, stale, or a full build was requested; runAll")
        blog.runAll()
    else:
        print("blogBase is current and issue_number!=0, runOne")
        blog.blogBase["postListJson"]=oldBlogBase.get("postListJson", {})
        blog.blogBase["singeListJson"]=oldBlogBase.get("singeListJson", {})
        blog.blogBase["labelColorDict"]=blog.labelColorDict
        blog.runOne(options.issue_number)

    writeBuildState(blog)

if __name__ == "__main__":
    main()
######################################################################################
