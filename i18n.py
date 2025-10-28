import json
import os
from typing import Dict, Any

class I18n:
    def __init__(self, language: str = "zh-CN"):
        self.language = language
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        """加载语言翻译文件"""
        translations_file = os.path.join(os.path.dirname(__file__), "resources", "i18n", f"{self.language}.json")
        try:
            with open(translations_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            # 如果找不到对应语言文件，尝试加载默认中文
            if self.language != "zh-CN":
                try:
                    default_file = os.path.join(os.path.dirname(__file__), "resources", "i18n", "zh-CN.json")
                    with open(default_file, 'r', encoding='utf-8') as f:
                        self.translations = json.load(f)
                except FileNotFoundError:
                    self.translations = {}

    def t(self, key: str, **kwargs) -> str:
        """获取翻译文本"""
        # 支持嵌套key，如 "banner.title"
        keys = key.split('.')
        value = self.translations

        try:
            for k in keys:
                value = value[k]

            # 支持字符串格式化
            if kwargs:
                return value.format(**kwargs)
            return value
        except (KeyError, TypeError):
            # 如果找不到翻译，返回key本身
            return key

    def get_banner_file(self) -> str:
        """获取对应语言的banner文件路径"""
        banner_file = os.path.join(os.path.dirname(__file__), "resources", f"banner_{self.language.replace('-', '_')}.txt")

        # 如果找不到对应语言的banner文件，使用默认的中文版本
        if not os.path.exists(banner_file):
            banner_file = os.path.join(os.path.dirname(__file__), "resources", "banner_zh_CN.txt")

        # 如果中文版本也不存在，使用原来的banner.txt
        if not os.path.exists(banner_file):
            banner_file = os.path.join(os.path.dirname(__file__), "resources", "banner.txt")

        return banner_file

# 全局实例
_i18n_instance = None

def init_i18n(language: str = "zh-CN"):
    """初始化国际化"""
    global _i18n_instance
    _i18n_instance = I18n(language)

def t(key: str, **kwargs) -> str:
    """全局翻译函数"""
    if _i18n_instance is None:
        init_i18n()
    return _i18n_instance.t(key, **kwargs)

def get_banner_file() -> str:
    """获取banner文件路径"""
    if _i18n_instance is None:
        init_i18n()
    return _i18n_instance.get_banner_file()