__author__ = 'Antriksh'

import os.path as o

PATH = o.dirname(o.dirname(o.abspath(__file__)))

#Name of the template file need not to be changed
TEMPLATE = 'df_template_tabs.html'



'''
EDITABLE CONFIGURATION
'''

#Name of the reference file in csv format
META_REPO = 'S_CUBO_Equipments.csv'

SOURCE = o.join(PATH, 'files')
META = o.join(PATH, 'meta', META_REPO)

#Name of the output file
RESULT_NAME = 'df.html'

RESULT = o.join(PATH, 'results', RESULT_NAME)
TEMPLATE_REPO = o.join(PATH, 'templates')

#Limit of number of rows you want to see in pattern distribution
PD_LIMIT = 15
#Limit of number of rows you want to see in frequency distribution
FD_LIMIT = 15

#Type of files you want to profile(supports only txt and csv)
TYPES = ['txt']

#Change the encoding of a input file
ENCODING = 'utf-8-sig'

#Delimiter in the file
DELIMITER = '\t'

'''
for tab use '\t'
'''
