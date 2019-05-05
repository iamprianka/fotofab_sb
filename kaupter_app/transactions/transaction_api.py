import os
from json import loads, dumps
from flask import request, current_app as app
from SolomoLib import Util as util
from simple_salesforce import Salesforce
from rules import rules


def example_field_map(fieldmap):
    return dumps(util.load_configuration(fieldmap))

def process_account(records):
    print(records[0]['Id'])
    accounts = []
    account = {}
    sf = util.salesforce_login()

    account = {}
    accounts = []
    sobject_dict = {}
    sobject_list = []
    fieldmap = util.load_configuration('./account/accountfieldmap.sdl')
    related = util.load_configuration('./account/accountfieldmap.related')
    objectmap = util.load_configuration('./account/objectmap.sdl')
    lus = util.load_configuration('./account/lookup.sdl')
    exids = util.load_configuration('./account/externalids.sdl')
    upkeys = util.load_configuration('./account/upsertkeys.sdl')
    rulesfile = util.load_configuration('./account/rules.sdl')

    #print('@@@RECORDS {}'.format(records))
    for data in records:

        for field in fieldmap.keys():
            #print('@@@FIELD {}'.format(field))

            if field in objectmap:
                sobject_dict[objectmap[field]] = process_related('./account/'+fieldmap[field], data[field], lus[field], data[exids['Account']], './account/objectmap.sdl')
                sobject_list.append(sobject_dict)
                sobject_dict = {}
            elif field in rulesfile:
                #print(field)
                if getattr(rules, rulesfile[field])(data[field]) is not None:
                    account[fieldmap[field]] =getattr(rules, rulesfile[field])(data[field])

            else:
                print('@@@FIELD {}'.format(field))
                if data[field] is not None:
                    account[fieldmap[field]] = data[field]
                else:
                    continue
        accounts.append(account)
        account = {}

    print('@@@ACCOUNT {}'.format('@@ACOUNT {}'.format(accounts)))
    #account_upsert = sf.bulk.Accounts.upsert('Crowdhub_ID__c/'+str(data[exids['Account']]),account) 

    account_upsert = sf.bulk.Account.upsert(accounts, 'Crowdhub_ID__c') 
    i = 0
    for obj in sobject_list:

        obj_label =list(obj.keys())[0]

        print('@@@SOBJECT LIST {}'.format(sobject_list))
        print('label: {}'.format(sobject_list[i][obj_label]))
        if len(sobject_list[i][obj_label]) >0:
            print('Current Upsert {} - {}'.format(sobject_list[i][obj_label], upkeys[obj_label]))
            result = sf.bulk.__getattr__(obj_label).upsert(sobject_list[i][obj_label], upkeys[obj_label])
            print(result)
        i = i +1

#---------Anudeep Modified February 22nd 2019--------------------------
def processAccountInformation(data):
    

    sf = util.salesforce_login()
    accountFieldmap = util.load_configuration('./accountspecificfieldmap/Account.sdl')
    createRelatedObjects = util.load_configuration('./accountspecificfieldmap/AccountRelatedObjectsMap.sdl')
    upsertSpecificFieldRulesDict = util.load_configuration('./account/rules.sdl')
    #data is in an array format so all the processing needs to be in a for loop.
    masterObjectUpsertList = []
    relatedObjectsUpsertList =[]
    processedRelatedObjectDict={}
    masterObjectName = 'account'
    for singleAccountMap in data:
        masterObjectDict = {}
        for mappedKey in singleAccountMap.keys():
            if mappedKey in accountFieldmap.keys():
                if singleAccountMap[mappedKey] != None and singleAccountMap[mappedKey] != '' and mappedKey not in upsertSpecificFieldRulesDict.keys():
                    masterObjectDict[accountFieldmap[mappedKey]] = singleAccountMap[mappedKey]
                if singleAccountMap[mappedKey] != None and singleAccountMap[mappedKey] != '' and mappedKey in upsertSpecificFieldRulesDict.keys():
                    masterObjectDict[accountFieldmap[mappedKey]] = getattr(rules, upsertSpecificFieldRulesDict[mappedKey])(singleAccountMap[mappedKey])
            #Creating Related Objects ---------------
            if mappedKey in createRelatedObjects.keys():
                if singleAccountMap[mappedKey] != None and len(singleAccountMap[mappedKey])>0:
                    relatedObjectsUpsertList.append(processAccountRelatedRecords(createRelatedObjects[mappedKey],singleAccountMap[mappedKey],singleAccountMap['Id'],masterObjectName))
            #----------------------------------------
        if masterObjectDict!= None and len(masterObjectDict.keys())>0:
            masterObjectUpsertList.append(masterObjectDict)

    if masterObjectUpsertList != None and len(masterObjectUpsertList)>0:
        try:
            print('processedRelatedObjectDict',relatedObjectsUpsertList)
            resultFromSalesforceAccountCreation = sf.bulk.Account.upsert(masterObjectUpsertList,'Crowdhub_ID__c')
            print('nothing')
        except Exception as e:
            print('AD Error Out During Account Creation line 107')
    
    relatedObjectUpsertDict={}
    if relatedObjectsUpsertList!=None and len(relatedObjectsUpsertList)>0:
        for relatedObjectApiName in createRelatedObjects.keys():
            relatedObjectConcatenatedList = []
            for relatedObjectToUpsert in relatedObjectsUpsertList:
                for relatedObjectNumberedApiName in relatedObjectToUpsert.keys():
                    if createRelatedObjects[relatedObjectApiName] in relatedObjectNumberedApiName:
                        relatedObjectConcatenatedList.append(relatedObjectToUpsert[relatedObjectNumberedApiName])
            if relatedObjectConcatenatedList!=None and len(relatedObjectConcatenatedList)>0:
                relatedObjectUpsertDict[createRelatedObjects[relatedObjectApiName]]=relatedObjectConcatenatedList

    if relatedObjectUpsertDict!=None and len(relatedObjectUpsertDict.keys())>0:
        for relatedObjectUpsertObjectName in relatedObjectUpsertDict.keys():
            try:
                relatedObjectsCreated = sf.bulk.__getattr__(relatedObjectUpsertObjectName).upsert(relatedObjectUpsertDict[relatedObjectUpsertObjectName],'Crowdhub_ID__c')
            except Exception as e:
                print('AD Exception occured. Please handle here in line 125 - ',e)



def processAccountRelatedRecords(relatedObjectSFAPIName,relatedObjectDataList,relatedAccountId,masterObjectName):
    relatedObjectFieldMap = util.load_configuration('.//'+masterObjectName+'specificfieldmap/'+relatedObjectSFAPIName+'.sdl')
    print('relatedObjectFieldMap 2',relatedObjectFieldMap)
    relatedObjectAppendingList =[]
    processedRelatedObjectInitialDict={}
    i=0
    if relatedObjectFieldMap!=None and len(relatedObjectFieldMap.keys())>0:
        for relatedObjectData in relatedObjectDataList:
            i=i+1
            appendValue=str(i)
            processedRelatedObjectMap={}
            for relatedObjKey in relatedObjectFieldMap.keys():
                if relatedObjKey in relatedObjectData.keys():
                    if relatedObjectData[relatedObjKey] != None and relatedObjectData[relatedObjKey]!='':
                        processedRelatedObjectMap[relatedObjectFieldMap[relatedObjKey]] = relatedObjectData[relatedObjKey]
                if '__r' in relatedObjKey:
                    relatedObjectUpsertExternalIdDict = {}
                    relatedObjectUpsertExternalIdDict[relatedObjectFieldMap[relatedObjKey]]=relatedAccountId
                    processedRelatedObjectMap[relatedObjKey]=relatedObjectUpsertExternalIdDict
                if 'Account' in relatedObjKey:
                    relatedObjectUpsertExternalIdDict = {}
                    relatedObjectUpsertExternalIdDict[relatedObjectFieldMap[relatedObjKey]]=relatedAccountId
                    processedRelatedObjectMap[relatedObjKey]=relatedObjectUpsertExternalIdDict
            if processedRelatedObjectMap != None and len(processedRelatedObjectMap.keys())>0:
                processedRelatedObjectInitialDict[relatedObjectSFAPIName+appendValue]=processedRelatedObjectMap
    return processedRelatedObjectInitialDict

# def createJunctionObjects(sfJuncObjAPIName,junctionObjectJsonList,primaryObjectSfName,secondaryObjectSFName,secondaryExternalID):
#     relatedJunctionObjectFieldMap = util.load_configuration('./AccountContactRelatedObjects/AccountContactRelation.sdl')
#     i=0
#     accountContactRelatedObjectDict ={}
#     for junctionObjJsonData in junctionObjectJsonList:
#         i=i+1
#         appendValue = str(i)
#         juncUpsertRelObj={}
#         for junctionObjJsonKey in junctionObjJsonData:
#             if junctionObjJsonKey in relatedJunctionObjectFieldMap.keys():
#                 if junctionObjJsonData[junctionObjJsonKey] != None and junctionObjJsonData[junctionObjJsonKey]!='':
#                     juncUpsertRelPrimExtIdDict={}
#                     juncUpsertRelPrimExtIdDict[relatedJunctionObjectFieldMap[junctionObjJsonKey]]=junctionObjJsonData[junctionObjJsonKey]
#                     juncUpsertRelObj[primaryObjectSfName]=juncUpsertRelPrimExtIdDict
#                     juncUpsertRelSecondaryExtIdDict={}
#                     juncUpsertRelSecondaryExtIdDict[relatedJunctionObjectFieldMap[junctionObjJsonKey]]=secondaryExternalID
#                     juncUpsertRelObj[secondaryObjectSFName]=juncUpsertRelSecondaryExtIdDict
#                     juncUpsertRelObj[relatedJunctionObjectFieldMap[junctionObjJsonKey]]=junctionObjJsonData[junctionObjJsonKey]+secondaryExternalID
#         if juncUpsertRelObj!=None and len(juncUpsertRelObj.keys())>0:
#             print('juncUpsertRelObj----------->',juncUpsertRelObj)
#             accountContactRelatedObjectDict[sfJuncObjAPIName+appendValue]=juncUpsertRelObj
#     return accountContactRelatedObjectDict

def processInformationForListWithNoKeys(masterObjectName,sfObjAPIName,listValuesData,crowdHubUniqueRecID):
    print('sfObjAPIName',sfObjAPIName)
    relatedObjectFieldMap = util.load_configuration('.//'+masterObjectName+'specificfieldmap/'+sfObjAPIName+'.sdl')
    relatedObjectNoKeyValueList=[]
    relatedObjectNoKeyValueDict={}
    for listItem in listValuesData:
        relatedObjectDict={}
        if listItem != None:
            for relatedObjKey in relatedObjectFieldMap.keys():
                print('type(listItem)---------',type(listItem))
                if type(listItem)==str:
                    if relatedObjKey=='Name':
                        relatedObjectDict[relatedObjectFieldMap[relatedObjKey]] = listItem
                        if len(listItem)>=80:
                            relatedObjectDict[relatedObjectFieldMap[relatedObjKey]] = listItem[:79]
                    if '__r' in relatedObjKey :
                        relatedMasterDict={}
                        relatedMasterDict[relatedObjectFieldMap[relatedObjKey]]=crowdHubUniqueRecID
                        relatedObjectDict[relatedObjKey]=relatedMasterDict
                    if '__c' in relatedObjKey:
                       relatedObjectDict[relatedObjectFieldMap[relatedObjKey]] = listItem+crowdHubUniqueRecID
                if type(listItem) == dict:
                    if relatedObjKey in listItem.keys():
                        if listItem[relatedObjKey]!=None and listItem[relatedObjKey]!='':
                            relatedObjectDict[relatedObjectFieldMap[relatedObjKey]]=listItem[relatedObjKey]
                        print('relatedObjKey$$$$$$$$$$$$$$$',relatedObjKey)
                    if '__r' in relatedObjKey :
                        relatedMasterDict={}
                        relatedMasterDict[relatedObjectFieldMap[relatedObjKey]]=crowdHubUniqueRecID
                        relatedObjectDict[relatedObjKey]=relatedMasterDict
                        print('Forum Posts',relatedObjectDict[relatedObjKey])
            if relatedObjectDict!=None:
                relatedObjectNoKeyValueList.append(relatedObjectDict)
    relatedObjectNoKeyValueDict[sfObjAPIName]=relatedObjectNoKeyValueList
    return relatedObjectNoKeyValueDict


def processContactInformation(contactRecordsListFromCrowdHub):
    #print('Contact DATA',contactRecordsListFromCrowdHub)
    sf = util.salesforce_login()
    contactFieldMap = util.load_configuration('./Contactspecificfieldmap/Contact.sdl')
    contactRelatedObjectsWithoutKeyValue=util.load_configuration('./Contactspecificfieldmap/ContactRelatedObjectNoKeyValue.sdl')
    # print('contactRelatedObjectsWithoutKeyValue',contactRelatedObjectsWithoutKeyValue)
    #accountContactRelatedObjectFieldMap = util.load_configuration('./AccountContactRelatedObjects/AccountContactRelatedObjectMap.sdl')
    #print('accountContactRelatedObjectFieldMap',accountContactRelatedObjectFieldMap)
    contactRecordsSFUpsertMasterList=[]
    accConRelatedJuncObjectList=[]
    accRelatedObjectList=[]
    accountContactRelatedObjectSFUpsertDict={}
    masterobject = 'Contact'
    primObj='Account'
    secObj4JuncObj='Contact'
    relatedObjectNoKeyValueList=[]
    relatedObjectNoKeyValueDict={}
    
    i=0
    for contactRecordJson in contactRecordsListFromCrowdHub:
        i=i+1
        appendValue = str(i)
        contactRecordMasterDict={}
        for conRecJsonKey in contactRecordJson.keys():
            if conRecJsonKey in contactFieldMap.keys():
                if contactRecordJson[conRecJsonKey]!=None and contactRecordJson[conRecJsonKey]!='':
                    contactRecordMasterDict[contactFieldMap[conRecJsonKey]]=contactRecordJson[conRecJsonKey]
            if conRecJsonKey =='Companies' and contactRecordJson[conRecJsonKey]!=None and contactRecordJson[conRecJsonKey]!='' and len(contactRecordJson[conRecJsonKey])>0:
                print('I am here at line 241',len(contactRecordJson[conRecJsonKey]))
                masterObjectDict={}
                #print('contactRecordJson[conRec',contactRecordJson[conRecJsonKey][0]['company_id'])
                masterObjectDict[contactFieldMap[primObj]]=contactRecordJson[conRecJsonKey][0]['company_id']
                contactRecordMasterDict[primObj]=masterObjectDict
            if conRecJsonKey in contactRelatedObjectsWithoutKeyValue.keys():
                if contactRecordJson[conRecJsonKey]!=None and len(contactRecordJson[conRecJsonKey])>0:
                    #relatedObjectNoKeyValueDict[contactRelatedObjectsWithoutKeyValue[conRecJsonKey]+appendValue]= processInformationForListWithNoKeys(masterobject,contactRelatedObjectsWithoutKeyValue[conRecJsonKey],contactRecordJson[conRecJsonKey],contactRecordJson['Id'])
                    relatedObjectNoKeyValueList.append(processInformationForListWithNoKeys(masterobject,contactRelatedObjectsWithoutKeyValue[conRecJsonKey],contactRecordJson[conRecJsonKey],contactRecordJson['Id']))
            # if conRecJsonKey in accountContactRelatedObjectFieldMap.keys():
            #     if contactRecordJson[conRecJsonKey]!=None and contactRecordJson[conRecJsonKey]!='':
            #         accConRelatedJuncObjectList.append(createJunctionObjects(accountContactRelatedObjectFieldMap[conRecJsonKey],contactRecordJson[conRecJsonKey],primObj4JuncObj,secObj4JuncObj,contactRecordJson['Id']))
        if contactRecordMasterDict!=None and len(contactRecordMasterDict.keys())>0:
            contactRecordsSFUpsertMasterList.append(contactRecordMasterDict)

    #print('contactRecordsSFUpsertMasterList',contactRecordsSFUpsertMasterList)
    #print('relatedObjectNoKeyValueList',relatedObjectNoKeyValueList)


    if contactRecordsSFUpsertMasterList!=None and len(contactRecordsSFUpsertMasterList)>0:
        try:
            contactRecordsUpsert = sf.bulk.Contact.upsert(contactRecordsSFUpsertMasterList,'Crowdhub_ID__c')
        except Exception as e:
            print('AD Contacts Encountered an Error Check Line 178 - ',e)

    for relatedObjKey in contactRelatedObjectsWithoutKeyValue.keys():
        concatenatedList=[]
        for payloadtoUpsert in relatedObjectNoKeyValueList:
            if contactRelatedObjectsWithoutKeyValue[relatedObjKey] in payloadtoUpsert.keys():
                for relatedObjectmap in payloadtoUpsert[contactRelatedObjectsWithoutKeyValue[relatedObjKey]]:
                    #print('relatedObjectmap',relatedObjectmap)
                    concatenatedList.append(relatedObjectmap)


        relatedObjectNoKeyValueDict[contactRelatedObjectsWithoutKeyValue[relatedObjKey]]=concatenatedList

    if relatedObjectNoKeyValueDict!=None and len(relatedObjectNoKeyValueDict.keys())>0:
        for relatedObjectWithoutKeyValueName in relatedObjectNoKeyValueDict.keys():
            try:
                if relatedObjectNoKeyValueDict[relatedObjectWithoutKeyValueName] != None and len(relatedObjectNoKeyValueDict[relatedObjectWithoutKeyValueName])>0:
                    print('-------------------relatedObjectWithoutKeyValueName---------------------',relatedObjectWithoutKeyValueName)
                    print('relatedObjectNoKeyValueDict',relatedObjectNoKeyValueDict[relatedObjectWithoutKeyValueName])
                    upsertedObjects = sf.bulk.__getattr__(relatedObjectWithoutKeyValueName).upsert(relatedObjectNoKeyValueDict[relatedObjectWithoutKeyValueName],'Crowdhub_ID__c')
            except Exception as e:
                print('-----------------FAILED RECORDS$$$$$$$$$$$---------',relatedObjectNoKeyValueDict[relatedObjectWithoutKeyValueName])
                print('AD There is an error in the related objects without key value line number 284 - ',e)


    # if accConRelatedJuncObjectList != None and len(accConRelatedJuncObjectList)>0:
    #     for accConObjAPIName in accountContactRelatedObjectFieldMap.keys():
    #         relatedObjectUpsertList=[]
    #         for accConRelObjDict in  accConRelatedJuncObjectList:
    #             for accConRelObjKey in accConRelObjDict.keys():
    #                 if accountContactRelatedObjectFieldMap[accConObjAPIName] in accConRelObjKey:
    #                     relatedObjectUpsertList.append(accConRelObjDict[accConRelObjKey])
    #         accountContactRelatedObjectSFUpsertDict[accountContactRelatedObjectFieldMap[accConObjAPIName]]=relatedObjectUpsertList
    #         # print('relatedObjectUpsertList------',relatedObjectUpsertList)
    #         # print('relatedObjectUpsertDict-------',relatedObjectUpsertDict)

    # if accountContactRelatedObjectSFUpsertDict!=None and len(accountContactRelatedObjectSFUpsertDict.keys())>0:
    #     for accountObjSFAPIName in accountContactRelatedObjectSFUpsertDict.keys():
    #         try:
    #             print('Nothing')
    #             #upsertAccConRelatedRecs = sf.bulk.__getattr__(accountObjSFAPIName).upsert(accountContactRelatedObjectSFUpsertDict[accountObjSFAPIName],'Crowdhub_ID__c')
    #         except Exception as e:
    #             print('AD Account Contact Related Objects Are Failing On Line 228.',e)





#----------------------------------------------------------------------
def process_contact(records):
    print('@@@@record {}'.format(records))
    sf = util.salesforce_login()

    contact = {}
    contacts = []
    sobject_dict = {}
    sobject_list = []

    related_contacts = []
    related_contact = {}

    fieldmap = util.load_configuration('./contact/contactfieldmap.sdl')
    related = util.load_configuration('./contact/contactfieldmap.related')
    objectmap = util.load_configuration('./contact/objectmap.sdl')
    lus = util.load_configuration('./contact/lookup.sdl')
    exids = util.load_configuration('./contact/externalids.sdl')
    upkeys = util.load_configuration('./contact/upsertkeys.sdl')
    rulesfile = util.load_configuration('./contact/rules.sdl')

    for data in records:

        for field in fieldmap.keys():

            if field in objectmap:
                sobject_dict[objectmap[field]] = process_related('./contact/'+fieldmap[field], data[field], lus[field], data[exids['Contact']], './Contact/objectmap.sdl')
                sobject_list.append(sobject_dict)
                sobject_dict = {}
            elif field == 'Companies':

                account_set = False
                for rac in data['Companies']:
                    if account_set == False:
                        #contacts need to be associated with an account.  Otherwise, we cannot
                        #create a related contact record because the contact will be considered private
                        contact['Account'] = dict([('Crowdhub_ID__c', rac['company_id'])])

                        account_set = True
                    else:
                        related_contact['Account'] = dict([('Crowdhub_ID__c', rac['company_id'])])
                        related_contact['Contact'] = dict([('Crowdhub_ID__c', data['Id'])])
                        related_contact['Crowdhub_ID__c'] = rac['company_id'] + data['Id']
                        related_contacts.append(related_contact)
                        related_contact = {}
                #rac_upsert = sf.bulk.AccountContactRelation.upsert(related_contacts, 'Crowdhub_ID__c') 
            elif field in rulesfile:
                print(field)
                if getattr(rules, rulesfile[field])(data[field]) is not None:
                    contact[fieldmap[field]] =getattr(rules, rulesfile[field])(data[field])

            else:
                #print('@@@FIELD {} - {}'.format(field, data))
                if data[field] is not None: 
                    contact[fieldmap[field]] = data[field]
        contacts.append(contact)
        contact = {}

    contact_upsert = sf.bulk.Contact.upsert(contacts, 'Crowdhub_ID__c') 
    print('@@@CONTACT: {}'.format(contacts))
    rac_upsert = sf.bulk.AccountContactRelation.upsert(related_contacts, 'Crowdhub_ID__c') 
    print('@@RAC RESULT {}'.format(related_contacts))
    i = 0
    for obj in sobject_list:
        obj_label =list(obj.keys())[0]

        #try:
        print(sobject_list[i][obj_label])
        #print('@@@{} - {}'.format(obj[upkeys[obj_label]], list(obj.keys())[0]))
        if len(sobject_list[i][obj_label]) >0:
            result = sf.bulk.__getattr__(obj_label).upsert(sobject_list[i][obj_label], upkeys[obj_label])
            print(result)
        i = i + 1

"""this method creates lists of records to be upserted in to Salesforce
    from nested collections in the json payload. 

    args are:  mapfile is the field map, data is the nested collection from the json payload,
    lu is the lookup field, exid is the external id to be passed with the lookup field and objectmap
    is the list of the objects by the field in the json payload"""
def process_related(mapfile, data, lu, exid, objectmap):

    #objects holds the map of the nested collections to the sobjects in Salesforce
    objects = util.load_configuration(objectmap)

    #the mapfile is the name of the file holding the fields to be mapped
    fieldmap = util.load_configuration(mapfile)

    #dictionary and list that hold the nested collections
    sobject = {}
    sobjects = []

    """first, determine if there's a corresponding key value.  not all 
       nested collections have a key value, such as when there is only one
       text value"""
    if fieldmap is not None:
        #iterate through each record in the collection
        for record in data:
            if exid is not None:
                sobject[lu.split("\\:")[0]] = dict([(lu.split("\\:")[1], exid)])
                #sobject[lu] = exid
            for origfield in fieldmap.keys():

                sobject[fieldmap[origfield]] = record[origfield]

            sobjects.append(sobject)
            sobject = {}

    if len(fieldmap)==0:
        for record in data:
            if exid is not None:
                sobject[lu] = exid
            sobject['Name'] = record


    return sobjects
