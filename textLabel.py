
#import modules
import streamlit as st
import pandas as pd
from annotated_text import annotated_text
import re
import json
import os
import pathlib

#predefine parameters
phaseChoices = ['Label Data', 'Save Result']
file = ''
# col = 'Description'
confirmButton = False
nextButton = False
#current working dir
wd = str(pathlib.Path().absolute())
#regex pattern
# regexPattern = '[\n\,\(\:]*%s\,* |^%s '
regexPattern = '[\n\,\(\:\s]*%s[\,\)\s\.]*|^%s[\s]'
#org - blue color, person - red color
tagColorDict = {'ORG': "#8ef", 'PERSON':"#faa", 'LOC':"#fea", 'BANK':"#afa"}
tagTxtFile = './TempResult/tagList.txt'
contentTxtFile = './TempResult/content.txt'
#default result name
resultJsonFile = 'result.json'
tagResult = []
contentResult = []
finalList = []

#sidebars
option = st.sidebar.selectbox("Section", phaseChoices)

#input for tag
orgTag = st.sidebar.text_input('Organization Tag') 
pplTag = st.sidebar.text_input('Person Tag')
locTag = st.sidebar.text_input('Location Tag')
bankTag = st.sidebar.text_input('Bank Tag')

#create a temp folder if not found
if not os.path.exists('./TempResult'):
    os.mkdir('./TempResult')

#cache func
# @st.cache(hash_funcs={streamlit.uploaded_file_manager.UploadedFile: my_hash_func}, suppress_st_warning = True)
@st.cache(suppress_st_warning = True)
def load_data(file_uploaded):
    return pd.read_csv(file_uploaded, sep=',', encoding='utf-8')

@st.cache(suppress_st_warning = True)
def tag_content(desc):
    #for annotation and result
    tagList = []
#     orgList = [i for i in orgTag.split(',') if i!='']
#     pplList = [i for i in pplTag.split(',') if i!='']
    allTagList = [orgTag, pplTag, locTag, bankTag]
    allLabelList = ['ORG', 'PERSON', 'LOC', 'BANK']
    allTagNoEmptyList = [[j for j in i.split(',') if j!=''] for i in allTagList]
    
    for tempList in zip(allTagNoEmptyList, allLabelList):
        for item in tempList[0]:
            if len(re.findall('[\n\,\(\:\s]*%s[\,\)\s\.]*|^%s[\s]'%(item, item), desc)) >= 1:
                for match in [(i.start(), i.end(), tempList[1]) for i in re.finditer(item, desc)]:
                    tagList.append(match)
    
#     for org in orgList:
#         if len(re.findall('\n*%s\,* |^%s '%(org, org), desc)) >= 1:
#             for match in [(i.start(), i.end(), "ORG") for i in re.finditer(org, desc)]:
#                 tagList.append(match)
                
#     for ppl in pplList:
#         if len(re.findall('\n*%s\,* |^%s '%(ppl, ppl), desc)) >= 1:
#             for match in [(i.start(), i.end(), "PERSON") for i in re.finditer(ppl, desc)]:
#                 tagList.append(match)
                        
    return tagList

# @st.cache(suppress_st_warning = True)
def store_tempResult(tempTagList, tempContent):
    with open(tagTxtFile, 'a') as myFile:
        myFile.write('%s \n'%json.dumps(tempTagList))      
    with open(contentTxtFile, 'a') as myFile:
        myFile.write('%s \n'%json.dumps(tempContent))
        
def keyInWorkingPath(key, print = False):
#     startPath = "D:/Users/figohjs/Documents"
    resultWd = st.text_input('Current directory:', wd, key = key)
    resultFileName = st.text_input('Filename:', resultJsonFile)
    #show how many lablled data
    #read text file
    if os.path.isfile(tagTxtFile):
        with open(tagTxtFile, 'r', encoding='utf-8') as input_file:
            for row in input_file.readlines():
                tagResult.append(json.loads(row))
        numRow = len(set([key for i in tagResult for key,val in i.items()]))
    else:
        numRow = 0
    st.markdown('Number of labelled rows: %s'%numRow)
    button = st.button('Save Result', key = 'JN')
    resultLoc = resultWd + "\\" + resultFileName
    return resultLoc, button
            
#upload file
if option == 'Label Data':
    file = st.file_uploader("Upload file", type = ['csv'])
    #if user uploaded file
    if file:
        st.markdown("Uploaded file: %s"%"YES")
        df = load_data(file)
        col = st.selectbox("Please select col for description", sorted(df.columns))
        page_number = st.number_input(
                                        label = "Record",
                                        min_value = 1,
                                        max_value = df.shape[0],
                                        step = 1,
                                    )
        #display text
        content = df.loc[page_number - 1, col]
        st.write(content)
        
        #display tag
        finalTagList = tag_content(content)
        
        #if tag list is not empty
        if len(finalTagList)!=0:
            taggedTermList = [(content[i[0]:i[1]], i[2], tagColorDict[i[2]]) for i in finalTagList]
            #only show unique set
            annotated_text(*sorted(list(set(taggedTermList)), key = lambda x:x[1]))
        else:
            taggedTermList = []
                
        store_tempResult({page_number:taggedTermList}, {page_number:content})
#         st.write(taggedTermList)
        
    else:
        st.markdown("Please upload file before label data")
        
elif option == 'Save Result':
    #save result button
    chosenPath, buttonSR = keyInWorkingPath(2)
    
    #if click save button
    if buttonSR:  
        #check if both txt file exist
        if os.path.isfile(tagTxtFile) and os.path.isfile(contentTxtFile):

            #read text file
            with open(tagTxtFile, 'r', encoding='utf-8') as input_file:
                for row in input_file.readlines():
                    tagResult.append(json.loads(row))

            with open(contentTxtFile, 'r', encoding='utf-8') as input_file:
                for row in input_file.readlines():
                    contentResult.append(json.loads(row))

            #get latest record for every row
            dictKeys = [key for i in tagResult for key,val in i.items()]
            for finalKey in set(dictKeys):
                tempDict = {}
                tagVal = list([i for i in tagResult for key,val in i.items() if key == finalKey][-1].values())[0]
                contentVal = list([i for i in contentResult for key,val in i.items() if key == finalKey][-1].values())[0]
                tempDict['tagList'] = tagVal
                tempDict['content'] = contentVal
                finalList.append(tempDict)
                        
            #write final file
            with open(chosenPath, 'w', encoding='utf-8') as output_file:
                for dic in finalList:
                    json.dump(dic, output_file) 
                    output_file.write("\n")
            #remove temp file
            if os.path.isfile(tagTxtFile):
                os.remove(tagTxtFile)
            if os.path.isfile(contentTxtFile):
                os.remove(contentTxtFile)
            #remove temp folder
            if os.path.exists(wd + '\\' + 'TempResult'):
                os.rmdir(wd + '\\' + 'TempResult')
            
            #success msg
            st.markdown('Result is saved as %s' %chosenPath)

        else:
            st.markdown("Please label data before save result")
