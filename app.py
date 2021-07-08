from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://pusatdata.kontan.co.id/makroekonomi/inflasi')
soup = BeautifulSoup(url_get.content,"html.parser")

table = soup.find('div', attrs={'class':'baris-scroll'})
row = table.find_all('div', attrs={'class':'kol-konten3-1'})
row_length = len(row)

temp = [] 

for i in range(1, row_length):
    
    #get period 
    period = table.find_all('div', attrs={'class':'kol-konten3-1'})[i].text
    
    #get inflation mom
    inflation_mom = table.find_all('div', attrs={'class':'kol-konten3-2'})[i].text
    inflation_mom = inflation_mom.strip() #to remove excess white space
    
    #get inflation yoy
    inflation_yoy = table.find_all('div', attrs={'class':'kol-konten3-3'})[i].text
    inflation_yoy = inflation_yoy.strip() #to remove excess white space
    
    temp.append((period,inflation_mom,inflation_yoy)) 

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('period','inflation_mom','inflation_yoy'))

#insert data wrangling here
df['inflation_mom'] = df['inflation_mom'].str.replace(",",".")
df['inflation_mom'] = df['inflation_mom'].astype('float64')
df['inflation_yoy'] = df['inflation_yoy'].str.replace(",",".")
df['inflation_yoy'] = df['inflation_yoy'].astype('float64')
df['period'] = df['period'].astype('datetime64')
df = df.set_index('period')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data1 = f'{df["inflation_mom"].mean().round(2)}'
	card_data2 = f'{df["inflation_yoy"].mean().round(2)}'

	# generate plot
	ax = df.plot(figsize = (18,9))
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]


	# render to htmls
	return render_template('index.html',
		card_data1 = card_data1,
		card_data2 = card_data2, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)
