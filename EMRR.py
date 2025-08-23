
import numpy as np
import threading
import math
import Setting
import Data

#with open("content/mu_bs_pickle", "rb") as mu_loc_object:
#    all_mu_bs = pickle.load(mu_loc_object)
##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
def pop_InProcess(key):
    req = [x for x in Setting.inprocessreqs if x[0] == key]   
    if (len(req)>0):
      Setting.inprocessreqs.remove(req[0])
##------------------------------------------------------------------------------------------##
def push_InProcess(key, user, reqtime, fileName, fileSize, type, expireTime, startTime, iotZone):  

    index = -1
    if ((Setting.priority_strategy == "TYPE"  or Setting.priority_strategy == "TYPESIZE")  and type == "A"):
        index = 0
    else:
        for i in range(len(Setting.inprocessreqs)):
            itime = Setting.inprocessreqs[i][2]
            isize = Setting.inprocessreqs[i][4]
            itype = Setting.inprocessreqs[i][5]


            if (Setting.priority_strategy == "NO" and itime > reqtime):
                index = i
                break
            
            if (Setting.priority_strategy == "TYPE" and (itime > reqtime or (itime == reqtime and itype > type) )):
                index = i
                break
            if (Setting.priority_strategy == "TYPESIZE" and 
                    (itime > reqtime or (itime == reqtime and (itype > type or (itype == type and isize > fileSize)  ) )
                    
                    )):
                index = i
                break
            if (Setting.priority_strategy == "TYPESIZETIME") :  
               if (reqtime - startTime > 4000):
                   if (itype > type ):
                        index = i
                        break
               else:         
                   if (itime > reqtime or (itime == reqtime and (itype > type or (itype == type and isize > fileSize) ) )):
                        index = i
                        break




    if (index > -1):
        Setting.inprocessreqs.insert(index,[key, user, reqtime, fileName, fileSize,type, expireTime, startTime, iotZone])
    else:    
         Setting.inprocessreqs.append([key, user, reqtime, fileName, fileSize,type, expireTime, startTime, iotZone])
    # print("-----queue-------")
    # print(Setting.inprocessreqs)
    # print([key, user, reqtime, fileName, fileSize,type, expireTime, startTime, iotZone])

    return

def push_InProcess_Init(key, user, reqtime, fileName, fileSize, type, expireTime, startTime, iotZone):  

    index = -1

    for i in range(len(Setting.inprocessreqs)):
        itime = Setting.inprocessreqs[i][2]
        isize = Setting.inprocessreqs[i][4]
        itype = Setting.inprocessreqs[i][5]


        if (Setting.priority_strategy == "NO" and itime > reqtime):
            index = i
            break
        if (Setting.priority_strategy == "TYPE" and (itime > reqtime or (itime == reqtime and itype > type) )):
            index = i
            break
        if (Setting.priority_strategy == "TYPESIZE" and 
                (itime > reqtime or (itime == reqtime and (itype > type or (itype == type and isize > fileSize)  ) )
                  
                 )):
            index = i
            break

    if (index > -1):
        Setting.inprocessreqs.insert(index,[key, user, reqtime, fileName, fileSize,type, expireTime, startTime, iotZone])
    else:    
         Setting.inprocessreqs.append([key, user, reqtime, fileName, fileSize,type, expireTime, startTime, iotZone])
    # print("-----queue-------")
    # print(Setting.inprocessreqs)
    # print([key, user, reqtime, fileName, fileSize,type, expireTime, startTime, iotZone])

    return
##------------------------------------------------------------------------------------------##
def miss_Process(key, antenna, user, reqtime, reqtype, fileName, remindSize, starttime):
    antennaindex = abs(antenna)
    if (antenna<0):          
        Setting.mbs_antena_log[antennaindex][3] += 1
    else:    
        Setting.sbs_antena_log[antennaindex][3] += 1
    Setting.missing_log.append([user,reqtime,antenna,fileName, reqtype, remindSize])
    request_Log_Update(key, starttime, reqtime, "MISS")    
    pop_InProcess(key)
    return
##------------------------------------------------------------------------------------------##
def getAntennaStayingTime(user, reqtime, antenna , checkparent = False):
    staytime = len(Setting.mu_bs[user])
    for i in range(int(reqtime),len(Setting.mu_bs[user])):
        new_t = Setting.mu_bs[user][i]        
        if (checkparent):
            new_t = find_mbs_antenna(new_t)
        if new_t != antenna:
            staytime = i
            break

    return staytime
##------------------------------------------------------------------------------------------##
def getStackQueueEmptyTime(user, reqtime, antenna): 
    reqtime = int(reqtime)
    antennaindex = abs(antenna)
    index = -1
    if reqtime > Setting.sim_time:
       return -1

    if (antenna<0):          
        if Setting.mbs_queue[antennaindex][reqtime] == -1:
            index = reqtime
            Setting.mbs_queue[antennaindex][reqtime] = user
        else:
            for i in range(reqtime,len(Setting.mbs_queue[antennaindex])):
                n = Setting.mbs_queue[antennaindex][i]
                if n == -1:
                    index = i
                    break
    else:
        if Setting.sbs_queue[antennaindex][reqtime] == -1:
            index = reqtime
            Setting.sbs_queue[antennaindex][reqtime] = user
        else:
            for i in range(reqtime,len(Setting.sbs_queue[antennaindex])):
                n = Setting.sbs_queue[antennaindex][i]
                if n == -1:
                    index = i
                    break
    return index
##------------------------------------------------------------------------------------------##
def find_mbs_antenna(antennacode):
    if (antennacode < 0):
        return antennacode
    
    for mbs in range(len(Setting.antenna_position)):
        if (antennacode in Setting.antenna_position[mbs]):
            break

    return -1*mbs

##---------------------------------------##
##                LOG                    ##
##---------------------------------------##
#["User","RequestCount", "RequestSize", "RequestDone", "RequestMiss", "ResponseTime"]
def summary_User_Log_Update(user, fileSize, done, miss, starttime, endtime):
    index = -1
    for i in range(len(Setting.summary_user_log)):
        if (Setting.summary_user_log[i][0]==user):
            index=i
            break

    if (index == -1):
        Setting.summary_user_log.append([user, 1, fileSize, done, miss, (endtime - starttime)+1])
    else:
        Setting.summary_user_log[index][1] += 1
        Setting.summary_user_log[index][2] += fileSize
        Setting.summary_user_log[index][3] += done #RequestDone
        Setting.summary_user_log[index][4] += miss #RequestMiss
        Setting.summary_user_log[index][5] += (endtime - starttime)+1 #ResponceTime


##------------------------------------------------------------------------------------------##
# ["RequestType", "RequestCount", "RequestSize", "RequestDone", "RequestMiss", "ResponseTime"]
def summary_ReqType_Log_Update(type, fileSize, done, miss, time):  
    index = -1
    for i in range(len(Setting.req_type)):
        if (Setting.summary_reqtype_log[i][0]==type):
            index=i
            break
    if (index == -1):
        print("Request Type not found !!!")
    else:
        Setting.summary_reqtype_log[index][1] += 1
        Setting.summary_reqtype_log[index][2] += fileSize #RequestSize        
        Setting.summary_reqtype_log[index][3] += done
        Setting.summary_reqtype_log[index][4] += miss
        Setting.summary_reqtype_log[index][5] += time
##------------------------------------------------------------------------------------------##
def request_Log_Add(key, user, type, filename, filesize, reqtime):
    Setting.request_log.append([key, user, type, filename, filesize, reqtime, 0, 0, ""])

#["key", "user", "type", "fileName", "fileSize", "reqtime", "starttime", "endtime", "status"]
def request_Log_Update(key, starttime, endtime, status):
    index = -1
    for i in range(len(Setting.request_log)):
        if (Setting.request_log[i][0]==key):
            index=i
            break
    if (index > -1):        
        Setting.request_log[i][6] = starttime
        Setting.request_log[i][7] = endtime
        Setting.request_log[i][8] = status

##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
def removeMix(antenna, type, neededsize, strategy):
    antennaindex = abs(antenna)
    sortedList = []
    if (antenna < 0):
        if (strategy == "LRU"):
            sortedList = sorted(Setting.mbs_cache[antennaindex], key=lambda x: x[3])
        if (strategy == "LFU"):
            sortedList = sorted(Setting.mbs_cache[antennaindex], key=lambda x: x[4])
        size = 0
        index = -1
        for i in range(0,len(sortedList)): 
            size += sortedList[i][3]
            if (size >= neededsize):
                index = i
                break
        if (index != -1):
            Setting.mbs_cache[antennaindex] = sortedList[i+1:]
        else:
            print("somthing happend in cleaning chache!!!")        
            return
    else:  
        if (strategy == "LRU"):
            sortedList = sorted(Setting.sbs_cache[antennaindex], key=lambda x: x[3])
        if (strategy == "LFU"):
            sortedList = sorted(Setting.sbs_cache[antennaindex], key=lambda x: x[4])
    
        size = 0
        index = -1
        for i in range(0,len(sortedList)): 
            size += sortedList[i][1]
            if (size >= neededsize):
                index = i
                break
        if (index >-1):
            Setting.sbs_cache[antennaindex] = sortedList[i+1:]
        else:
            print("somthing happend in cleaning chache!!!")        
            return
        
def removeType(antenna, type, neededsize, strategy):
    antennaindex = abs(antenna)
    sortedList = []


    if (antenna < 0):
        alist = filter(lambda x: x[2] == "A", Setting.mbs_cache[antennaindex])
        blist = filter(lambda x: x[2] == "B", Setting.mbs_cache[antennaindex])
        clist = filter(lambda x: x[2] == "C", Setting.mbs_cache[antennaindex])
        sortedList = []
        if (strategy == "LRU"):
            if (type == "A"):
                sortedList = sorted(alist, key=lambda x: x[3])
            if (type == "B"):
                sortedList = sorted(blist, key=lambda x: x[3])
            if (type == "C"):
                sortedList = sorted(clist, key=lambda x: x[3])
        if (strategy == "LFU"):
            if (type == "A"):
                selflist = filter(lambda x:not("_" in x[0]), alist)
                otherList = filter(lambda x: "_" in x[0], alist)

                sortedSelfList = sorted(selflist, key=lambda x: x[4])
                sortedOtherList = sorted(otherList, key=lambda x: x[4])
                sortedList = sortedOtherList + sortedSelfList  

            if (type == "B"):
                sortedList = sorted(blist, key=lambda x: x[4])
            if (type == "C"):
                sortedList = sorted(clist, key=lambda x: x[4])

        size = 0
        index = -1
        for i in range(0,len(sortedList)): 
            size += sortedList[i][3]
            if (size >= neededsize):
                index = i
                break
        if (index >-1):
            finalList = []
            if (type == "A"):
                finalList = list(blist) + list(clist) + sortedList[i+1:]
            if (type == "B"):
                finalList = list(alist) + list(clist) + sortedList[i+1:]
            if (type == "C"):
                finalList = list(blist) + list(alist) + sortedList[i+1:]
            Setting.mbs_cache[antennaindex] = finalList
        else:
            print("somthing happend in cleaning chache!!!")        
            return
        # print("remove mbs cach :"+ str(antennaindex))
        # for i,item in enumerate(Setting.mbs_cache[antennaindex]):
        #     print(item)
        
    else:   
        alist = filter(lambda x: x[2] == "A", Setting.sbs_cache[antennaindex])
        blist = filter(lambda x: x[2] == "B", Setting.sbs_cache[antennaindex])
        clist = filter(lambda x: x[2] == "C", Setting.sbs_cache[antennaindex])
        sortedList = []
        if (strategy == "LRU"):
            if (type == "A"):
                sortedList = sorted(alist, key=lambda x: x[3])
            if (type == "B"):
                sortedList = sorted(blist, key=lambda x: x[3])
            if (type == "C"):
                sortedList = sorted(clist, key=lambda x: x[3])
        if (strategy == "LFU"):
            if (type == "A"):
                sortedList = sorted(alist, key=lambda x: x[4])
            if (type == "B"):
                sortedList = sorted(blist, key=lambda x: x[4])
            if (type == "C"):
                sortedList = sorted(clist, key=lambda x: x[4])

        size = 0
        index = -1
        for i in range(0,len(sortedList)): 
            size += sortedList[i][1]
            if (size >= neededsize):
                index = i
                break
        if (index >-1):
            finalList = []
            if (type == "A"):
                finalList = list(blist) + list(clist) + sortedList[i+1:]
            if (type == "B"):
                finalList = list(alist) + list(clist) + sortedList[i+1:]
            if (type == "C"):
                finalList = list(blist) + list(alist) + sortedList[i+1:]
            Setting.sbs_cache[antennaindex] = finalList
        else:
            print("somthing happend in cleaning chache!!!")        
            return
        # print("remove sbs cach :"+ str(antennaindex))
        # for i,item in enumerate(Setting.sbs_cache[antennaindex]):
        #     print(item)

def removeRate(antenna, type, neededsize, strategy):
    antennaindex = abs(antenna)
    sortedList = []

    if (antenna < 0):
        alist = filter(lambda x: x[2] == "A", Setting.mbs_cache[antennaindex])
        blist = filter(lambda x: x[2] == "B", Setting.mbs_cache[antennaindex])
        clist = filter(lambda x: x[2] == "C" and x[6] < 1, Setting.mbs_cache[antennaindex])
        #
        sortedList = []

        if (type == "A"):
            sortedList = sorted(alist, key=lambda x: (x[6], x[3]))
        if (type == "B"):
            sortedList = sorted(blist, key=lambda x: (x[6], x[3]))
        if (type == "C"):
            sortedList = sorted(clist, key=lambda x: (x[6], x[3]))

        size = 0
        index = -1
        for i in range(0,len(sortedList)): 
            size += sortedList[i][3]
            if (size >= neededsize):
                index = i
                break
        if (index >-1):
            finalList = []
            if (type == "A"):
                finalList = list(blist) + list(clist) + sortedList[i+1:]
            if (type == "B"):
                finalList = list(alist) + list(clist) + sortedList[i+1:]
            if (type == "C"):
                finalList = list(blist) + list(alist) + sortedList[i+1:]
            Setting.mbs_cache[antennaindex] = finalList
        else:
            print("somthing happend in cleaning chache!!!")        
            return
        # print("remove mbs cach :"+ str(antennaindex))
        # for i,item in enumerate(Setting.mbs_cache[antennaindex]):
        #     print(item)
        
    else:   
        alist = filter(lambda x: x[2] == "A", Setting.sbs_cache[antennaindex])
        blist = filter(lambda x: x[2] == "B", Setting.sbs_cache[antennaindex])
        clist = filter(lambda x: x[2] == "C" and x[6] < 1, Setting.sbs_cache[antennaindex])
        sortedList = []
        if (type == "A"):
            sortedList = sorted(alist, key=lambda x: (x[6], x[3]))
        if (type == "B"):
            sortedList = sorted(blist, key=lambda x: (x[6], x[3]))
        if (type == "C"):
            sortedList = sorted(clist, key=lambda x: (x[6], x[3]))

        size = 0
        index = -1
        if (len(sortedList) > 0):
            for i in range(0,len(sortedList)): 
                size += sortedList[i][1]
                if (size >= neededsize):
                    index = i
                    break
        if (index >-1):
            finalList = []
            if (type == "A"):
                finalList = list(blist) + list(clist) + sortedList[i+1:]
            if (type == "B"):
                finalList = list(alist) + list(clist) + sortedList[i+1:]
            if (type == "C"):
                finalList = list(blist) + list(alist) + sortedList[i+1:]
            Setting.sbs_cache[antennaindex] = finalList
        else:
            print("somthing happend in cleaning chache!!!")        
            return
        # print("remove sbs cach :"+ str(antennaindex))
        # for i,item in enumerate(Setting.sbs_cache[antennaindex]):
        #     print(item)

def cleanCache(antenna, time):
    antennaindex = abs(antenna)
    cleanedList = []
    if (antenna < 0):
        cleanedList = filter(lambda x: x[2] == 'C' or x[5] >= time, Setting.mbs_cache[antennaindex])
        Setting.mbs_cache[antennaindex] = list(cleanedList)
    else:    
        cleanedList = filter(lambda x: x[2] == 'C' or x[5] >= time, Setting.sbs_cache[antennaindex])
        Setting.sbs_cache[antennaindex] = list(cleanedList)

def recalcCachSize(antenna, time):
    antennaindex = abs(antenna)
    anewcachesize = 0
    bnewcachesize = 0
    cnewcachesize = 0
    time = time - 5000

    alist = list(filter(lambda x: x[6] == antenna and x[1] > time and x[4] == "A", Setting.doing_log))
    blist = list(filter(lambda x: x[6] == antenna and x[1] > time and x[4] == "B", Setting.doing_log))
    clist = list(filter(lambda x: x[6] == antenna and x[1] > time and x[4] == "C", Setting.doing_log))
    aaccess = 0
    baccess = 0
    caccess = 0

    afils = []
    bfils = []
    cfils = []
    
    for i in alist : 
        if (not i[3] in afils):
           afils.append(i[3])
           aaccess += i[7]
    for i in blist : 
        if (not i[3] in bfils):
            bfils.append(i[3])
            baccess += i[7]
    for i in clist : 
        if (not i[3] in cfils):
            cfils.append(i[3])
            caccess += i[7]
    
    rate = Setting.file_size / Setting.iot_size

    caccess = caccess*rate
    recentlyacess =  aaccess + baccess + caccess

    apercent = 0
    bpercent = 0
    cpercent = 0

    if (aaccess > 0): apercent = aaccess / recentlyacess 
    if (baccess > 0): bpercent = baccess / recentlyacess 
    if (caccess > 0): cpercent = caccess / recentlyacess 

    if (antenna < 0 ):
        cachsize = Setting.mbs_cache_size[antennaindex][0]
    if (antenna >= 0):
        cachsize = Setting.sbs_cache_size[antennaindex][0]

    amincachesize = cachsize % Setting.file_size
    cmincachesize = Setting.file_size

    remindcachsize =  cachsize - (amincachesize + cmincachesize)
    if (remindcachsize == 0):
        return
    acachesize = math.ceil(((apercent * remindcachsize) / 100) / Setting.file_size) * Setting.file_size
    ccachesize = remindcachsize - acachesize


    anewcachesize = amincachesize + acachesize
    bnewcachesize = 0
    cnewcachesize = cmincachesize + ccachesize

    filledcachsizes = getCacheFilledSize(antenna, "")
    afilledcachesize = filledcachsizes[1]
    bfilledcachesize = filledcachsizes[2]
    cfilledcachesize = filledcachsizes[3]

    if (afilledcachesize > anewcachesize):
        removeCache(antenna, "A", afilledcachesize - anewcachesize )

    # if (bfilledcachesize > bnewcachesize):
    #     removeCache(antenna, "B", bfilledcachesize - bnewcachesize )

    if (cfilledcachesize > cnewcachesize):
        removeCache(antenna, "C", cfilledcachesize - cnewcachesize )

    if (antenna < 0 ):
        Setting.mbs_cache_size[antennaindex][1] = anewcachesize
        Setting.mbs_cache_size[antennaindex][2] = bnewcachesize
        Setting.mbs_cache_size[antennaindex][3] = cnewcachesize
    if (antenna >= 0):
        Setting.sbs_cache_size[antennaindex][1] = anewcachesize
        Setting.sbs_cache_size[antennaindex][2] = bnewcachesize
        Setting.sbs_cache_size[antennaindex][3] = cnewcachesize

def removeCache(antenna, type, neededsize):       

    if ("RATETYPE" in Setting.replacement_strategy):        
        removeRate(antenna, type, neededsize, "RATE")
        return 

    if ("LRUTYPE" in Setting.replacement_strategy):
        removeType(antenna, type, neededsize, "LRU")
        return 
    if ("LFUTYPE" in Setting.replacement_strategy):
        removeType(antenna, type, neededsize, "LFU")
        return 
   
    if ("LFU" in Setting.replacement_strategy ):
        removeMix(antenna, type, neededsize, "LFU")
        return 
    if ("LRU" in Setting.replacement_strategy):
        removeMix(antenna, type, neededsize, "LRU")
        return 
    return 

def getCacheFilledSize(antenna, type):
    antennaindex = abs(antenna)
    if (antenna < 0):
        cache = Setting.mbs_cache[antennaindex]
    else:    
        cache = Setting.sbs_cache[antennaindex]
        
    alist = list(filter(lambda x: x[2] == "A", cache))
    blist = list(filter(lambda x: x[2] == "B", cache))
    clist = list(filter(lambda x: x[2] == "C", cache))
    afilledcachsize = 0
    bfilledcachsize = 0
    cfilledcachsize = 0

    for item in alist: afilledcachsize += item[1]
    for item in blist: bfilledcachsize += item[1]
    for item in clist: cfilledcachsize += item[1]

    if (type == "A"): return afilledcachsize
    if (type == "B"): return bfilledcachsize
    if (type == "C"): return cfilledcachsize
    if (type == "ALL"): return afilledcachsize + bfilledcachsize + cfilledcachsize
    return [afilledcachsize + bfilledcachsize + cfilledcachsize, afilledcachsize, bfilledcachsize, cfilledcachsize]


def getNaighbor(antenna):
    sbss = []
    if antenna == 0: sbss=[1,16]
    elif antenna == 1: sbss=[0]
    elif antenna == 2: sbss=[7,9,17]
    elif antenna == 3: sbss=[4,29,9,10]
    elif antenna == 4: sbss=[3,29,18]
    elif antenna == 5: sbss=[6,24]
    elif antenna == 6: sbss=[5,9]
    elif antenna == 7: sbss=[3,17,14]
    elif antenna == 8: sbss=[]
    elif antenna == 9: sbss=[17,6,2,3]
    elif antenna == 10: sbss=[17,13,29]
    elif antenna == 11: sbss=[13,7,21]
    elif antenna == 12: sbss=[16,20,28]
    elif antenna == 13: sbss=[15,11,17,10]
    elif antenna == 14: sbss=[21,19,7]
    elif antenna == 15: sbss=[13]
    elif antenna == 16: sbss=[12,0,27,23]
    elif antenna == 17: sbss=[7,2,9,10,13]
    elif antenna == 18: sbss=[4]
    elif antenna == 19: sbss=[21,25,14]
    elif antenna == 20: sbss=[12]
    elif antenna == 21: sbss=[19,11,14,25]
    elif antenna == 22: sbss=[26,21]
    elif antenna == 23: sbss=[16]
    elif antenna == 24: sbss=[6,2]
    elif antenna == 25: sbss=[26, 19, 21]
    elif antenna == 26: sbss=[25]
    elif antenna == 27: sbss=[16]
    elif antenna == 28: sbss=[16, 23]
    elif antenna == 29: sbss=[10, 4, 18]
    return sbss

def updateOtherCache(antenna, filename, type, time, size, expiretime):
    if (Setting.update_strategy == "DYNAMIC"):
        if (type == "C"):    
            sbslist = getNaighbor(antenna)
            for sbs in sbslist:
                if (sbs != antenna):
                    checkInCach(sbs,filename, time, type, size, expiretime, False, 0, -100)
            return
        # else:
        #     mbs = find_mbs_antenna(antenna)
        #     sbslist = Setting.antenna_position[mbs]
        #     for sbs in sbslist:
        #         if (sbs != antenna):
        #             checkInCach(sbs,filename, time, type, size, expiretime, False)
        #     return


    if (Setting.update_strategy == "SIBILING"):
        mbs = find_mbs_antenna(antenna)
        sbslist = Setting.antenna_position[mbs]
        for sbs in sbslist:
            if (sbs != antenna):
                checkInCach(sbs,filename, time, type, size, expiretime, False, 0, -100)
        return
    if (Setting.update_strategy == "NAIGHBOR"):
        sbslist = getNaighbor(antenna)
        for sbs in sbslist:
            if (sbs != antenna):
                checkInCach(sbs,filename, time, type, size, expiretime, False, 0, -100)
        return
    return    

def getCashSize(antenna):
    antennaindex = abs(antenna)
    cachsize = 0
    if (antenna < 0 ):
        cachsize = Setting.mbs_cache_size[antennaindex][0] 
        if ("TYPE" in Setting.replacement_strategy):
            if (type == "A"): cachsize = Setting.mbs_cache_size[antennaindex][1]
            if (type == "B"): cachsize = Setting.mbs_cache_size[antennaindex][2]
            if (type == "C"): cachsize = Setting.mbs_cache_size[antennaindex][3]
    if (antenna >= 0):
        cachsize = Setting.sbs_cache_size[antennaindex][0] 
        if ("TYPE" in Setting.replacement_strategy):
            if (type == "A"): cachsize = Setting.sbs_cache_size[antennaindex][1]
            if (type == "B"): cachsize = Setting.sbs_cache_size[antennaindex][2]
            if (type == "C"): cachsize = Setting.sbs_cache_size[antennaindex][3]
    return cachsize

def addInCache(antenna, filename, type, time, size, expiretime, foruse, key):

    antennaindex = abs(antenna)
    #no need to update cache
    if (Setting.cache_strategy == "FULL" or Setting.cache_strategy == "NO"):
        return    
    #no cach

    cachsize = getCashSize(antenna)
    
    if (cachsize < size ):
        return
          
    #implement chach
    filledcachsize = 0
    if ("TYPE" in Setting.replacement_strategy):
        filledcachsize = getCacheFilledSize(antenna, type)
    else:    
        filledcachsize = getCacheFilledSize(antenna, "ALL")

    haseSpaceToAdd = True

    if ((filledcachsize+size) > cachsize):
        if ("DYNAMIC" in  Setting.replacement_strategy):
            recalcCachSize(antenna, time)
            cachsize = getCashSize(antenna)
            if ((filledcachsize+size) > cachsize):
                removeCache(antenna, type, size- (cachsize - filledcachsize) )
        else:                
            removeCache(antenna, type, size- (cachsize - filledcachsize) )

    if ("RATETYPE" in Setting.replacement_strategy):     
        newfilledcachsize = getCacheFilledSize(antenna, type)    
        haseSpaceToAdd = (newfilledcachsize+size) <= cachsize



    waiting = 0
    speed = Setting.mbs_speed if antenna < 0 else Setting.sbs_speed

    if (foruse and size > speed): waiting = 1

    if (haseSpaceToAdd):
        if (antenna < 0):      
            Setting.mbs_cache[antennaindex].append([filename, size, type, time, 1, expiretime+time, waiting])
        else:         
            Setting.sbs_cache[antennaindex].append([filename, size, type, time, 1, expiretime+time, waiting])
            if (foruse == True):
                updateOtherCache(antenna, filename, type, time, size, expiretime)

        if (foruse):
            Setting.service_log.append([antenna, filename, key])

    return

##------------------------------------------------------------------------------------------##
def findServiceIndex(key):
    index = -1
    for i in range(len(Setting.service_log)):
        if (Setting.service_log[i][2] == key):
            index = i
            break

    return index

def findFileNameIndex(cache, fileName):
    index = -1
    for i in range(len(cache)):
        if (fileName == cache[i][0]):
            index = i
            break

    return index


def checkInCach(antenna, fileName, time, type, size, expiretime, foruse, remindsize, key) :
    if (Setting.cache_strategy == "FULL"):
        return True
    if (Setting.cache_strategy == "NO"):
        return False
    if (antenna < 0 and type == "C"):
        return True
    
    cleanCache(antenna, time)
    inCach = False
    antennaindex = abs(antenna)
  
    


    if (antenna >= 0):
        sbs_cache = Setting.sbs_cache[antennaindex]
        for i in range(len(sbs_cache)):
            if (fileName == sbs_cache[i][0]):
                inCach = True
                if (foruse == True):
                    Setting.sbs_cache[antennaindex][i][3] = time
                    Setting.sbs_cache[antennaindex][i][4] += 1

                    if (size == remindsize):
                        Setting.sbs_cache[antennaindex][i][6] += 1
                    else:
                        serviceindex = findServiceIndex(key)
                        
                        if (serviceindex > -1):
                            oldanten = Setting.service_log[serviceindex][0]
                            if (oldanten == antenna):
                                if (remindsize <= Setting.sbs_speed):
                                   Setting.sbs_cache[antennaindex][i][6] -= 1
                            else:
                                if (oldanten < 0):      
                                    j = findFileNameIndex(Setting.mbs_cache[abs(oldanten)], fileName) 
                                    if (j > -1):                              
                                        Setting.mbs_cache[abs(oldanten)][j][6] -= 1
                                else:   
                                    j = findFileNameIndex(Setting.sbs_cache[oldanten], fileName) 
                                    if (j > -1):
                                        Setting.sbs_cache[oldanten][j][6] -= 1
                                
                                if (remindsize > Setting.sbs_speed):
                                   Setting.sbs_cache[antennaindex][i][6] += 1

                        Setting.service_log[serviceindex][0] = antenna           

                break
    else:
        mbs_cache = Setting.mbs_cache[antennaindex]
        for i in range(len(mbs_cache)):
            if (fileName == mbs_cache[i][0]):
                inCach = True
                if (foruse == True):
                    Setting.mbs_cache[antennaindex][i][3] = time
                    Setting.mbs_cache[antennaindex][i][4] += 1


                    if (size == remindsize):
                        Setting.mbs_cache[antennaindex][i][6] += 1
                    else:
                        serviceindex = findServiceIndex(key)
                        
                        if (serviceindex > -1):
                            oldanten = Setting.service_log[serviceindex][0]
                            if (oldanten == antenna):
                                if (remindsize <= Setting.sbs_speed):
                                   Setting.sbs_cache[antennaindex][i][6] -= 1
                            else:
                                if (oldanten < 0):     
                                    j = findFileNameIndex(Setting.mbs_cache[abs(oldanten)], fileName) 
                                    if (j > -1):                                                             
                                        Setting.mbs_cache[abs(oldanten)][j][6] -= 1
                                else:    
                                    j = findFileNameIndex(Setting.sbs_cache[oldanten], fileName) 
                                    if (j > -1):                                                             
                                        Setting.sbs_cache[oldanten][j][6] -= 1
                                
                                if (remindsize > Setting.sbs_speed):
                                   Setting.sbs_cache[antennaindex][i][6] += 1

                                Setting.service_log[serviceindex][0] = antenna


                    if (size == remindsize and remindsize > Setting.mbs_speed):
                        Setting.mbs_cache[antennaindex][i][6] += 1
                    if (remindsize <= Setting.mbs_speed):
                        Setting.mbs_cache[antennaindex][i][6] -= 1
                break
    if (not inCach):
       addInCache(antenna,fileName,type, time, size, expiretime, foruse, key)
    return inCach

##------------------------------------------------------------------------------------------##
def generateSencorData(fileName):
    return 5 #time to generate iot data


def getSencorData(key, antenna, user, reqtime, type, filename, 
                      starttime, expiretime, iotZone):
    
    zonestr = "_"+str(iotZone)
    inCach = checkInCach(iotZone,filename+zonestr, reqtime, type, Setting.iot_size, expiretime, True, Setting.iot_size, key)
    if (not inCach):       
        reqtime += generateSencorData(filename)

    firstemptytime = getStackQueueEmptyTime(user, reqtime, iotZone)   
    if (firstemptytime > -1):
        antennaindex = abs(iotZone)
        if (iotZone<0):          
            Setting.mbs_queue[antennaindex][firstemptytime] = user
        else:    
            Setting.sbs_queue[antennaindex][firstemptytime] = user
        
    return firstemptytime

##------------------------------------------------------------------------------------------##
def processIotRequest(key, antenna, user, reqtime, type, fileName, 
                      startTime, expiretime, iotZone, iotsize):
    zonestr=""
    if iotZone!=0 and iotZone != antenna : zonestr = "_"+str(iotZone)
    expiretime = 500
    inCach = checkInCach(antenna,fileName+zonestr, reqtime, type, iotsize, expiretime, True, iotsize, key)

    senderAntenna = antenna
    if (not inCach):       
        if (iotZone==0):            
            reqtime += generateSencorData(fileName)
            stayingtime = getAntennaStayingTime(user, reqtime, antenna)
        else:            
            reqtime = getSencorData(key, antenna, user, reqtime, type, fileName, 
                        startTime, expiretime, iotZone)            
            antenna = find_mbs_antenna(antenna)
            stayingtime = getAntennaStayingTime(user, reqtime, antenna, True)
            # reqtime = reqtime +1
    else:
        stayingtime = getAntennaStayingTime(user, reqtime, antenna)
    antennaindex = abs(antenna)
    firstemptytime = getStackQueueEmptyTime(user, reqtime, antenna)   

    if (firstemptytime > -1 and firstemptytime <= stayingtime):

       
        if (antenna<0):          
            Setting.mbs_queue[antennaindex][firstemptytime] = user
        else:    
            Setting.sbs_queue[antennaindex][firstemptytime] = user
        Setting.doing_log.append([user,firstemptytime,antenna,fileName, type, inCach, senderAntenna, iotsize, key])
        pop_InProcess(key)
    
        nexttime = firstemptytime+1
        remindsize = iotsize
        if (antenna<0):          
            remindsize -= Setting.mbs_speed
        else:    
            remindsize -= Setting.sbs_speed

        if (remindsize>0):
            push_InProcess(key, user, nexttime, fileName, remindsize, type, expiretime, startTime, iotZone)
        else:
            if (antenna<0):          
                Setting.mbs_antena_log[antennaindex][2] += 1
            else:    
                Setting.sbs_antena_log[antennaindex][2] += 1
            request_Log_Update(key, startTime, firstemptytime, "DONE")    

    else:
        miss_Process(key, antenna, user, reqtime, type, fileName, 1, startTime)

#-------------------------------------------------------------------------------------------------------#
def processMultimediaRequest(key, antenna, user, reqtime, type, fileName, fileSize, startTime, expiretime):
    orginalfileSize = fileSize
    for i in range(len(Setting.request_log)):
        if (Setting.request_log[i][0]==key):
            orginalfileSize=Setting.request_log[i][4]
            break
    inCach = checkInCach(antenna,fileName, reqtime, type, orginalfileSize, expiretime, True, fileSize, key)
    stayingtime = getAntennaStayingTime(user, reqtime, antenna)
    senderAntenna = antenna

    if (not inCach):       
        antenna = find_mbs_antenna(antenna)

    firstemptytime = getStackQueueEmptyTime(user, reqtime, antenna)   

    antennaindex = abs(antenna)
    nexttime = reqtime     
    remindsize = fileSize

    if (firstemptytime > -1 and firstemptytime <= stayingtime):
        nexttime = firstemptytime
        if (antenna<0):          
            Setting.mbs_queue[antennaindex][firstemptytime] = user
            remindsize -= Setting.mbs_speed
        else:    
            Setting.sbs_queue[antennaindex][firstemptytime] = user
            remindsize -= Setting.sbs_speed

        Setting.doing_log.append([user,firstemptytime,antenna,fileName, type, inCach, senderAntenna, orginalfileSize, key ])

    else:
        nexttime = stayingtime

    nexttime += 1
    pop_InProcess(key)

    if (remindsize>0):
        push_InProcess(key, user, nexttime, fileName, remindsize, type, expiretime, startTime, 0)
    else:
        if (antenna<0):          
            Setting.mbs_antena_log[antennaindex][2] += 1
        else:    
            Setting.sbs_antena_log[antennaindex][2] += 1
        request_Log_Update(key, startTime, firstemptytime, "DONE")    
##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
def ProcessRequest(req):      
    key = int(req[0])
    user = int(req[1])
    reqtime = (req[2])
    fileName = req[3]
    fileSize = req[4]
    type = req[5]
    expireTime = int(req[6])
    startTime = int(req[7])
    intreqtime = int(reqtime)
    antenna = Setting.mu_bs[user][intreqtime]

    if reqtime > Setting.sim_time:
        miss_Process(key, antenna, user, reqtime, type, fileName, fileSize, startTime)
        return
    if ((type == "A") | (type == "B")):
        iotZone = int(req[8])
        processIotRequest(key, antenna, user, reqtime, type, fileName, startTime, expireTime, iotZone, fileSize)
    else:
        processMultimediaRequest(key, antenna, user, reqtime, type, fileName, fileSize, startTime, expireTime)

##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
def Run_InProcess():   
    while (len(Setting.inprocessreqs) > 0):      
       if (len(Setting.inprocessreqs) > 0):
            req = Setting.inprocessreqs[0]
            ProcessRequest(req)

##------------------------------------------------------------------------------------------##
def Fill_InProcessQueue():   
    
    for i, req in enumerate(Data.allreqs):
        reqtime = float(req[0])
        if (reqtime > Setting.sim_time) :
            break

        fileName = str(req[1])
        user = int(req[2]) - 1  
        type = req[3]
        expireTime = req[4]
        if (type == "A" or type == "B"):
            fileSize = Setting.iot_size

        if (type == "C"):
            if (Setting.file_size == 0):
                fileSize = int(req[5])
            else:    
                fileSize = Setting.file_size

        iotZone = 0
        if (len(req)>6):
            iotZone = int(req[6])
        antenna =  Setting.mu_bs[user][int(reqtime)]
        if (antenna<0):          
            Setting.mbs_antena_log[abs(antenna)][0] = Setting.mbs_antena_log[abs(antenna)][0]+1
            Setting.mbs_antena_log[abs(antenna)][1] = Setting.mbs_antena_log[abs(antenna)][1]+fileSize
        else:    
            Setting.sbs_antena_log[antenna][0] = Setting.sbs_antena_log[antenna][0]+1
            Setting.sbs_antena_log[antenna][1] = Setting.sbs_antena_log[antenna][1]+fileSize
        push_InProcess_Init(i, user, reqtime, fileName, fileSize, type, expireTime, reqtime, iotZone)
        request_Log_Add(i, user, type, fileName, fileSize, reqtime)

    Setting.hangOn[0] = False


def takeSecond(elem):
    return elem[0]
##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
##------------------------------------------------------------------------------------------##
def run():
    Fill_InProcessQueue()
    Run_InProcess()

def simulate(tag, cachestrategy, prioritystrategy, replacementstrategy, updatestrategy):
    Setting.priority_strategy = prioritystrategy
    Setting.cache_strategy = cachestrategy
    Setting.replacement_strategy = replacementstrategy
    Setting.update_strategy = updatestrategy


    Setting.mbs_queue = [[]*(Setting.sim_time+1)]*(Setting.mbs_antenna_count+1)
    Setting.sbs_queue = [[]*(Setting.sim_time+1)]*(Setting.sbs_antenna_count+1)
    Setting.mbs_cache = [[]]*(Setting.mbs_antenna_count+1)
    Setting.sbs_cache = [[]]*(Setting.sbs_antenna_count+1)

    Setting.mbs_antena_log = [[]*len(Setting.antenna_log_data_field)]*(Setting.mbs_antenna_count+1)
    Setting.sbs_antena_log = [[]*len(Setting.antenna_log_data_field)]*(Setting.sbs_antenna_count+1)
    Setting.summary_user_log = []

    Setting.summary_reqtype_log = []

    Setting.request_log = []

    Setting.doing_log = []
    Setting.missing_log = []
    Setting.inprocessreqs = []
    Setting.hangOn = [True]
    Setting.expend_time_reqs = []


    print("=====================")
    print("Cachestrategy : ", cachestrategy+" Prioritystrategy:"+prioritystrategy +" Replacementstrategy:"+replacementstrategy+" Updatestrategy:"+updatestrategy)

    Setting.mbs_queue = [[-1 for i in range(Setting.sim_time+1)] for j in range(Setting.mbs_antenna_count+1)]
    Setting.sbs_queue = [[-1 for i in range(Setting.sim_time+1)] for j in range(Setting.sbs_antenna_count+1)]

    Setting.mbs_antena_log = [[0 for i in range(len(Setting.antenna_log_data_field))] for j in range(Setting.mbs_antenna_count+1)]
    Setting.sbs_antena_log = [[0 for i in range(len(Setting.antenna_log_data_field))] for j in range(Setting.sbs_antenna_count+1)]

    for i in range(len(Setting.req_type)):
        row = [0 for j in range(len(Setting.summary_reqtype_log_data_field))]
        row[0] = Setting.req_type[i]
        Setting.summary_reqtype_log.append(row)

    Data.allreqs.sort(key=takeSecond)

    totalcachsize = (Setting.cache_a_count * Setting.iot_size) + (Setting.cache_c_count * Setting.file_size)

    Setting.mbs_cache_size = [[totalcachsize, (Setting.cache_a_count * Setting.iot_size) ,0, (Setting.cache_c_count * Setting.file_size)] for j in range(Setting.mbs_antenna_count+1)]
    Setting.sbs_cache_size = [[totalcachsize, (Setting.cache_a_count * Setting.iot_size) ,0, (Setting.cache_c_count * Setting.file_size)] for j in range(Setting.sbs_antenna_count+1)]

    run()
    
    #request_log_data_field = ["key", "user", "type", "fileName", "fileSize", "reqtime", "starttime", "endtime", "status"]
    for i, req in enumerate(Setting.request_log):
        don = 0
        mis=0
        if (req[8] == 'DONE'):
            don = 1
        if (req[8] == 'MISS'):
            mis = 1
        summary_User_Log_Update(req[1],req[4], don, mis, req[6], req[7])
        sz = 1
        if (Setting.file_size == 0):
            sz = req[4]

        summary_ReqType_Log_Update(req[2],req[4], don, mis, ((int(req[7])-int(req[5]))+1) / sz)

    for i in range(len(Setting.summary_reqtype_log)):
        if (Setting.summary_reqtype_log[i][3] > 0):
            Setting.summary_reqtype_log[i][6] = (Setting.summary_reqtype_log[i][5] / Setting.summary_reqtype_log[i][3])*0.01

    f = open("result/"+str(tag)+"_"+cachestrategy+"_"+prioritystrategy+"_"+replacementstrategy+"_"+updatestrategy+".txt", "x")

    f.write("Simulate Time : "+ str(Setting.sim_time))
    f.write("\n")
    f.write("mbs Anteta Cache Size :" + str(Setting.mbs_cache_size))
    f.write("\n")
    f.write("mbs Anteta Count :" + str(Setting.mbs_antenna_count))
    f.write("\n")
    f.write("sbs Anteta Count :"+ str(Setting.sbs_antenna_count))
    f.write("\n")
    f.write("sbs Anteta Cache Size :"+ str(Setting.sbs_cache_size))
    f.write("\n")

    # f.write("===== mbs =======")
    # f.write("mbs queue : ", Setting.mbs_queue)
    # for i in range(0,len(Setting.mbs_queue)):
    #     f.write(i,"  :", Setting.mbs_queue[i])
    # f.write("===== sbd =======")
    # f.write("sbs queue : ", Setting.sbs_queue)
    # for i in range(0,len(Setting.sbs_queue)):
    #     f.write(i,"  :", Setting.sbs_queue[i])

    sbsmissreq = 0
    mbsmissreq = 0
    sbsdonereq = 0
    mbsdonereq = 0
    sbssizereq = 0
    mbssizereq = 0

    f.write("===== Antenna Log =======")
    f.write("\n")
    f.write("SBS     Count   Size   Done   Miss ")
    f.write("\n")
    for i,antennalog in enumerate(Setting.sbs_antena_log):
        sbsmissreq += Setting.sbs_antena_log[i][3]
        sbsdonereq += Setting.sbs_antena_log[i][2]
        sbssizereq += Setting.sbs_antena_log[i][1]
        f.write("sbs " +str(i)+"   "+str( antennalog[0])+"   "+str( antennalog[1])+"   "+str(antennalog[2])+"   "+str(antennalog[3]))
        f.write("\n")

    f.write("================================")
    f.write("\n")
    f.write("MBS     Count   Size   Done   Miss ")
    f.write("\n")
    for i in range(0,len(Setting.mbs_antena_log)):
        mbsmissreq += Setting.mbs_antena_log[i][3]
        mbsdonereq += Setting.mbs_antena_log[i][2]
        mbssizereq += Setting.mbs_antena_log[i][1]
        f.write("mbs "+str(i) + "   "+str( Setting.mbs_antena_log[i][0])+"   "+ str(Setting.mbs_antena_log[i][1])+"   "+str(Setting.mbs_antena_log[i][2])+"   "+str(Setting.mbs_antena_log[i][3]))
        f.write("\n")

    f.write("===== Done Req =======")
    f.write("\n")
    f.write("sbs = "+str(sbsdonereq))
    f.write("\n")
    f.write("mbs = "+str(mbsdonereq))
    f.write("\n")
    f.write("all done req = "+str(sbsdonereq+mbsdonereq))
    f.write("\n")
    f.write("===== Miss Req =======")
    f.write("\n")
    f.write("sbs = "+str( sbsmissreq))
    f.write("\n")
    f.write("mbs = "+str(mbsmissreq))
    f.write("\n")
    f.write("all miss req = "+str( sbsmissreq+mbsmissreq))
    f.write("\n")
    f.write("===== Size Req =======")
    f.write("\n")
    f.write("sbs = "+str( sbssizereq))
    f.write("\n")
    f.write("mbs = "+str( mbssizereq))
    f.write("\n")
    f.write("all size req = "+str( sbssizereq+mbssizereq))
    f.write("\n")
    f.write("===== Request Log =======")
    f.write("\n")
    f.write(str(Setting.request_log))
    f.write("\n")
    f.write("===== Request Type Summary Log =======")
    f.write("\n")
    f.write(str(Setting.summary_reqtype_log))
    f.write("\n")
    f.write("===== User Summary Log =======")
    f.write("\n")
    f.write(str(Setting.summary_user_log))
    f.write("\n")
    new_list = sorted(Setting.doing_log, key=lambda x: x[1])
    f.write("===== Doing  Log =======")
    f.write("\n")
    f.write(str(new_list))
    f.write("\n")
    f.write("===== Missing Log =======")
    f.write("\n")
    f.write(str(Setting.missing_log))
    f.write("\n")
    f.write(str(Setting.summary_reqtype_log))
    f.write("\n")
    f.write("===== finished =======")
    f.write("\n")
    f.close()

    print(str(Setting.summary_reqtype_log))
    print("===== finished =======")

