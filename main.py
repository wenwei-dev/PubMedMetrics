#!/usr/bin/env python
import os
import sys
import yaml
import progressbar
import logging
import datetime as dt
import unicodecsv as csv
import colorlog
import argparse

from pubmedmetrics.entrez import search, fetch_details
from pubmedmetrics.db import PubMed, Metric, session_scope
from pubmedmetrics.metric import queryAltmetric

progressbar.streams.wrap_stderr()
logger = logging.getLogger('main')

def fetch_papers(args):
    config = []
    with open(args.config) as f:
        config = yaml.load(f)

    pubmeds = []
    papers = []
    keywords = [q['query'] for q in config]
    logger.info("Fetching papers. Keywords: %s" % ', '.join(keywords))
    for c in config:
        results = search(c['query'], c['days'], c['max_lines'])
        id_list = results['IdList']  # papers PMID
        _papers = fetch_details(id_list)
        logger.info("Fetched %s papers for query %s" % (
            len(id_list), c['query']))
        if 'PubmedArticle' in _papers:
            papers += _papers['PubmedArticle']

    logger.info("Fetched total %s papers" % len(papers))
    logger.info("Extracing fields")
    for paper in papers:
        try:
            PubMedTitle = paper['MedlineCitation']['Article']['ArticleTitle']
            PubMedTitle = PubMedTitle.replace('\n', ' ').strip()
            PubMedID = paper['MedlineCitation']['PMID']
            PubMedURL = 'https://www.ncbi.nlm.nih.gov/pubmed/' + PubMedID
        except Exception as ex:
            logger.error(ex)
            continue
        pubmed = PubMed(
            pmid=PubMedID,
            title=PubMedTitle,
            link=PubMedURL,
            create_dt=dt.datetime.utcnow()
        )
        pubmeds.append(pubmed)

    with session_scope() as session:
        for pubmed in pubmeds:
            session.merge(pubmed)
    logger.info("Processed %s papers" % (len(pubmeds)))

def fetch_metrics(args):
    now = dt.datetime.utcnow()
    days_ago = now - dt.timedelta(days=args.days)
    records = []
    with session_scope() as session:
        pubmeds = session.query(PubMed).filter(
            PubMed.create_dt >= days_ago).all()
        logger.info("Found %s papers in database since %s days ago" % (
            len(pubmeds), args.days))
        logger.info("Fetching metrics")
        with progressbar.ProgressBar(
            maxval=len(pubmeds), redirect_stdout=True) as bar:
            for i, pubmed in enumerate(pubmeds):
                pmid = pubmed.pmid
                altmetric = queryAltmetric(pmid)
                metric = Metric(pmid=pmid, altmetric=altmetric,
                    create_dt=dt.datetime.utcnow())
                session.merge(metric)
                records.append((altmetric, pubmed))
                bar.update(i+1)
        session.expunge_all()
    records = sorted(records, key=lambda x: x[0], reverse=True)
    with open(args.output, 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Metric', 'Title', 'Link'])
        for record in records:
            writer.writerow((record[0], record[1].title, record[1].link))

#TODO
def publish_paper(args):
    pass

def init_logging(level):
    formatter = logging.Formatter(
        '[%(name)s][%(levelname)s] %(asctime)s: %(message)s')
    fh = logging.FileHandler('main.log', 'w')
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    if os.isatty(2):
        cformat = '%(log_color)s' + formatter._fmt
        formatter = colorlog.ColoredFormatter(
            cformat,
            log_colors={
                'DEBUG':'reset',
                'INFO': 'reset',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )
    sh.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(sh)
    root.addHandler(fh)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config', default='config.yaml',
        help='Configuration for querying')
    parser.add_argument(
        '-o', '--output', default='papers.csv',
        help='Output file name of the fetched papers')
    parser.add_argument(
        '-d', '--days', default=7, type=int,
        help='Number of days of looking back')
    args = parser.parse_args()

    init_logging(logging.INFO)
    fetch_papers(args)
    fetch_metrics(args)

if __name__ == '__main__':
    main()
