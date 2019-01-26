# WhoPaysWriters
A data scrape and analysis of [WhoPaysWriters.com](http://whopayswriters.com/#/results).
A summary of the results can be found [here](Explore_Data.html).
Pending article in the [Columbia Journalism Review](https://www.cjr.org/).
Questions and suggestions for improvement are welcome: kevinrmcelwee@gmail.com.

***
[WhoPaysWriters.com](http://whopayswriters.com/#/results) is an anonymous platform where freelance journalists post details about their compensation. There were approximately 3000 submissions to the site from 2012-2018, making it the largest publicly-available dataset available of its kind. Journalists not only submit their pay, but also include information about their rights, their relationship with the editor, and other contextual data.

#### `scrapeWPW.py`
This script opens creates three kinds of CSVs:
* [publications.csv](publications.csv), which lists all publications scraped from the opening webpage.
* A CSV created for each publication's page under the `data` folder.
* [allData_raw.csv](allData_raw.csv), which is one CSV of everything in `data`.
It requires that the user download [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) in addition to its python packages.

#### `Clean_Data.ipynb`
Cleans data for analysis. Other than normal cleaning, here are some decisions made:
* I replaced most `other` entries with NaNs.
* I dropped everything with fewer than 100 words.
* I dropped all `fiction` and `poetry` entries.
* I removed entries for 2019.
* Potential spam, unreasonable outliers are cut. They are addressed on a case-by-case basis.
This notebook creates [allData_clean.csv](allData_clean.csv), what is ultimately used for analysis.

#### `Explore_Data.ipynb`
Explores most 2-variable relationships and creates appropriate graphs for study.
