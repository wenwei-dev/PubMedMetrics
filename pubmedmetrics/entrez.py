# https://marcobonzanini.com/2015/01/12/searching-pubmed-with-python/
from Bio import Entrez

def search(query, days, max_lines):
    Entrez.email = 'your.email@example.com'
    handle = Entrez.esearch(db='pubmed',
                            reldate=days,
                            sort='pub date',
                            retmax=max_lines,
                            retmode='xml',
                            term=query)
    results = Entrez.read(handle)
    return results

def fetch_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'your.email@example.com'
    handle = Entrez.efetch(db='pubmed',
                            retmode='xml',
                            id=ids)
    results = Entrez.read(handle)
    return results
