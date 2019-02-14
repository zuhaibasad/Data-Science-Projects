from daftlistings import Daft, RentType
import pandas as pd
import datetime

now = datetime.datetime.now().date()
offset = 0
pages = True
database = pd.DataFrame(columns=['Formalized_address','Price','Num_bedrooms','Daft_link'])
i=0
j=1
Areas = ['Dublin 1', 'Dublin 2', 'Dublin 6', 'Dublin 7', 'Dublin 8', 'Dublin 10', 'Dublin 6W', 'Dublin 12']
while j < len(Areas):
	while pages:
		daft = Daft()
		daft.set_county('Dublin')
		daft.set_area(Areas[j])
		daft.set_listing_type(RentType.APARTMENTS)
		daft.set_offset(offset)

		listings = daft.get_listings()

		if not listings:
			pages = False

		for listing in listings:
			database.loc[i] = [listing.get_formalised_address(),listing.get_price(),listing.get_price(),listing.get_daft_link()]
			i = i+1

		offset = offset + 10
	pages = True
	j = j+1	

writer = pd.ExcelWriter(str(now)+'_Rent.xlsx')
database.to_excel(writer,'Sheet0')
writer.save()
