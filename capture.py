#%%
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from wand.image import Image as wi
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
        for  r, d, f in os.walk(os.path.join(os.getcwd(),'papers','pdfs')):
            for file in f:
                numdone = numdone+1
                print ('Converting file {} | {} of {}'.format(file,numdone,numfiles))
                i = 0
                path = os.path.join(os.getcwd(),'papers','imgs',str(r).split(os.path.sep)[-1],file.strip('.pdf'))
                make_dir(path)
                pdf = wi(filename=os.path.join(r,file), resolution = 300)
                pdfImage = pdf.convert("jpeg")
                for img in pdfImage.sequence:
                    print('Doing page {} of {}'.format(i+1,len(pdfImage.sequence)))
                    page = wi(image=img)
                    page.save(filename=os.path.join(path,str(i)+".jpg"))
                    i= i+1
#%%
capture_utils.get_anp_papers()
#%%
capture_utils.pdf_to_img()

# %%
