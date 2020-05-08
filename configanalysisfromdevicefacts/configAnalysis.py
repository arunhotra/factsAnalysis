import json
import os
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt


##################################
##config analysis from bigip_device_facts as .json
##have all the device fact files (.json) in the python directory 
################################

##############################################################################

####Returns the LB_METHOD count , roundrobin, leastconn and other

def countLBMethod(reqFileDict):
    rr = 0 
    lc = 0
    other = 0
    for filename in reqFileDict:
        poolsInFile = reqFileDict[filename]
        poolData = poolsInFile['pools']
        for pool in poolData.keys():
            poolValue = poolData[pool]
            lb_method = poolValue['lb_method']
            if 'ROUND' in lb_method.upper() :
                rr = rr+1
            elif 'LEAST' in lb_method.upper() :
                lc = lc+1
            else:
                other = other + 1

    return rr,lc,other

#######################################################################

def getTCPProfileCounts(reqFileDict):
    tcp_base = 0
    tcp_custom = 0
    for filename in reqFileDict:
        vSInFile = reqFileDict[filename]
        vSData = vSInFile['VS']
        for VS in vSData.keys():
            vSValue = vSData[VS]
            profiles = vSValue['profile']
            if len(profiles) != 0:
                for each_profile in profiles:
                    profile_name = each_profile['profile_name']
                    profile_type = each_profile['profile_type']
                    if profile_type == 'PROFILE_TYPE_TCP':
                        if profile_name == '/Common/tcp':
                            tcp_base = tcp_base + 1
                        else:
                            tcp_custom = tcp_custom + 1

    return tcp_base,tcp_custom

###################################################


def getHTTPProfileCounts(reqFileDict):
    http_base = 0
    http_custom = 0
    for filename in reqFileDict:
        vSInFile = reqFileDict[filename]
        vSData = vSInFile['VS']
        for VS in vSData.keys():
            vSValue = vSData[VS]
            profiles = vSValue['profile']
            if len(profiles) != 0:
                for each_profile in profiles:
                    profile_name = each_profile['profile_name']
                    profile_type = each_profile['profile_type']
                    if profile_type == 'PROFILE_TYPE_HTTP':
                        if profile_name == '/Common/http':
                            http_base = http_base + 1
                        else:
                            http_custom = http_custom + 1

    return http_base,http_custom


#######################################################################
def countPersistenceType(reqFileDict):
    source_address_900 = 0 
    source_address_other = 0  
    cookie = 0
    other = 0
    for filename in reqFileDict:
        vSInFile = reqFileDict[filename]
        vSData = vSInFile['VS']
        for VS in vSData.keys():
            vSValue = vSData[VS]
            persistence = vSValue['persistence_profile']
            if len(persistence) != 0:
                for each_persistence_profile in persistence:
                    persistence_profile_name = each_persistence_profile['profile_name']
                    if '900' in persistence_profile_name :
                        source_address_900 = source_address_900 + 1
                    elif 'source' in persistence_profile_name:
                        source_address_other = source_address_other + 1
                    elif 'cookie' in persistence_profile_name:
                        cookie = cookie + 1
                    else:
                        other = other + 1

    return source_address_900,source_address_other,cookie,other
#################################################################################


def countSNATType(reqFileDict):
    no_snat = 0 
    automap = 0  
    snatpool = 0
    for filename in reqFileDict:
        vSInFile = reqFileDict[filename]
        vSData = vSInFile['VS']
        for VS in vSData.keys():
            vSValue = vSData[VS]
            snat = vSValue['snat']
            if snat == 'SNAT_TYPE_SNATPOOL':
                snatpool = snatpool+1
            elif snat == 'SNAT_TYPE_AUTOMAP':
                automap = automap + 1
            else:
                no_snat = no_snat + 1

    return snatpool,automap,no_snat

##########################################################################################

#def countTCPMonitorType(reqFileDict):
#    tcp_base = 0 
#    tcp_custom = 0
#    for filename in reqFileDict:
#        poolsInFile = reqFileDict[filename]
#        poolData = poolsInFile['pools']
#        for pool in poolData.keys():
#            poolValue = poolData[pool]
#            monitorData = poolValue['monitor_instance']
#            for monitor in monitorData:

#            if lb_method == 'LB_METHOD_ROUND_ROBIN':
#                rr = rr+1
#            elif lb_method.startswith('LB_METHOD_LEAST'):
#                lc = lc+1
#            else:
#                other = other + 1

#    return rr,lc,other

##################################################################

def getRequiredPoolData(allPools):
    requiredPoolDict = {}
    for pool in allPools.keys(): 
        necessaryPoolData = {}
        poolValues = allPools[pool]
        necessaryPoolData['lb_method'] = poolValues['lb_method']
        necessaryPoolData['monitor_instance'] = poolValues['monitor_instance']
        requiredPoolDict[pool] = necessaryPoolData
    return requiredPoolDict

######################################################################

def getRequiredVSData(allVS):
    requiredVSDict = {}
    for virtual_server in allVS.keys(): 
        necessaryVSData = {}
        vSValues = allVS[virtual_server]
        necessaryVSData['persistence_profile'] = vSValues['persistence_profile']
        necessaryVSData['profile'] = vSValues['profile']
        necessaryVSData['snat'] = vSValues['snat_type']
        requiredVSDict[virtual_server] = necessaryVSData
    return requiredVSDict

########################################################################

def getReqFileData():
    reqFileDict = {}

    for filename in os.listdir(os.getcwd()):
        reqFileData = {}
        if filename.endswith(".json") : 
            reqFileData = {}
            with open(filename) as config:
                configJSON = json.load(config)

            try:
                allVS = configJSON['virtual_server']
            except:
                continue

            try:
                allPools = configJSON['pool']
            except:
                continue

            requiredPoolDict = getRequiredPoolData(allPools)
            requiredVSDict = getRequiredVSData(allVS)
            reqFileData['pools'] = requiredPoolDict
            reqFileData['VS'] = requiredVSDict

            reqFileDict[filename] = reqFileData

    return reqFileDict
##################################################




#########################################

reqFileDict = getReqFileData()

rr,lc,otherLB = countLBMethod(reqFileDict)
source_addr_900, source_addr_other, cookie, otherPer = countPersistenceType(reqFileDict)
snatpool,automap,no_snat = countSNATType(reqFileDict)
tcp_base_profile,tcp_custom_profile = getTCPProfileCounts(reqFileDict)
http_base_profile,http_custom_profile = getHTTPProfileCounts(reqFileDict)
#countTCPMonitorType(reqFileDict)


#countMonitorType(reqFileDict)

####################################

#########Plotting data############

snat_array = [snatpool,automap,no_snat]
LB_array = [rr,lc,otherLB]
per_array = [source_addr_900, source_addr_other, cookie, otherPer]
SNAT_objects = ['snatpool', 'automap', 'no snat']
LB_objects = ['round robin', 'least connections', 'other']
per_objects = ['source_addr_900', 'source_addr_other', 'cookie', 'otherPer']
y_pos_snat = np.arange(len(SNAT_objects))
y_pos_LB = np.arange(len(LB_objects))
y_pos_per = np.arange(len(per_objects))
base_profiles_array = [tcp_base_profile, http_base_profile]
custom_profiles_array = [tcp_custom_profile,http_custom_profile]
###########################################
#Plotting Profiles
###########################################

# data to plot
n_groups = 2
 
# create plot
fig, ax = plt.subplots()
index = np.arange(n_groups)
bar_width = 0.35
opacity = 0.8
 
rects1 = plt.bar(index, base_profiles_array, bar_width,
                 alpha=opacity,
                 color='b',
                 label='base profile')
 
rects2 = plt.bar(index + bar_width, custom_profiles_array, bar_width,
                 alpha=opacity,
                 color='g',
                 label='custom profile')
 
plt.xlabel('Profile Comparison')
plt.ylabel('Count')
#plt.title('Scores by person')
plt.xticks(index + bar_width, ('TCP Profiles', 'HTTP Profiles'))
plt.legend()
 
plt.tight_layout()



#########Plotting persistence#########

# plt.bar(y_pos_per, per_array, align='center', alpha=0.5)
# plt.xticks(y_pos_per, per_objects)
# plt.ylabel('Count')
# plt.xlabel('Persistence type')

####Plotting Snat Objects########

#def plotBarGraph():
#    y_pos_snat = np.arange(len(SNAT_objects))
#    plt.bar(y_pos_snat, snat_array, align='center', alpha=0.5)
#    plt.xticks(y_pos_snat, SNAT_objects)
#    plt.ylabel('Count')
# #    plt.xlabel('Snat type')


# #plt.subplot(2,1,1)
# plt.bar(y_pos_snat, snat_array, align='center', alpha=0.5)
# plt.xticks(y_pos_snat, SNAT_objects)
# plt.ylabel('Count')
# plt.xlabel('Snat type')
# #plt.title('object comparisons')



###Plotting LB Methods########

# #plt.subplot(2,1,2)
# plt.bar(y_pos_LB, LB_array, align='center', alpha=0.5)
# plt.xticks(y_pos_LB, LB_objects)
# plt.ylabel('Count')
# plt.xlabel('LB type')
plt.show()



print('test')

