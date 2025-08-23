import EMRR
import EMLCache
import uuid
import Setting
import pickle

with open("content/mu_bs_pickle", "rb") as mu_loc_object:
    all_mu_bs = pickle.load(mu_loc_object)

#===========================================================================#
tag =  uuid.uuid4()

if (Setting.user_speed > 1):
    for x in all_mu_bs:
        newx = []
        for i in range(0, len(x), Setting.user_speed):
            newx.append(x[i])    
        Setting.mu_bs.append(newx)
else:    
    Setting.mu_bs = all_mu_bs


#===========================================================================#
#cachestrategy, prioritystrategy, replacementstrategy, updatestrategy

# EMRR.simulate(tag, "DYNAMIC","NO","LFUTYPEDYNAMIC", "SIBLING" )
# EMRR.simulate(tag, "DYNAMIC","TYPESIZE","LFUTYPEDYNAMIC", "SIBLING" )
    
# 
# EMRR.simulate(tag, "NO", "NO", "", "" )
# EMRR.simulate(tag, "DYNAMIC","NO","LFU", "" )
# EMRR.simulate(tag, "DYNAMIC","NO","LRU", "" )
# EMRR.simulate(tag, "DYNAMIC","TYPESIZE","LRU", "" )
EMRR.simulate(tag, "DYNAMIC","NO","LFU", "" )


# EMRR.simulate(tag, "DYNAMIC","TYPESIZE","RATETYPE", "" )
# EMRR.simulate(tag, "DYNAMIC","TYPESIZE","RATETYPE", "NAIGHBOR" )
# EMRR.simulate(tag, "DYNAMIC","TYPESIZE","RATETYPE", "SIBLING" )
# EMRR.simulate(tag, "DYNAMIC","TYPESIZE","RATETYPE", "DYNAMIC" )



# EMRR.simulate(tag, "DYNAMIC","TYPESIZE","LFUTYPEDYNAMIC", "" )
# EMRR.simulate(tag, "DYNAMIC","TYPESIZE","LRUTYPEDYNAMIC", "" )


# EMLCache.simulate(tag)









# EMRR.simulate(tag, "DYNAMIC","TYPESIZE","RATETYPE", "NAIGHBOR" )
# EMRR.simulate(tag, "DYNAMIC","TYPESIZE","LFUTYPEDYNAMIC", "NAIGHBOR" )
# EMRR.simulate(tag, "DYNAMIC","TYPESIZE","LRUTYPEDYNAMIC", "NAIGHBOR" )


# 


# EMRR.simulate(tag, "DYNAMIC","TYPESIZE","RATETYPE", "" )

# EMRR.simulate(tag, "FULL","NO","LFUTYPEDYNAMIC", "SIBLING" )
# EMLCache.simulate(tag)

#EMRR.simulate(tag, "DYNAMIC","NO","LRU", "" )
#EMRR.simulate(tag, "DYNAMIC","TYPE","LRUTYPE", "" )
#EMRR.simulate(tag, "DYNAMIC","TYPESIZE","LRUTYPE", "" )
#EMRR.simulate(tag, "DYNAMIC","NO","LRUTYPE", "NAIGHBOR" )
#EMRR.simulate(tag, "DYNAMIC","TYPESIZE","LRUTYPEDYNAMIC", "DYNAMIC" )
#EMRR.simulate(tag, "DYNAMIC","NO","LRUTYPEDYNAMIC", "NAIGHBOR" )
#EMRR.simulate(tag, "DYNAMIC","NO","LFU", "" )
#EMRR.simulate(tag, "NO","NO","LRU", "" ) 
# EMRR.simulate(tag, "FULL","TYPESIZE","LRU", "" )
#EMRR.simulate(tag, "DYNAMIC","NO","LFU", "" ) 
# EMRR.simulate(tag, "DYNAMIC","TYPESIZE","LFU", "" ) 
# EMRR.simulate(tag, "DYNAMIC","NO","LRU", "" ) 
# EMRR.simulate(tag, "No","TYPESIZE","LFU", "" ) 
# EMRR.simulate(tag, "DYNAMIC","NO","LRU", "" ) 

#EMRR.simulate(tag, "NO", "NO", "", "" )
# EMRR.simulate(tag, "DYNAMIC","NO","LFU", "" )
# EMRR.simulate(tag, "DYNAMIC","NO","LFUTYPE", "" )
#EMRR.simulate(tag, "DYNAMIC","NO","LRUTYPE", "" )
#EMRR.simulate(tag, "DYNAMIC","NO","LRUTYPEDYNAMIC", "" )

#EMRR.simulate(tag, "FULL","NO","LRU", "" )



