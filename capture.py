#%%
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from pdf2image import convert_from_path
#%%
def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

class capture_utils():
    def list_anp_papers():
        s = requests.session()

        data = {
            'garea': '0',
            'area': '0',
            'sarea': '0',
            'orientador': '',
            'oautores': '',
            'titulo': '',
            'pchave1': '',
            'pchave2': '',
            'pchave3': '',
            'pchave4': '',
            'pchave5': '',
            'pchave6': '',
            'snivel': '-999999',
            'sPRH': '-999999'
        }

        url = 'https://sicbolsas.anp.gov.br/CapitalHumano/resultadobusca.asp'
        html = s.post(url,data=data)
        soup = BeautifulSoup(html.content,'html.parser')
        table = soup.find_all('table')[0]
        df = pd.read_html(str(table),header=0)[0]
        links = []
        files = []
        for a in table.find_all('a', href=True): 
            if a.text: 
                links.append(a['href'])
                files.append(a['href'].split('/')[-1])
        df['link'] = pd.Series(links)
        df['file'] = pd.Series(files)
        return df

    def get_anp_papers():
        df = capture_utils.list_anp_papers()

        for i in range(len(df)):
            path = os.path.join(os.getcwd(),'papers','pdfs',df['link'][i].split('/')[-2])
            make_dir(path)
            print('Dowloandig {} | {} of {}'.format(df['file'][i],i+1,len(df)))
            paper = requests.get(df['link'][i])
            with open(os.path.join(path,df['file'][i]), 'wb') as f:
                f.write(paper.content)
        return df

    def pdf_to_img():
        numfiles =0 
        for  r, d, f in os.walk(os.path.join(os.getcwd(),'papers','pdfs')):
            for file in f:
                numfiles= numfiles+1
        numdone=0
        errors = []
        for  r, d, f in os.walk(os.path.join(os.getcwd(),'papers','pdfs')):
            for file in f:
                numdone = numdone+1
                print ('Converting file {} | {} of {}'.format(file,numdone,numfiles))
                path = os.path.join(os.getcwd(),'papers','imgs',str(r).split(os.path.sep)[-1],file.strip('.pdf'))
                make_dir(path)
                try:
                    pages = convert_from_path(os.path.join(r,file),output_folder=path,dpi=300, fmt="jpg",thread_count=8)
                    l = []
                    for i in range(len(pages)):
                        l.append(pages[i].filename)
                    pages = 0
                    for i in range(len(l)):
                        old_name = l[i]
                        new_name = l[i][:len(l[i])-len(l[i].split(os.path.sep)[-1])]+str(i)+".jpg"
                        os.rename(old_name,new_name)
                except:
                    print ('Error on file {}. Check repport'.format(file))
                    errors.append(os.path.join(r,file))
        return errors

#%%
#capture_utils.get_anp_papers()

# %%
