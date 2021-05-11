import requests
import os
import pandas as pd

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

    txt_file_list = []

    for CIK_Number in CIK_List[0:100]:
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

        for link in doc_link_list:
            response_link = requests.get(link, headers=headers)
            pre_txt_link = BeautifulSoup(response_link.content, features='lxml')
            txt_table = pre_txt_link.find('table', class_='tableFile')
            txt_row = txt_table.findAll('tr')[-1]
            txt_column = txt_row.findAll('td')[2]
            txt_href = txt_column.find('a')['href']
            txt_url = base_url2 + txt_href
            txt_file_list.append(txt_url)

    master_table = pd.DataFrame(txt_file_list, columns=['Text File Links'])
    os.chdir('C:/Users/Phu Tran/Downloads/SEC_Scraper')
    master_table.to_csv('10KTextFileLinks.csv')

