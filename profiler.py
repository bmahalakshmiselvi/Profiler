#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Developer: Antriksh Kumar Singh
Maintainer: Antriksh Kumar Singh
Email: antriksh.singh@walmart.com
Last Modified On: Managed by GIT
Version: Managed by GIT
Status: Development
"""
__author__ = 'Antriksh'


import unicodecsv
import os
import sys
import source.constants as C
import datetime as D
from jinja2 import Environment, FileSystemLoader


def file_finder(path):
    '''
    :param path: Folder path of the source files, all files must be in txt format other type of file will not be read
    :return: List of profiled data of all the files
    :description: This function walks through all the directories in the given path read all the text files with the
                given delimiter in the configuration file
    '''
    data_profiling = list()
    for r, d, f in os.walk(path):
        for ff in f:
            if ff.split('.')[1] in C.TYPES:
                print str(D.datetime.now()) + ">>" + ff + ">>processing..."
                file_info = dict()
                file_info['file_name'] = ff.split('.')[0]
                file_info['table'] = ff.split('.')[0].replace(" ","")
                # file_info['table'] = add_meta(ff)
                data = file_reader(os.path.join(r,ff))
                file_info['columns'] = summary_data(data,ff)
                data_profiling.append(file_info)
                print str(D.datetime.now()) + ">>" + ff + ">>done"
                # break
    return data_profiling


def file_reader(path):
    colDict = dict()
    row = None
    index = None
    maxInt = sys.maxsize
    decrement = True

    while decrement:
        # decrease the maxInt value by factor 10
        # as long as the OverflowError occurs.

        decrement = False
        try:
            unicodecsv.field_size_limit(maxInt)


            colList = list()
            with open(path, 'r') as fr:
                data = unicodecsv.reader(fr, delimiter=C.DELIMITER, encoding=C.ENCODING,errors='replace')
                # print C.ENCODING
                for header in data.next():
                    colList.append({header: list()})
                for index,row in enumerate(data):
                    # print row
                    for i, field in enumerate(row):
                        colList[i][colList[i].keys()[0]].append( field[1:].strip())
            colDict = {k:v for d in colList for k, v in d.items()}
        except OverflowError:
            maxInt = int(maxInt/10)
            decrement = True
        except IndexError:
            # print row
            index = index + 2
            print str(D.datetime.now()) + ">>" + path.split('\\')[-1] + ">>File is not proper>>Row number:" + str(index)
        except Exception as e:
            print str(D.datetime.now()) + ">>" + path.split('\\')[-1] + ">>" + str(e)
    return colDict


def add_meta(file_name, column_name = None):
    table_name = file_name.split('.')[0]
    with open(C.META) as fr:
        meta = list(unicodecsv.DictReader(fr, delimiter=C.DELIMITER, encoding=C.ENCODING))
        for row in meta:
            if table_name == row['Table']:
                if column_name:
                    # print [table_name,row['Table'],column_name,row['Alias in Actual Table']]
                    if column_name == row['Alias in Actual Table']:
                        return row['Description']
                else:
                    return row['Table'].replace(' ','')
    return None




def summary_data(data,tab):
    results = list()
    for col in data:
        colSumm = dict()
        colSumm['column_name'] = col
        colSumm['description'] = add_meta(tab, col)
        colSumm['min'] = min(data[col])
        colSumm['max'] = max(data[col])
        colSumm['count'] = len(data[col])
        colSumm['freq_dist'] = freq_dist(data[col])[1]
        colSumm['pattern_dist'] = pattern_dist(data[col])[1]
        pattern = pattern_dist(data[col])[0]
        colSumm['unique_count'] = len(freq_dist(data[col])[0])
        colSumm['completeness_count'] = completeness(pattern)
        colSumm['data_type'] = data_type(pattern)
        # print colSumm['data_type']
        if colSumm['data_type'] in ('integer','real'):
            if colSumm['data_type'] == 'integer':
                values = map(int,data[col])
            else:
                values = map(float,data[col])
            colSumm['max'] = max(values)
            colSumm['min'] = min(values)
            colSumm['avg'] = sum(values)/len(values)
        results.append(colSumm)
    return results


def data_type(pd):
    dt = 'integer'
    # print pd
    for p in pd:
        if isfloat(p) and not p.isdigit():
            dt = 'string'
        if not p.isdigit() and dt != 'real':
            dt = 'string'
            break
    return dt

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def completeness(pd):
    c = 0
    for p in pd:
        if p != 'NULL':
            c += pd[p]
    return c


def freq_dist(data):
    fdDict = dict()
    for value in data:
        if value in fdDict:
            fdDict[value] += 1
        else:
            fdDict[value] = 1
    temp = fdDict.items()
    fdDict2 = dict(sorted(temp, key=lambda x: x[1],reverse=True)[:C.FD_LIMIT])
    return fdDict,fdDict2


def pattern_dist(data):
    pdDict = dict()
    for value in data:
        value = pattern_creater(value)
        if value in pdDict:
            pdDict[value] += 1
        else:
            pdDict[value] = 1

    temp = pdDict.items()
    pdDict2 = dict(sorted(temp, key=lambda x: x[1],reverse=True)[:C.PD_LIMIT])
    return pdDict,pdDict2


def pattern_creater(text):
    format_value = list()
    if text:
        for c in text:
            if c.isdigit():
                format_value.append(u'9')
            elif c.isalpha() and c.islower():
                format_value.append(u'a')
            elif c.isalpha() and c.isupper():
                format_value.append(u'A')
            elif c == " ":
                format_value.append(u'_')
            elif c in [",", "."]:
                format_value.append(c)
            elif ord(c) >= 19968 and ord(c) <= 40908:
                format_value.append(u'あ')
            else:
                format_value.append(u'#')
        return "".join(format_value)
    else:
        return "NULL"


def to_csv(data):
    headers = ['File_Name','File_Size','Column_Name','Min','Max','Count',
               'Unique_Count','Completeness_Count','Data_Type','Patterns','Patterns_Count' ]
    output = list()
    for f in data:
        for c in f['columns']:
            for pd in c['pattern_dist']:
                tempDict = dict()
                tempDict['File_Name']=f['file_name']
                tempDict['File_Size']=f['file_size']
                tempDict['Column_Name']=c['column_name']
                tempDict['Min']=c['min']
                tempDict['Max']=c['max']
                tempDict['Count']=c['count']
                tempDict['Unique_Count']=c['unique_count']
                tempDict['Completeness_Count']=c['completeness_count']
                tempDict['Data_Type']=c['data_type']
                tempDict['Patterns']=pd
                tempDict['Patterns_Count']=c['pattern_dist'][pd]
                output.append(tempDict)

    with open('df.csv', 'wb') as fw:
        wr = unicodecsv.DictWriter(fw,fieldnames=headers,)
        wr.writeheader()
        wr.writerows(output)


def tohtml(data):
    env = Environment(loader=FileSystemLoader(C.TEMPLATE_REPO))
    template = env.get_template(C.TEMPLATE)
    output_from_parsed_template = template.render(data=data)
    with open(C.RESULT, "wb") as fh:
        fh.write(output_from_parsed_template.encode('UTF-8'))

if __name__ == '__main__':
    print str(D.datetime.now()) + ">>Job Started"
    #print file_finder()
    # with open('data_profiling.json', 'wb') as fw:
    #     json.dump(file_finder(), fw)
    # to_csv(file_finder())
    tohtml(file_finder(C.SOURCE))
    print str(D.datetime.now()) + ">>Job Complete"
    raw_input('Press Enter to close the program...')
