
import re
import enchant

#british dict
d = enchant.Dict("en_GB")

#import stopword
stopWordList = []
txtFile = "D:\\Users\\figohjs\\Documents\\NLP\\NER\\Data\\training\\stopwords.txt"
with open(txtFile, 'r') as myfile:
    for row in myfile.readlines():
        stopWordList.append(re.sub('\n','',row))

#import surname
surnameList = []
txtFile = "D:\\Users\\figohjs\\Documents\\NLP\\NER\\Data\\training\\surname.txt"
with open(txtFile, 'r') as myfile:
    for row in myfile.readlines():
        surnameList.append(re.sub('\n','',row))

#first layer of text cleaning
def cleanText(text):
    #special chars list
    scList = ['\si.e.\s']
    
    #remove null in end of sentence
    text = re.sub('null $', '', text, flags = re.I)
    #remove rm as training data does not have rm
    text = re.sub('(rm|myr)\s*(\d+)', r'\2', text, flags = re.I)
    #remove special char 
    text = re.sub('|'.join(scList), '', text)
    #remove additional spaces
    text = re.sub('(\s)+', r'\1', text)        
    return text

#change case by checking dictionary, capitalize if it s not found in dict
def changeCase(text):
    tempList = []
    #clean text first before split
    text = re.sub('\n|\t', ' ',re.sub('\r', '', text))
    #special char list
    scList = [':', ',', '(', ')', '.']
    
    for word in text.split(' '):
        #if not empty string after remove special chars
        if re.sub(r',|:|\.', '', word).strip() != '':
            cleanWord = re.sub(r',|:|\.', '', word).strip()
            #if cleanWord can be found in dict and cleanWord is not found in surnameList (chinese names)
            if d.check(cleanWord.lower()) and cleanWord.lower() not in surnameList:
                finalWord = word.lower()     
            else:
                #if first char in word in scList
                if word[0] in scList:
                    finalWord = word[0] + word[1:].capitalize()
                else:
                    finalWord = word.capitalize()
                    
            tempList.append(finalWord)
    
    #join every words in tempList with space
    sentence = ' '.join(tempList)
    
#     sentence = ' '.join([word if word == '' else word.lower() 
#                      if d.check(re.sub(r',|:|\.', '', word)) and re.sub(r',|:|\.', '', word).lower() not in surnameList
#                          else word.capitalize() 
#                      for word in text.split(' ')])
    return sentence

#second layer of text cleaning - sentence case companies/banks name
def changeCase2(text):
    nameList = ['bank', 'berhad', 'bhd', 'enterprise', 'shop', 'trading', 'agency']
    nameListPattern = re.compile('|'.join(['\s(\w+\s' + i +')\s' for i in nameList]), re.IGNORECASE)
    #any 
    matchList = [j for i in re.findall(nameListPattern, text) for j in i if j!='']
    scList = ['(', ')']
    
    for match in matchList:
        firstWord = match.split(' ')[0]
        #second word is element to nameList: bank, berhad, bhd, enterprise
        secondWord = match.split(' ')[1]
        #default targetWord and replaceWord
        targetWord = match
        replaceWord = match
        
        #if word before namelist is not in stopwordlist and not digit
        if firstWord not in stopWordList and not firstWord.isdigit():
            #capitalize both words
            replaceWord = firstWord.capitalize() + ' ' + secondWord.capitalize()
            #if still can find first word in desc
            if firstWord in text.split(' '):
                firstWordIndex = text.split(' ').index(firstWord)
                if firstWordIndex != 0:
                    b4FirstWord = text.split(' ')[firstWordIndex - 1]
                    b4FirstWord2 = re.sub(r',|:|\.|\(|\)', '', b4FirstWord)
                    if b4FirstWord2 not in stopWordList:
                        targetWord = b4FirstWord + ' ' + targetWord
                        replaceWord = b4FirstWord2.capitalize() + ' ' + replaceWord 
                        if firstWordIndex - 1 != 0:
                            b4b4FirstWord = text.split(' ')[firstWordIndex - 2]
                            b4b4FirstWord2 = re.sub(r',|:|\.|\(|\)', '', b4b4FirstWord)
                            if b4b4FirstWord2 not in stopWordList:
                                targetWord = b4b4FirstWord + ' ' + targetWord
                                replaceWord = b4b4FirstWord2.capitalize() + ' ' + replaceWord
        #replace targetWord with replaceWord
#         print(targetWord + ":" + replaceWord)
        #add escape sign to special char (avoid eror of unbalanced parenthesis)
#         if re.search('|'.join(scList), targetWord):
#             targetWord = re.escape(targetWord)
#         if re.search('|'.join(scList), replaceWord):
#             replaceWord = re.escape(replaceWord)
        text = re.sub(re.escape(targetWord), '%s'%re.escape(replaceWord), text)
        #final clean up
        text = re.sub(r"\\", "", text)
    return text


#change case for chinese name capitalize 3 consecutive words
def changeCase3(text):
    surnameListPattern = re.compile('|'.join(['\s'+ i + '\s' for i in surnameList]), re.IGNORECASE)
    #any 
    matchList = re.findall(surnameListPattern, text)
    wordList = text.split(' ')
    
    for match in matchList:
        index = wordList.index(match.strip())
        if (index + 2) <= len(wordList):
            targetWords = ' '.join(wordList[index: index + 3])
            replaceWords = ' '.join([i.capitalize() for i in wordList[index: index + 3]])
#             print(targetWords + ":" + replaceWords)
            text = re.sub(re.escape(targetWords), '%s'%re.escape(replaceWords), text)
    
    #final clean up
    text = re.sub(r"\\", "", text)
    
    return text

#default features used in nltk
def word2features(sent, i):
    word = sent[i][0]
#     postag = sent[i][1]

    features = {
        'bias': 1.0,
#         'ori':word,
        'word.lower()': word.lower(),
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
#         'postag': postag,
#         'postag[:2]': postag[:2],
    }
    if i > 0:
        word1 = sent[i-1][0]
#         postag1 = sent[i-1][1]
        features.update({
            '-1:word.lower()': word1.lower(),
            '-1:word.istitle()': word1.istitle(),
            '-1:word.isupper()': word1.isupper(),
#             '-1:postag': postag1,
#             '-1:postag[:2]': postag1[:2],
        })
    else:
        #beginning of speech
        features['BOS'] = True

    if i < len(sent)-1:
        word1 = sent[i+1][0]
#         postag1 = sent[i+1][1]
        features.update({
            '+1:word.lower()': word1.lower(),
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper(),
#             '+1:postag': postag1,
#             '+1:postag[:2]': postag1[:2],
        })
    else:
        #end of speech
        features['EOS'] = True
    return features

def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, postag, label in sent]

def sent2tokens(sent):
    return [token for token, postag, label in sent]

def generateFeatures(descList):
    featuresList = []
    
    for desc in descList: 
        sample = [(i,) for i in desc.split(' ')]
        sampleFeatures = [sent2features(i) for i in [sample]]
        featuresList.append(sampleFeatures[0])
    
    return featuresList

#tag dictionary
tagDict = {'org':'ORG', 'per':'PERSON', 'geo': 'GEO'}

def getNamedEntity(records, text):
    finalResult = []
    for noRow, row in enumerate(records):
        temp = []
        for noTerm, term in enumerate(row):
            #if token is beginning of org or per
            if term in ['B-' + i for i in tagDict.keys()]:
                tagType = term.split('-')[1]
                namedEnt = text[noRow][noTerm]
                #if current term is not the last term of the row
                if (noTerm + 1) != len(row):
                    if row[noTerm + 1] != ('I-' + tagType):
                        tempResult = checkTuple((namedEnt, tagDict[tagType]))
                        if tempResult:
                            temp.append(tempResult)
                            
                else:
                    tempResult = checkTuple((namedEnt, tagDict[tagType]))
                    if tempResult:
                        temp.append(tempResult)

            #if token is inside org or per
            elif term in ['I-org', 'I-per', 'I-geo']:
                tagType = term.split('-')[1]
                namedEnt = ' '.join([namedEnt, text[noRow][noTerm]])
                #if current term is not the last term of the row
                if (noTerm + 1) != len(row):
                    if row[noTerm + 1] != ('I-' + tagType):
                        tempResult = checkTuple((namedEnt, tagDict[tagType]))
                        if tempResult:
                            temp.append(tempResult)   

                else:
                    tempResult = checkTuple((namedEnt, tagDict[tagType]))
                    if tempResult:
                        temp.append(tempResult)
                        
        finalResult.append(temp)
            
    return finalResult  

def checkTuple(tupleResult):
    if tupleResult[1] in ['PERSON', 'GEO']:
        if re.search('berhad|bhd', tupleResult[0], flags = re.I):
            return (tupleResult[0], 'ORG')
        else:
            #filter out geo
            if tupleResult[1] == 'GEO':
                return None
            else:
                return tupleResult
            
    elif tupleResult[1] == 'ORG':
        #put chinese name back as label
        if len(tupleResult[0].split(' ')) == 3 and not re.search('berhad|bhd', tupleResult[0], flags = re.I):
            if tupleResult[0].split(' ')[0].lower() in surnameList:
                return (tupleResult[0], 'PERSON')
            else:
                return tupleResult
        else:
            return tupleResult
    else:
        return tupleResult
