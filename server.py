import os
from flask import Flask
import tempfile
import urllib2
import requests
import json
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


app = Flask(__name__)


@app.route('/', methods=['GET'])
def scrap_web_page():
    # specify the url
    quote_page = "https://www.amazon.com/Apple-iPhone-Fully-Unlocked-5-8/dp/B075QLRSPK/ref=sr_1_5?s=wireless&ie=UTF8&qid=1529324094&sr=1-5&keywords=iphone+10"

    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    page = opener.open(quote_page).read()


    data = ET.Element('data')
    items = ET.SubElement(data, 'ProductInfo') 
    item1 = ET.SubElement(items, 'title')  
    item2 = ET.SubElement(items, 'content') 

    soup = BeautifulSoup(page, "lxml")
    title_tag = soup.find(id="productTitle")
    item1.text =  title_tag.getText().strip()

    img_div_tag = soup.find(id="imgTagWrapperId")
    img_tag = img_div_tag.img['data-old-hires']
    item3 = ET.SubElement(item2, 'img') 
    item3.text = img_tag

    # video_div_tag= soup.find(id="ivVideoBlock")   
    # video_link = video_div_tag.findChildren()
    # print video_div_tag
    # item4 = ET.SubElement(item2, 'video') 
    # item4.text = video_link

    prod_desc = soup.find(id="productDescription").p.getText()
    item5 = ET.SubElement(items, 'ProductSpecs')  

    prod_details = soup.find(id="productDetails_detailBullets_sections1")
    prod_details_dict = {}
    prod_details_tr = prod_details.find_all('tr')
    for tr in prod_details_tr:
        key = str(tr.th.getText().strip())
        if key not in ['Customer Reviews', 'Best Sellers Rank']:
            prod_details_dict[str(tr.th.getText().strip())] = str(tr.td.getText().strip().replace('\n',''))
    item5.text =  json.dumps(prod_details_dict)


    more_tag = soup.find(id="aplus_feature_div")
    more_tag_1 = more_tag.find(id='aplus')
    more_tag_2 = more_tag_1.find('div')

    more_details = more_tag_2.find_all("div", {"class":"celwidget"})
    item6 = ET.SubElement(items, 'ManufDetails_row1')
    item7 = ET.SubElement(item6, 'data1')
    item8 = ET.SubElement(item6, 'img_src')
    count = 0
    img_data = text_data = []
    for detail in more_details:
        if count <3:
            tag =  detail.findChild().findChild().findChild().findChild()
            child_tag = tag.findChild()
            item7.text =  child_tag.getText()
            if child_tag.name == 'div':
                tags_now = child_tag.find_all("div")
                img_data= []
                for tag in tags_now:
                    try:
                        img_src = tag.img['src']
                        img_data.append(img_src)

                    except:
                        pass
                item8.text = json.dumps(img_data)
            if child_tag.name == 'table':
                trs = child_tag.find_all('tr')
                # print len(trs)
                for tr in trs:
                    child_tags = tr.findChildren()
                    for child in child_tags:
                        if child.find('img'):
                            img_data.append(child.find('img')['src'])
                        else:
                            text_data.append(child.text.strip())
            count += 1
    item9 = ET.SubElement(items, 'ManufDetails_row2')
    item10 = ET.SubElement(item9, 'img_src')
    item11 = ET.SubElement(item9, 'data2')  
    item10.text = json.dumps(img_data)              
    item11.text = json.dumps(text_data)

        
    item12 = ET.SubElement(items, 'Related_videos')
    related_videos_div = soup.find(id='vse-related-videos').findChild()
    video_list = [] 
    video_lis = related_videos_div.findAll(attrs={"class" : "a-carousel-card"})
    for tag in video_lis:
        video_dic = {}
        data_tag = tag.findChild()
        try:
            video_duration = data_tag['data-duration']
            video_title = data_tag['data-title']
            video_vendor_name = data_tag['data-vendor-name']
            video_url = data_tag['data-video-url'].replace('&amp;','&')
            video_dic['duration'] = video_duration
            video_dic['title'] = video_title
            video_dic['vendor'] = video_vendor_name
            video_dic['url'] = video_url
            video_list.append(video_dic)
        except:
            pass

    item12.text = json.dumps(video_list)


    mydata = ET.tostring(data) 
    tmp_dir = tempfile.gettempdir()
    path = os.path.join(tmp_dir, "product_details.xml")
    myfile = open(path, "w")  
    myfile.write(mydata)  

    return 'XML file has been generated in your /tmp folder !!'

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000)
