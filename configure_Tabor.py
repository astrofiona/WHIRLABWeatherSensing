from rainfunc import *
tabor1 = connect()



digconfig3(tabor1,framelen,numframes)
time.sleep(0.01)
config(tabor1)
tabor1.close_instrument()
time.sleep(0.01)