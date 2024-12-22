import os.path

from bs4 import BeautifulSoup

from lib.twitter.puzzle import DATAPATH_BASE, read_console


class DecodeHTML:
    soup: BeautifulSoup

    @staticmethod
    def fromCache():
        codec = DecodeHTML()
        path = os.path.join(DATAPATH_BASE, "tmp.html")
        html_content = read_console(path)
        codec.soup = BeautifulSoup(html_content, 'html.parser')
        return codec

    @staticmethod
    def toCache(html_content: str):
        codec = DecodeHTML()
        path = os.path.join(DATAPATH_BASE, "tmp.html")
        b = str.encode(html_content)
        codec._save_bytes(b, path)
        codec.soup = BeautifulSoup(html_content, 'html.parser')
        return codec

    def text(self):
        return self.soup.text

    def found(self, content: str):
        if content in self.soup.text:
            return True
        else:
            return False

    def get_input_attribute_val(self, name: str):
        return self.soup.find('input', {'name': name})["value"]

    def get_twitter_callback_x(self, class_name: str = "maintain-context"):
        result = ""
        for a in self.soup.find_all('a', {'class': class_name}, href=True):
            result = a.get("href")
        return result

    def _save_bytes(self, content, file_name):
        """
        save the bytes info into the file
        :param content:
        :param file_name:
        :return:
        """
        file_object = None
        try:
            file_object = open(file_name, 'wb')
            file_object.truncate(0)
        except FileNotFoundError:
            file_object = open(file_name, 'a+')
        finally:
            # file_object.buffer.write(content)
            file_object.write(content)
            file_object.close()
