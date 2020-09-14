



def sp500_company_names():
    import bs4 as bs
    import requests

    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    companyNames = []
    for row in table.findAll('tr')[1:]:
        companyName = row.findAll('td')[1].text
        companyNames.append(companyName)
        
    return companyNames


def generate_data_sample():
    import numpy as np
    import pandas as pd

    names = sp500_company_names()

    randomNameSelection = np.random.choice(names,size=100)

    def company_name_random_modification(companyName):
        randomAdditions = ['Co.', 'co', 'Ltd', 'Limited','Services', 'Payments', 'Inc','']
        return ' '.join([word for word in companyName.split()[:-1]] + list(np.random.choice(randomAdditions,size=int(3*np.random.rand()))))

    modifiedRandomNameSelection = [company_name_random_modification(name) for name in randomNameSelection]

    with pd.ExcelWriter('sampleFile.xlsx') as writer:
        pd.Series(names,name='companyName').to_excel(writer,sheet_name='Existent Names',index=None)
        pd.Series(modifiedRandomNameSelection,name='companyName').to_excel(writer,sheet_name='New Names',index=None)


if __name__=='__main__':
    generate_data_sample()