import requests
import os
import pandas as pd
import regex as re
import numpy as np

from bs4 import BeautifulSoup

if __name__ == "__main__":

    base_url = r"https://www.sec.gov/cgi-bin/browse-edgar"
    base_url2 = r"https://www.sec.gov"
    file_type = '10-K'

    section_list = []
    ten_k_file = open("C:/Users/Phu Tran/Downloads/SEC_Scraper/ten_k.txt", "r")
    # ten_k = np.empty((18, 0)).tolist()
    ten_k = []
    for line in ten_k_file:
        stripped_line = line.strip()
        section_list = stripped_line.split(',')
        ten_k = section_list
    # for section, line in enumerate(section_list):
    #     ten_k[section].append(section_list[section])
    ten_k_file.close()

    # The fields in the csv file are the following:
    # CIK|Ticker|Name|Exchange|SIC|Business|Incorporated|IRS
    # 1090872|A|Agilent Technologies Inc|NYSE|3825|CA|DE|770518772
    CIK_File = pd.read_csv(r'C:\Users\Phu Tran\Downloads\cik_ticker.csv', sep='|')
    CIK_List = []
    for line in CIK_File['CIK']:
        CIK_List.append(line)
    # [1090872, 4281, 1332552, 1287145, 1024015, 1099290, 1264707, 1281629]
    CIK_List = CIK_List[0:]

    master_data = np.empty((18, 0)).tolist()

    for CIK_Number in CIK_List[0:2]:
        file_CIK = CIK_Number
        # define our parameters dictionary
        parameters = {'action': 'getcompany',
                      'CIK': file_CIK,
                      'type': file_type,
                      'owner': 'exclude',
                      'count': '100'}

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/90.0.4430.93 Safari/537.36'}
        # Sample:https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=1090872&type=10-K&owner=exclude&count=100
        make_url = requests.get(url=base_url, params=parameters, headers=headers)

        soup = BeautifulSoup(make_url.content, features='lxml')
        doc_table = soup.find_all('table', class_='tableFile2')

        # Sample doc_link_list ['https://www.sec.gov/Archives/edgar/data/1090872/000109087220000020/0001090872-20-000020
        # -index.htm',...,'https://www.sec.gov/Archives/edgar/data/1090872/0000912057-00-002160-index.html']
        doc_link_list = []
        for tr in doc_table:
            td = tr.find_all('td')

            for doc_link in td:
                document_href = doc_link.find('a', dict(href=True, id='documentsbutton'))

                if document_href is not None:
                    filing_doc_link = base_url2 + document_href['href']
                    doc_link_list.append(filing_doc_link)

        for link in doc_link_list[0:5]:
            response_link = requests.get(link, headers=headers)
            pre_txt_link = BeautifulSoup(response_link.content, features='lxml')
            txt_table = pre_txt_link.find('table', class_='tableFile')
            txt_row = txt_table.findAll('tr')[-1]
            txt_column = txt_row.findAll('td')[2]
            txt_href = txt_column.find('a')['href']
            txt_url = base_url2 + txt_href
            print(txt_url)

            response = requests.get(txt_url, headers=headers)
            raw_10k = response.text
            doc_start_pattern = re.compile(r'<DOCUMENT>')
            doc_end_pattern = re.compile(r'</DOCUMENT>')

            doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10k)]
            doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10k)]
            type_pattern = re.compile(r'<TYPE>[^\n]+')
            doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10k)]

            document = {}

            for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
                if doc_type == '10-K':
                    document[doc_type] = raw_10k[doc_start:doc_end]
            section_list = []
            regex = re.compile(r"(>Item(\s|&#160;|&nbsp;)(1A|1B|2|3|4|5|6|7A|7|8|9A|9B|10|11|12|13|14|15|1"
                               r")\.{0,1})| "
                               r"(ITEM\s(1A|1B|2|3|4|5|6|7A|7|8|9A|9B|10|11|12|13|14|15|1))")
            matches = regex.finditer(document['10-K'])

            test_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])
            test_df.columns = ['item', 'start', 'end']
            test_df['item'] = test_df.item.str.lower()
            test_df.replace('&#160;', ' ', regex=True, inplace=True)
            test_df.replace('&nbsp;', ' ', regex=True, inplace=True)
            test_df.replace(' ', '', regex=True, inplace=True)
            test_df.replace('\.', '', regex=True, inplace=True)
            test_df.replace('>', '', regex=True, inplace=True)
            pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')
            pos_dat.set_index('item', inplace=True)

            section_list = ['1', '1a', '1b', '2', '3', '4', '5', '6', '7', '7a', '8', '9a', '9b', '10', '11', '12',
                            '13', '14', '15']
            section_index_list = []
            section_content_list = []
            raw_name_list = []
            list_name = []

            for index, section in enumerate(section_list):
                raw_name = 'item_' + section_list[index] + '_raw'
                raw_name_list.append(raw_name)
                section_index = 'item' + section_list[index]
                section_index_list.append(section_index)
                content_name = 'item_' + section_list[index] + '_content'
                section_content_list.append(content_name)

            pre_data = []
            for index, name in enumerate(raw_name_list):
                if name != 'item_15_raw':
                    name = document['10-K'][pos_dat['start'].loc[section_index_list[index]]:
                                            pos_dat['start'].loc[section_index_list[index + 1]]]
                    mast_content = BeautifulSoup(name, 'lxml')
                    mast_content_text = mast_content.get_text()
                    pre_data.append(mast_content_text)
            master_data = [x + [y] for x, y in zip(master_data, pre_data)]
    master_dictionary = {column_name: row_value for column_name, row_value in zip(ten_k, master_data)}
    master_table = pd.DataFrame(master_dictionary)
    os.chdir('C:/Users/Phu Tran/Downloads/SEC_Scraper')
    master_table.to_csv('10KParseData.csv')

