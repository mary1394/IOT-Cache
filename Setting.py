
#---------------------------------------------------------------------------------------------#
## Configs ##
#---------------------------------------------------------------------------------------------#
sim_time = 85000

mbs_antenna_count = 6
mbs_speed = 1

sbs_antenna_count = 30
sbs_speed = 10

file_size = 100
iot_size = 10
cache_size_percent = 0.1

#--v9
cache_a_count =20
cache_c_count = 20

user_speed = 1

main_q_l_cache = 100
pend_q_l_cache = 100
threshhold_l_cache = 100
min_l_cache = 100


#mbs_cache_size = 10
#sbs_cache_size = 100
#---------------------------------------------------------------------------------------------#
req_type = ["A","B","C"]
antenna_position = [[-1],
           [-1],
           [4,18],
           [5,6],
           [2,3,7,9,10,11,13,21,14,15,29,17],           
           [0,1,12,16,20,23,24,28],
           [8,22,26,27,25,19]
           ]

#---------------------------------------------------------------------------------------------#
## Internal variable ##
## ------------------------------------------------------------------------------------------##
priority_strategy = "NO" #NO,TYPE,TYPESIZE
cache_strategy = "NO" #FULL,NO,DYNAMIC
replacement_strategy = ""
update_strategy = ""

mu_bs = []

mbs_queue = [[]*(sim_time+1)]*(mbs_antenna_count+1)
sbs_queue = [[]*(sim_time+1)]*(sbs_antenna_count+1)

antenna_cach_field = ["FileName", "FileSize", "Type", "LastAccessTime", "AccessCount", "ExpireTime", "WatingCount"]
mbs_cache = [[]]*(mbs_antenna_count+1)
sbs_cache = [[]]*(sbs_antenna_count+1)

antenna_cach_size = ["Size", "ASize", "BSize", "CSize"]
mbs_cache_size = []
sbs_cache_size = []

antenna_log_data_field = ["TaskCount", "TaskSize", "TaskDone", "TaskMiss"]
mbs_antena_log = [[]*len(antenna_log_data_field)]*(mbs_antenna_count+1)
sbs_antena_log = [[]*len(antenna_log_data_field)]*(sbs_antenna_count+1)

summary_user_log_data_field = ["User","RequestCount", "RequestSize", "RequestDone", "RequestMiss", "ResponseTime"]
summary_user_log = []

summary_reqtype_log_data_field = ["RequestType", "RequestCount", "RequestSize", "RequestDone", "RequestMiss", "ResponseTime", "AvgResponseTime"]
summary_reqtype_log = []

request_log_data_field = ["key", "user", "type", "fileName", "fileSize", "reqtime", "starttime", "endtime", "status"]
request_log = []


doing_log_data_field = ["user","Reqtime","antenna","fileName", "type", "incache", "senderAntenna", "size", "key"]
doing_log = []


service_log_field = ["antenna", "fileName", "key"]
service_log = []

missing_log_data_field = ["user","Reqtime","FileName", "RemindSize", "type"]
missing_log = []

inprocessreqs = []
hangOn = [True]
expend_time_reqs = []

## ------------------------------------------------------------------------------------------##
## LCACHE
## ------------------------------------------------------------------------------------------##
#pending_queue[accesscount, filename, size, expiretime], main_queue[accesscount, filename, size, expiretime], main_pointer
mbs_l_cache = [[],[],0]*(mbs_antenna_count+1)
sbs_l_cache = [[],[],0]*(sbs_antenna_count+1)






