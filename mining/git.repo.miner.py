
'''
Akond Rahman 
Nov 19, 2020 
Mine Git-based repos 
'''

'''
====================
Forensics Logging SQA Project 4.b
====================
This file was updated to include forensics logging in key methods. The logging captures:
    - Status of the operation (success, failure, etc.)
    - Application context (initiator, target system/component)
    - Timestamp with timezone (using pytz, default UTC)
    - Error details on failure

The logging uses Python's built-in logging module, configured for INFO level and timestamps with timezone.
Look for log lines prefixed with [Forensics] in the logs for forensic/audit purposes.

Methods updated for forensics logging:
    - deleteRepo
    - cloneRepo
    - cloneRepos
    - getMLStats
    - getMLLibraryUsage
    - deleteRepos
'''



import pandas as pd 
import csv 
import subprocess
import numpy as np
import shutil
from git import Repo
from git import exc 
from xml.dom import minidom
from xml.parsers.expat import ExpatError
import time 
import datetime 
import os 
import logging
import pytz

# Forensics logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z',
)
tz = pytz.timezone('UTC')  # Change as needed for your distributed environment

def deleteRepo(dirName, type_):
    print(':::' + type_ + ':::Deleting ', dirName)
    initiator = 'deleteRepo'  # Example context
    target = dirName
    try:
        if os.path.exists(dirName):
            shutil.rmtree(dirName)
            status = 'success'
        else:
            status = 'not_found'
        logging.info(f"[Forensics] status={status} initiator={initiator} target={target} type={type_} tz={tz.zone}")
    except OSError as e:
        status = 'failure'
        logging.error(f"[Forensics] status={status} initiator={initiator} target={target} type={type_} tz={tz.zone} error={e}")


def makeChunks(the_list, size_):
    for i in range(0, len(the_list), size_):
        yield the_list[i:i+size_]

def cloneRepo(repo_name, target_dir):
    cmd_ = "git clone " + repo_name + " " + target_dir 
    initiator = 'cloneRepo'
    target = repo_name
    try:
        subprocess.check_output(['bash','-c', cmd_])    
        status = 'success'
        logging.info(f"[Forensics] status={status} initiator={initiator} target={target} target_dir={target_dir} tz={tz.zone}")
    except subprocess.CalledProcessError as e:
        status = 'failure'
        logging.error(f"[Forensics] status={status} initiator={initiator} target={target} target_dir={target_dir} tz={tz.zone} error={e}")

def dumpContentIntoFile(strP, fileP):
    fileToWrite = open( fileP, 'w')
    fileToWrite.write(strP )
    fileToWrite.close()
    return str(os.stat(fileP).st_size)

def getPythonCount(path2dir): 
    usageCount = 0
    for root_, dirnames, filenames in os.walk(path2dir):
        for file_ in filenames:
            full_path_file = os.path.join(root_, file_) 
            if (file_.endswith('py') ):
                usageCount +=  1 
    return usageCount                         


def cloneRepos(repo_list): 
    counter = 0     
    str_ = ''
    initiator = 'cloneRepos'
    for repo_batch in repo_list:
        for repo_ in repo_batch:
            counter += 1 
            print('Cloning ', repo_ )
            dirName = '/Users/arahman/FSE2021_ML_REPOS/GITHUB_REPOS/' + repo_.split('/')[-2] + '@' + repo_.split('/')[-1] 
            try:
                cloneRepo(repo_, dirName )
                all_fil_cnt = sum([len(files) for r_, d_, files in os.walk(dirName)])
                if (all_fil_cnt <= 0):
                    deleteRepo(dirName, 'NO_FILES')
                    status = 'deleted_no_files'
                else: 
                    py_file_count = getPythonCount( dirName  )
                    prop_py = float(py_file_count) / float(all_fil_cnt)
                    if(prop_py < 0.25):
                        deleteRepo(dirName, 'LOW_PYTHON_' + str( round(prop_py, 5) ) )
                        status = 'deleted_low_python'
                    else:
                        status = 'cloned'
                logging.info(f"[Forensics] status={status} initiator={initiator} target={repo_} dirName={dirName} tz={tz.zone}")
            except Exception as e:
                status = 'failure'
                logging.error(f"[Forensics] status={status} initiator={initiator} target={repo_} dirName={dirName} tz={tz.zone} error={e}")

def getMLStats(repo_path):
    repo_statLs = []
    repo_count  = 0 
    all_repos = [f.path for f in os.scandir(repo_path) if f.is_dir()]
    print('REPO_COUNT:', len(all_repos) ) 
    initiator = 'getMLStats'
    logging.info(f"[Forensics] status=start initiator={initiator} target={repo_path} repo_count={len(all_repos)} tz={tz.zone}")
    for repo_ in all_repos:
        repo_count += 1 
        try:
            ml_lib_cnt = getMLLibraryUsage( repo_ ) 
            repo_statLs.append( (repo_, ml_lib_cnt ) )
            status = 'success'
            logging.info(f"[Forensics] status={status} initiator={initiator} target={repo_} ml_lib_cnt={ml_lib_cnt} tz={tz.zone}")
        except Exception as e:
            status = 'failure'
            logging.error(f"[Forensics] status={status} initiator={initiator} target={repo_} tz={tz.zone} error={e}")
    return repo_statLs 


def getMLLibraryUsage(path2dir): 
    usageCount  = 0 
    initiator = 'getMLLibraryUsage'
    try:
        for root_, dirnames, filenames in os.walk(path2dir):
            for file_ in filenames:
                full_path_file = os.path.join(root_, file_) 
                if(os.path.exists(full_path_file)):
                    if (file_.endswith('py'))  :
                        f = open(full_path_file, 'r', encoding='latin-1')
                        fileContent  = f.read()
                        fileContent  = fileContent.split('\n') 
                        fileContents = [z_.lower() for z_ in fileContent if z_!='\n' ]
                        for fileContent in fileContents:
                            if('sklearn' in fileContent) or ('keras' in fileContent) or ('gym.' in fileContent) or ('pyqlearning' in fileContent) or ('tensorflow' in fileContent) or ('torch' in fileContent):
                                    usageCount = usageCount + 1
                            elif('rl_coach' in fileContent) or ('tensorforce' in fileContent) or ('stable_baselines' in fileContent) or ('tf.' in fileContent) :
                                    usageCount = usageCount + 1
        status = 'success'
        logging.info(f"[Forensics] status={status} initiator={initiator} target={path2dir} usageCount={usageCount} tz={tz.zone}")
    except Exception as e:
        status = 'failure'
        logging.error(f"[Forensics] status={status} initiator={initiator} target={path2dir} tz={tz.zone} error={e}")
    return usageCount      


def deleteRepos():
    initiator = 'deleteRepos'
    try:
        repos_df = pd.read_csv('DELETE_CANDIDATES_GITHUB_V2.csv')
        repos    = np.unique( repos_df['REPO'].tolist() ) 
        for x_ in repos:
            deleteRepo( x_, 'ML_LIBRARY_THRESHOLD' )
        status = 'success'
        logging.info(f"[Forensics] status={status} initiator={initiator} target=DELETE_CANDIDATES_GITHUB_V2.csv tz={tz.zone}")
    except Exception as e:
        status = 'failure'
        logging.error(f"[Forensics] status={status} initiator={initiator} target=DELETE_CANDIDATES_GITHUB_V2.csv tz={tz.zone} error={e}")

if __name__=='__main__':
    # repos_df = pd.read_csv('PARTIAL_REMAINING_GITHUB.csv')
    # list_    = repos_df['URL'].tolist()
    # list_    = np.unique(list_)
    # # print('Repos to download:', len(list_)) 
    # ## need to create chunks as too many repos 
    # chunked_list = list(makeChunks(list_, 100))  ### list of lists, at each batch download 100 repos 
    # cloneRepos(chunked_list)



    '''
    some utils  

    deleteRepos()     

    di_ = '/Users/arahman/FSE2021_ML_REPOS/GITHUB_REPOS/'
    ls_ = getMLStats(  di_  )
    df_ = pd.DataFrame( ls_ )
    df_.to_csv('LIB_BREAKDOWN_GITHUB_BATCH2.csv', header=['REPO', 'LIB_COUNT'] , index=False, encoding='utf-8')              
    '''


