'''
scrapeWPW.py
By Kevin McElwee

A series of functions that ultimately create a single CSV, allData_raw.csv, 
which contains all the data from WhoPaysWriters.com.
'''

import pandas as pd
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import csv
import time

def getAllPublications():
	''' retrieve list of publications from WPW homepage, create csv'''
	url = 'http://whopayswriters.com/#/results'
	browser = webdriver.Chrome()
	browser.get(url)

	time.sleep(1.5) # wait for page to load
	
	html = browser.page_source
	soup = BeautifulSoup(html, 'html.parser')

	mainContent = soup.find('div', {'class': 'main-content'})
	sideList = mainContent.find_all('li')
	pubAndLink = [(l.text, l.find('a')['href'], 0) for l in sideList]

	with open('publications.csv', 'w') as f:
		csv_out = csv.writer(f)
		csv_out.writerow(['pub', 'link', 'madeCSV'])
		for r in pubAndLink:
			csv_out.writerow(r)

def scrapePage(publication, browser):
	'''Scrape all data given publication page, return a list of rows dictionaries'''
	html = browser.page_source
	soup = BeautifulSoup(html, 'html.parser')

	listOfRows = []
	dataByYear = soup.find_all('div', {'ng-repeat':'year in orderedYears'})
	
	for m in dataByYear:
		year = m.h3.text
		submissions = m.find_all('div', {'ng-repeat': 'interaction in interactionsByYear[year]'})
		for s in submissions:
			r = {}
			r['publication'] = publication
			r['year'] = year

			dollaz = s.find('div', {'class': 'dollaz'})
			rateAndKind = dollaz.find_all('span')
			if len(rateAndKind) != 0:
				r['dollar'] = rateAndKind[0].text
				r['flatRate'] = 'flat' in rateAndKind[1].text
			else:
				r['dollar'] = None
				r['flatRate'] = None
			
			temp = s.find('div', {'class': 'payment'}).span.text
			r['paidYet'] = None if temp == ' ' else temp
			r['paymentDifficulty'] = s.find('div', {'class': 'payment'}).i['class'][-1]
			
			comment = s.find('section', {'ng-if': 'interaction.comment'})
			r['comment'] = comment if comment is None else comment.text

			mainStuff = s.find('div', {'class': 'main item'}).find('section')
			wordCountAndKind = mainStuff.find('p', {'ng-bind': 'interaction.description()'}).text
			if 'word' in wordCountAndKind:
				splitter = wordCountAndKind.split('-word ')
				r['wordCount'] = splitter[0]
				r['storyType'] = None if len(splitter) < 2 else splitter[1]
			else:
				r['wordCount'] = wordCountAndKind # CHANGED THIS
				r['storyType'] = None

			rep2 = mainStuff.find('p', {'ng-bind': 'interaction.details()'}).text
			if rep2 != '':
				if ';' in rep2:
					r['levelOfReporting'] = rep2.split(';')[0]
					r['relationship'] = rep2.split('; ')[1]
				else:
					r['levelOfReporting'] = rep2 # fix errors in notebook
			else:
				r['levelOfReporting'] = None
				r['relationship'] = None

			icons = s.find('div', {'class': 'main item'}).find('div', {'class': 'icons'})
			all_is = icons.find_all('i')
			for i in all_is:
				q = i['data-title']
				if 'Contract' in q:
					r['contract'] = q
				if 'Rights' in q:
					r['rights'] = q
				
				# multiple platforms allowed
				# let's only make one platform column
				# let's say print trumps digital trumps other
				if 'Platform' in q:
					if 'print' in q:
						r['platform'] = q
					elif 'digital' in q:
						r['platform'] = q
					elif 'other' in q:
						r['platform'] = q

			listOfRows.append(r)
	return listOfRows

def create_Publication_CSVs(sleepSeconds=0.8):
	'''call scrapePage() to create a csv for each publication'''
	df = pd.read_csv('publications.csv')

	browser = webdriver.Chrome()
	for i, row in df.iterrows():
		if not bool(row['madeCSV']): 
			publication = row['pub']
			print(str(i) + ' ' + publication)
			url = 'http://whopayswriters.com/' + row['link']
			browser.get(url)
			time.sleep(sleepSeconds) # wait for full page to load
			
			info = scrapePage(publication, browser)
			df_temp = pd.DataFrame(info)
			df_temp.to_csv('data/' + (row['link'].split('/')[-1]) + '.csv', index=False)
			
			# change the publications.csv so we don't scrape this data again
			df.at[i, 'madeCSV'] = 1
			df.to_csv('publications.csv', index=False)

def combine_csvs():
	''' Combine each publication's csvs into one large csv '''
	errorFiles = []
	df = pd.DataFrame()
	for file in os.listdir('data'):
		if file.endswith('.csv'):
			try: 
				df = df.append(pd.read_csv('data/' + file), ignore_index=True, sort=False)
			except:
				errorFiles.append(file)
				file
	df.to_csv('allData_raw.csv', index=False)
	return errorFiles

def doubleCheckErrors(errorFiles1, sleepSeconds=.5):
	print('Errors on the first scrape attempt:')
	for e in errorFiles1:
		print(e, end=', ')
	print('\n' + '#'*50)
	print('\nTesting again with extra time: {} seconds'.format(sleepSeconds))
	
	errorLinks = ['#/publication/' + e[:-4] for e in errorFiles1]
	df = pd.read_csv('publications.csv')
	df.loc[df['link'].isin(errorLinks), 'madeCSV'] = 0
	
	df.to_csv('publications.csv', index=False)
	create_Publication_CSVs(sleepSeconds=sleepSeconds)

	errorFiles2 = combine_csvs()
	fixes = [e for e in errorFiles1 if e not in errorFiles2]
	
	print('\n' + '#'*50)
	print('Error Files corrected:', len(fixes))
	for f in fixes:
		print(f)

def main():	
	# getAllPublications()
	# create_Publication_CSVs()
	errorFiles = combine_csvs()
	doubleCheckErrors(errorFiles)
	
if __name__ == '__main__':
	main()

