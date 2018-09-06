# IMPORT LIB
import urllib
from bs4 import BeautifulSoup
import yaml
import re
import xlsxwriter
import codecs
from datetime import datetime
import urllib.request
import pickle
from pyvi.pyvi import ViTokenizer

# GLOBAL VARIABLES
count_duyet = 0
count_lay = 0
count_bo = 0
# UTILITY FUNCTION
def open_utf8_file_to_read(filename):
    try:
        return codecs.open(filename, "r", "utf-8")
    except:
        return None

def open_utf8_file_to_write(filename):
    try: return codecs.open(filename, "w+", "utf-8")
    except:
        return None

def open_binary_file_to_write(filename):
    try: return open(filename, "wb+")
    except:
        return None

def open_binary_file_to_read(filename):
    try: return open(filename, "rb")
    except:
        return None


def read_url_source_as_soup(url): # return page as soup of BeautifulSoup
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    try:
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        f = urllib.request.urlopen(req)
        return BeautifulSoup(f.read().decode('utf-8'), "lxml")
    except:
        print("Khong the mo trang: " + url)
        return None


def get_date(s_date):
    date_patterns = ["%d/%m/%Y","%d/%m/%y", "%d-%m-%Y", "%d-%m-%y" , "%d/%m.%Y"]
    for pattern in date_patterns:
        try:
            return datetime.strptime(s_date, pattern)
        except:
            pass

def is_not_outdated(date, ngay_toi_da):
    dateobj = get_date(date)
    return (datetime.now() - dateobj).days <= ngay_toi_da

def get_fullurl(weburl, articleurl):
    if re.compile("(http|https)://").search(articleurl):
        return articleurl
    else:
        return weburl + articleurl

# CLASS DEFINITION
class Article:
    def __init__(self, href, topic, date, newspaper, summary = ""):
        self._href=href
        self._topic=topic
        self._date=date
        self._summary=summary
        self._newspaper=newspaper
    def get_href(self):
        return self._href
    def get_date(self):
        return self._date
    def get_topic(self):
        return self._topic
    def get_newspaper(self):
        return self._newspaper
    def get_summary(self):
        return self._summary

class ArticleManager:
    _data = dict()  # a dict of (href: article)
    _blacklist = dict()  # a dict if {href: lifecount}
    def __init__(self, data_filename, blacklist_filename):
        self._default_blacklist_count = 10 # will be removed after 10 compression
        self._data_filename = data_filename
        self._blacklist_filename = blacklist_filename

    def load_data(self):
        stream = open_binary_file_to_read(self._data_filename)
        if stream is not None:
            self._data = pickle.load(stream)
        else:
            print("khong mo duoc file " + self._data_filename)
            self._data = {}

        stream = open_binary_file_to_read(self._blacklist_filename)
        if stream is not None:
            self._blacklist = pickle.load(stream)
        else:
            print("khong mo duoc file " + self._blacklist_filename)
            self._blacklist = {}

    def save_data(self):
        stream = open_binary_file_to_write(self._data_filename)
        pickle.dump(self._data, stream)
        stream.close()

        stream = open_binary_file_to_write(self._blacklist_filename)
        pickle.dump(self._blacklist, stream)
        stream.close()

    def get_article_list(self):
        return list(self._data.values())

    def get_article(self, href):
        return self._data[href]

    def get_time_of_an_url(self, url, webconfig):
        try:
            soup = read_url_source_as_soup(url)
        except:
            return None
        datere = webconfig.get_date_re()
        datetag = webconfig.get_date_tag_list()
        dateclass = webconfig.get_date_class_list()
        filter = re.compile(datere)

        if datetag is not None:
            for tag in datetag:
                for foundtag in soup.find_all(tag):
                    for tagstring in foundtag.contents:
                        searchobj = filter.search(str(tagstring))
                        if searchobj:
                            return searchobj.group(1)
        else:
            for date in dateclass:
                for foundtag in soup.find_all(class_=date):
                    for tagstring in foundtag.contents:
                        searchobj = filter.search(str(tagstring))
                        if searchobj:
                            return searchobj.group(1)
        return None

    def is_a_valid_article(self, atag, webconfig, ):
        global count_bo
        fullurl = get_fullurl(webconfig.get_weburl(), atag['href'])
        topic_word_list = atag.string.split()
        print("Dang xu ly bai: " + atag.string.strip())
        if (len(topic_word_list) >= config_manager.get_minimum_word()):
            newsdate = self.get_time_of_an_url(fullurl, webconfig) #note: date is string
            if (newsdate is not None):
                print("Xuat ban ngay: " + newsdate)
                if is_not_outdated(newsdate, config_manager.get_maximum_day_difference()):
                    return True
                else:
                    print("Loai bai nay vi bai viet qua han")
                    count_bo+=1
                    return False
            else:
                print("Loai bai nay vi khong phai bai bao")
                count_bo += 1
                return False
        else:
            print("Loai bai nay vi tieu de khong du so tu cho phep")
            count_bo += 1
            return False

    def is_in_database(self, href):
        return href in self._data

    def is_blacklisted(self, href):
        return href in self._blacklist

    def add_url_to_blacklist(self, href):
        self._blacklist[href] = self._default_blacklist_count

    def remove_url_from_blacklist(self, href):
        self._blacklist.pop(href)

    def compress_blacklist(self):
        remove =[]
        for href in self._blacklist:
            self._blacklist[href]-=1
            if self._blacklist[href] == 0:
                remove.append(href)
        for href in remove:
            self.remove_url_from_blacklist(href)

    def refresh_url_in_blacklist(self, href): #reward to href when it proves value
        self._blacklist[href]+=1

    def add_article(self, new_article):
        self._data[new_article.get_href()]= new_article

    def add_articles_from_newspaper(self, webconfig): #Get article list from newspaper with webconfig parsing
        global count_lay, count_duyet
        webname = webconfig.get_webname()
        weburl = webconfig.get_weburl()
        print("Dang quet bao: " + webname)
        try:
            soup = read_url_source_as_soup(weburl)
            ataglist = soup.find_all("a", text=True, href=True)
            print("Dang lay du lieu, xin doi...")
            for atag in ataglist:
                # loc ket qua
                fullurl = get_fullurl(weburl, atag['href'])
                print("Dang xu ly trang: " + fullurl)
                count_duyet+=1

                if not self.is_blacklisted(fullurl):
                    if not self.is_in_database(fullurl):
                        if self.is_a_valid_article(atag, webconfig):
                            self.add_article(Article(topic=atag.string.strip(), date = self.get_time_of_an_url(fullurl,webconfig)
                                , newspaper = webname, href=fullurl))
                            count_lay +=1
                            print("So bai viet da lay: " + str(count_lay))
                        else:
                            self.add_url_to_blacklist(fullurl)
                            print("Them vao blacklist")
                    else:
                        print("Bai nay da co trong co so du lieu")
                else:
                    print("Link nay nam trong blacklist")
                    self.refresh_url_in_blacklist(fullurl)
        except:
            print("Khong the mo bao: " + webname)

    def is_article_out_of_date_to_compress(self, article):
        return not is_not_outdated(article.get_date(), config_manager.get_maximum_day_difference()+3) #+1 here is important for compress

    def is_article_topic_too_short(self, article):
        return len(article.get_topic().split()) < config_manager.get_minimum_word()

    def remove_article(self, article):
        self._data.pop(article.get_href())

    def count_database(self):
        return len(self._data)

    def count_blacklist(self):
        return len(self._blacklist)

    def compress_database(self):
        remove = []
        for url, article in self._data.items():
            if self.is_article_out_of_date_to_compress(article):
                remove.append(article)
            if self.is_article_topic_too_short(article):
                remove.append(article)
        for article in remove:
            self.remove_article(article)

class WebParsingConfig:
    def __init__(self, web):
        self._web = web # dict of dict {"webname":{"url":...,date_tag:[...], date_class:[...]}

    def get_webname(self):
        return next(iter(self._web))

    def get_weburl(self):
        return self._web[self.get_webname()]['url']

    def get_date_tag_list(self):
        return self._web[self.get_webname()]['date_tag']

    def get_date_class_list(self):
        return self._web[self.get_webname()]['date_class']

    def get_date_re(self):
        return self._web[self.get_webname()]['date_re']

class TagExtractor():
    def __init__(self, datamanger):
        self._datamanger = data_manager
        self.__set_stopwords()

    def __set_stopwords(self):
        with open_utf8_file_to_read('stopwords-nlp-vi.txt') as f:
            stopwords = set([w.strip().replace(' ', '_') for w in f.readlines()])
        self.stopwords = stopwords

    def segmentation(self, topic):
        return ViTokenizer.tokenize(topic)

    def split_words(self, topic):
        text = self.segmentation(topic)
        SPECIAL_CHARACTER = '0123456789%@$.,=+-!;/()*"&^:#|\n\t\''
        try:
            return [x.strip(SPECIAL_CHARACTER).lower() for x in text.split()]
        except TypeError:
            return []

    def get_topic_tag_list(self, topic):
        split_words = self.split_words(topic)
        return [word.replace('_', ' ') for word in split_words if word not in self.stopwords]

    def get_tag_dict(self):
        tag_dict = dict()
        for article in self._datamanger.get_article_list():
            for keyword in self.get_topic_tag_list(article.get_topic()):
                if keyword in tag_dict:
                    tag_dict[keyword]+=1
                else:
                    tag_dict[keyword] = 1
        return tag_dict

    def get_hot_tag_dict(self):
        tag_dict = self.get_tag_dict()
        count = 0
        hot_tag = {}
        for keyword in sorted(tag_dict, key=tag_dict.get, reverse=True):
            if count <= config_manager.get_hot_tag_number():
                hot_tag[keyword]= tag_dict[keyword]
            count+=1
        return hot_tag

class ConfigManager:
    _filename = ""
    _config={}
    def __init__(self, filename):
        self._filename = filename

    def load_data(self):
        stream = open_utf8_file_to_read(self._filename)
        self._config = yaml.load(stream)

    def get_minimum_word(self):
        return int(self._config['so_tu_toi_thieu_cua_tieu_de'])

    def get_maximum_day_difference(self):
        return int(self._config['so_ngay_toi_da_lay_so_voi_hien_tai'])

    def get_newspaper_list(self):
        return [WebParsingConfig(web) for web in self._config['dia_chi_bao_can_quet']]

    def get_hot_tag_number(self):
        return int(self._config['so_hot_tag_toi_da'])

# GLOBAL OBJECT
config_manager = ConfigManager("docbao.txt") #config object must be instantiate first
data_manager = ArticleManager("article.dat", "blacklist.dat")

def in_ket_qua():
    # mo file excel ghi ket qua
    workbook = xlsxwriter.Workbook('ketqua.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0, 0, "STT")
    worksheet.write(0, 1, "Bài viết")
    worksheet.write(0, 2, "Link")
    worksheet.write(0, 3, "Báo")
    worksheet.write(0, 4, "Ngày xuất bản")
    worksheet.write(0, 5, "Sapo")
    row = 1
    col = 0

    count = 0
    for article in data_manager.get_article_list():
        count+=1
        worksheet.write(row, col, count )
        worksheet.write(row, col+1, article.get_topic())
        worksheet.write(row, col+2, article.get_href())
        worksheet.write(row, col+3, article.get_newspaper())
        worksheet.write(row, col+4, article.get_date())
        worksheet.write(row, col+5, article.get_summary())
        row+=1
    workbook.close()

    # mo file html in ket qua
    html_begin = '''<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    <style>
    a:link    {
      /* Applies to all unvisited links */
      text-decoration:  none;
      } 
    a:visited {
      /* Applies to all visited links */
      text-decoration:  none;
      } 
    a:hover   {
      /* Applies to links under the pointer */
      text-decoration:  underline;
      } 
    a:active  {
      /* Applies to activated links */
      text-decoration:  underline;
      } 
    table {
                    font-family: arial, sans-serif;
                    border-collapse: collapse;
                    width: 100%;
                }

                td, th {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }

                tr:nth-child(even) {
                    background-color: #dddddd;
                }

                #myInput {
                    background-image: url('https://www.w3schools.com/css/searchicon.png'); /* Add a search icon to input */
                    background-position: 10px 12px; /* Position the search icon */
                    background-repeat: no-repeat; /* Do not repeat the icon image */
                    width: 100%; /* Full-width */
                    font-size: 16px; /* Increase font-size */
                    padding: 12px 20px 12px 40px; /* Add some padding */
                    border: 1px solid #ddd; /* Add a grey border */
                    margin-bottom: 12px; /* Add some space below the input */
                }

                #myTable {
                    border-collapse: collapse; /* Collapse borders */
                    width: 100%; /* Full-width */
                    border: 1px solid #ddd; /* Add a grey border */
                    font-size: 18px; /* Increase font-size */
                }

                #myTable th, #myTable td {
                    text-align: left; /* Left-align text */
                    padding: 12px; /* Add padding */
                }

                #myTable tr {
                    /* Add a bottom border to all table rows */
                    border-bottom: 1px solid #ddd; 
                }

                #myTable tr.header, #myTable tr:hover {
                    /* Add a grey background color to the table header and on hover */
                    background-color: #f1f1f1;
                }
                #keyword
                {
                  color: blue;
                  background-color: #f1f1f1; 
                }
    </style>
    <script type="text/javascript" src="https://gc.kis.v2.scr.kaspersky-labs.com/495BB538-028B-484B-B7F3-50E1D0E14725/main.js" charset="UTF-8"></script><script>
                function myFunction() {
                  // Declare variables 
                  var input, filter, table, tr, td, i;
                  input = document.getElementById("myInput");
                  filter = input.value.toUpperCase();
                  table = document.getElementById("myTable");
                  tr = table.getElementsByTagName("tr");

                  // Loop through all table rows, and hide those who don't match the search query
                  for (i = 0; i < tr.length; i++) {
                    td = tr[i].getElementsByTagName("td")[1];
                    if (td) {
                      if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                      } else {
                        tr[i].style.display = "none";
                      }
                    } 
                  }
                }
            </script>
    </head>
    <body>
    '''
    html_end = '''
        <script>
            (function(w,d,t,u,n,a,m){w['MauticTrackingObject']=n;
                w[n]=w[n]||function(){(w[n].q=w[n].q||[]).push(arguments)},a=d.createElement(t),
                m=d.getElementsByTagName(t)[0];a.async=1;a.src=u;m.parentNode.insertBefore(a,m)
            })(window,document,'script','https://campaign.tudonghoamaytinh.com/mtc.js','mt');
        
            mt('send', 'pageview');
        </script>
        </body>
        </html>
        '''

    with open_utf8_file_to_write("index.html") as stream:
        stream.write(html_begin)
        stream.write("<h1> TIỆN ÍCH ĐỌC BÁO NHANH </h1>")
        stream.write("<h4> <i>Tóm tắt thế giới cho người bận rộn</i></h4>")
        stream.write("<h4> Cập nhật: " + datetime.now().strftime("%d/%m/%Y %H:%M") +
                     "       Số ngày quét: " + str(config_manager.get_maximum_day_difference()+1) +
                     "</h4>")
        #stream.write("<h4> Tổng số bài: " + str(data_manager.count_database()) + "</h4>" )
        #stream.write("<h4> Tạo bởi app Đọc báo version " + version + "</h4>")

        # write hot tag list
        tag_extract = TagExtractor(data_manager)
        tag_string = ""
        for keyword, count in tag_extract.get_hot_tag_dict().items():
            tag_string = tag_string + '<font id="keyword" size="' + str(int(count/5)+4) + 'px"'+'>' + keyword + "</font>" +"   •   "
        stream.write('<input type="text" id="myInput" onkeyup="myFunction()" placeholder="Lọc bài báo theo từ khóa">')
        stream.write("<h4> Từ khóa đang hot:</h4>")
        stream.write("<h4>" + tag_string + "</h4>")
        stream.write("<br>")
        stream.write('<table id="myTable">')
        stream.write("<tr>")
        stream.write("<th>STT</th>")
        stream.write("<th>Bài</th>")
        stream.write("<th>Báo</th>")
        stream.write("<th>Ngày xuất bản</th>")
        stream.write("</tr>")

        count = 0
        for article in data_manager.get_article_list():
            count+=1
            stream.write("<tr>")
            stream.write("<td>" + str(count) + "</td>")
            stream.write("<td>" + '<a href="' + article.get_href() + '"' + 'target="_blank">"' + article.get_topic() + "</a></td>")
            stream.write("<td>" + article.get_newspaper() +"</td>")
            stream.write("<td>" + article.get_date()+"</td>")
            stream.write("</tr>")
        stream.write("</table>")
        stream.write(html_end)
    stream.close()

#MAIN PROGRAM
#khoi tao du lieu
config_manager.load_data()
data_manager.load_data()

#Hien thi phien ban
version = "1.4.0"
print("DOC BAO VERSION " + version + "       Số ngày quét: " + str(config_manager.get_maximum_day_difference()+1))


#quet bao
for webconfig in config_manager.get_newspaper_list():
    data_manager.add_articles_from_newspaper(webconfig)
#thong bao ket qua
print("Tong so bai viet da duyet: " + str(count_duyet))
print("Tong so bai viet da lay: " + str(count_lay))
print("Tong so bai viet da bo: " + str(count_bo))
print("Tong so bai trong csdl: " + str(data_manager.count_database()))
print("Tong so link trong blacklist: " + str(data_manager.count_blacklist()))


print("Luu du lieu")
#in ket qua
print("Dang in ket qua")
in_ket_qua()
print("Moi xem ket qua trong file: ketqua.xlsx va index.html")
#luu du lieu
data_manager.compress_database()
data_manager.compress_blacklist()

data_manager.save_data()
