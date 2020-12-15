# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 17:36:27 2020

@author: Federico
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math
import sys
from sys import getsizeof
from datetime import datetime
import os, psutil
import time
import memory_profiler as mem_profile
from time import process_time

mode=None

# Import the date 
now = datetime.now()                      # actual date
now = now.strftime("%d/%m/%Y %H:%M:%S")   # Y=year, m=month, d=day, H=hour, M=minute, S=second   
now = str(now)                            # convert the date to a string

##### Number of edges
print('Insert number of edges to import. For example 5000. ')
edges_number=int(input())

print("""Select operator
[1]: Neighbor Match      
[2]: Common Neighbor Match 
""")

operator=int(input())

if operator ==1:
    #### Depth of walk
    print("""
    Insert depth of the walk.
    For example:
    depth=1      a->b     
    depth=2      a->b->c
    depth=3      a->b->c->d
      
    Minimum depth=1
    Maximum depth=11
    """)
    
    depth=int(input())

# Import Pocek graph
graph = pd.read_csv('soc-pokec-relationships.txt/soc-pokec-relationships.txt', sep="\t",nrows=edges_number, header=None)
graph = graph.rename(columns={0: "Source", 1: "Destination"})

max_number_nodes= max(graph['Source'])

if operator==1:
    #### Starting node
    print("""Insert the starting node.
    Nodes are between 1 and """+str(max_number_nodes)+ """, according to the selected edges     
    """)
    
    starting_node=int(input())

    ### Method
    print("""Select the method to use for the queries:
    [1]: HASH Table
    [2]: CSR
    [3]: Both
    """)
        
    mode=int(input())


if mode==1 or mode==3 or operator==2:
    
    # Build of the tables
    row_len=5
    row = math.ceil(max_number_nodes/row_len)
    
    destination_hash=np.zeros((row,row_len))
    destination_hash = pd.DataFrame(destination_hash)
    
    #source_hash=np.zeros((row, row_len))
    #source_hash = pd.DataFrame(source_hash)
    
    # Transform cell into object
    for i in range(0,row_len):
        destination_hash[i]=destination_hash[i].astype('object')
        #source_hash[i]=source_hash[i].astype('object')
    
    #### Reset index from 1  #######################
        
    #destination table: rows
    destination_hash.index=destination_hash.index+1
    #source table: rows
    #source_hash.index=source_hash.index+1
    
    #destination table: columns
    headers=range(1,row_len+1)
    destination_hash.columns=headers
    
    #source table: columns
    #headers=range(1,row_len+1)
    #source_hash.columns=headers
    
    for i in range(1,max_number_nodes+1):
        row_id=math.ceil(i/row_len)
        col_id=i-(row_id-1)*row_len
        list_i= graph.loc[(graph['Source'] ==i)]['Destination'] 
        list_i=list(list_i)
        destination_hash.at[row_id,col_id]=list_i    
    
    hash_size=(getsizeof(destination_hash))/1000
    
    #for i in range(1,max_number_nodes+1):
    #    row_id=math.ceil(i/row_len)
    #    col_id=i-(row_id-1)*row_len
    #    list_i= graph.loc[(graph['Destination'] ==i)]['Source'] 
    #    list_i=list(list_i)
    #    source_hash.at[row_id,col_id]=list_i
    
    
    def neighbors_hash(hash_destination, node):
        row_len= len(hash_destination.columns)
        row_id=math.ceil(node/row_len)
        col_id=node-(row_id-1)*row_len
        neighbors=hash_destination.at[row_id,col_id]
        number=len(neighbors)
        return(neighbors, number)

#if operator ==2:
#    print("Insert first vertex (highest node: "+str(max_number_nodes) +")")
#    vert1= int(input())
#    
#    print("Insert second vertex (highest node: "+str(max_number_nodes) +")")
#    vert2= int(input())
#
#    def intersection(lst1, lst2): 
#        lst3 = [value for value in lst1 if value in lst2] 
#        return lst3 
#
#    neig_vert1_hash= neighbors_hash(destination_hash, vert1)[0]
#    neig_vert2_hash= neighbors_hash(destination_hash, vert2)[0]
#
#    common=intersection(neig_vert1_hash,neig_vert2_hash)
#    
#    if len(common)>=1:
#        print("There are vertices in common between " +str(vert1) +" and "+str(vert2))
#        print("Common vertices")
#        print(common)
#    else:
#        print("No vertices in common")
#
#

if mode ==2 or mode ==3 or operator==2:
        
    source_list=list(graph['Source'])
    idx=list(graph['Destination'])
    ptr=[0]
    
    for i in range(1, max_number_nodes+1):
        if i in source_list:
            index_i=graph[graph['Source'] == i].index[0]
            ptr.append(index_i)
        if i not in source_list:
            next_value=next(val for val in range(i,max_number_nodes+1) if val in source_list) 
            index_i=graph[graph['Source'] == next_value].index[0]
            ptr.append(index_i)            
            
    def neighbors_csr(ptr,idx,node):
        start=ptr[node]
        end=ptr[node+1]
        neighbors=idx[start:end]
        number=len(neighbors)
        return(neighbors, number)
    
    idx_size=getsizeof(idx)
    ptr_size=getsizeof(ptr)
    csr_size=(idx_size+ptr_size)/1000

another=1

if operator ==2:
    print("Insert first vertex (highest node: "+str(max_number_nodes) +")")
    vert1= int(input())
    
    print("Insert second vertex (highest node: "+str(max_number_nodes) +")")
    vert2= int(input())
    
    print()

    def intersection(lst1, lst2): 
        lst3 = [value for value in lst1 if value in lst2] 
        return lst3 

    neig_vert1_hash= neighbors_hash(destination_hash, vert1)[0]
    neig_vert2_hash= neighbors_hash(destination_hash, vert2)[0]

    common_hash=intersection(neig_vert1_hash,neig_vert2_hash)
    print("Results using the HASH table")
    if len(common_hash)>=1:
        
        print("There are vertices in common between " +str(vert1) +" and "+str(vert2))
        print("Common vertices")
        print(common_hash)
    else:
        print("No vertices in common")
        
    neig_vert1_csr= neighbors_csr(ptr,idx,vert1)[0]
    neig_vert2_csr= neighbors_csr(ptr,idx,vert2)[0]
   
    common_csr=intersection(neig_vert1_csr,neig_vert2_csr)
    
    print("Results using the CSR")
    if len(common_csr)>=1:
        
        print("There are vertices in common between " +str(vert1) +" and "+str(vert2))
        print("Common vertices")
        print(common_csr)
    else:
        print("No vertices in common")


while another==1: 
    
    if mode==1 or mode==3:
        
        distance=' '*5
        hash_memory_before=mem_profile.memory_usage()[0]
        
#        a=psutil.virtual_memory()
#        hash_memory_before=a[3]/1000000       
#                    
        f= open("Hash.txt","w+")
        f.write('The selected starting node is ' +str(starting_node))
        f.write('\n')
        f.write('Depth: '+str(depth))
        
        neig_1=neighbors_hash(destination_hash,starting_node)[0]
        neig_1_number=neighbors_hash(destination_hash,starting_node)[0]
        f.write('\n')
        start_hash1=process_time()
        if depth>=1:    
            for i1 in neig_1:
                if depth==1:
                    f.write(str(starting_node) + distance + str(i1))
                    f.write('\n')                
                if depth>1:
                    if i1<max_number_nodes:
                        neig_2=neighbors_hash(destination_hash,i1)[0]            
                        for i2 in neig_2:            
                            if depth==2: 
                                if i2 != starting_node:
                                    f.write(str(starting_node) + distance + str(i1)+distance+ str(i2))
                                    f.write('\n')                
                            if depth>2:
                                if i2<max_number_nodes and i2 != starting_node:
                                    neig_3=neighbors_hash(destination_hash,i2)[0] 
                                    for i3 in neig_3:
                                        if depth==3: 
                                            if i3 not in [starting_node, i1]:
                                                f.write(str(starting_node) + distance + str(i1) + distance + str(i2) + distance +str(i3))
                                                f.write('\n')
                                        if depth>3:
                                            if i3<max_number_nodes and i3 not in [starting_node, i1]:
                                                neig_4=neighbors_hash(destination_hash,i3)[0] 
                                                for i4 in neig_4:
                                                    if depth==4: 
                                                        if i4 not in [starting_node,i1,i2]:
                                                            f.write(str(starting_node) + distance + str(i1) + distance + str(i2) + distance + str(i3) + distance+str(i4))
                                                            f.write('\n')
                                                    if depth>4:
                                                        if i4<max_number_nodes and i4 not in [starting_node,i1,i2]:
                                                            neig_5=neighbors_hash(destination_hash,i4)[0] 
                                                            for i5 in neig_5:
                                                                if depth==5:
                                                                    if i5 not in [starting_node,i1,i2,i3]:
                                                                        f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5))
                                                                        f.write('\n')
                                                                if depth>5:
                                                                    if i5<max_number_nodes and i5 not in [starting_node,i1,i2,i3]:
                                                                        neig_6=neighbors_hash(destination_hash,i5)[0]
                                                                        for i6 in neig_6:
                                                                            if depth==6:
                                                                                if i6 not in [starting_node,i1,i2,i3,i4]:
                                                                                    f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5)+distance+str(i6))
                                                                                    f.write('\n')
                                                                            if depth>6:
                                                                                if i6<max_number_nodes and i6 not in [starting_node,i1,i2,i3,i4]:
                                                                                    neig_7=neighbors_hash(destination_hash,i6)[0]
                                                                                    for i7 in neig_7:
                                                                                        if depth==7:
                                                                                            if i7 not in [starting_node,i1,i2,i3,i4,i5]:
                                                                                                f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5)+distance+str(i6)+distance+str(i7))
                                                                                                f.write('\n')
                                                                                        if depth>7:
                                                                                            if i7<max_number_nodes and i7 not in [starting_node,i1,i2,i3,i4,i5]:
                                                                                                neig_8=neighbors_hash(destination_hash,i7)[0]
                                                                                                for i8 in neig_8:
                                                                                                    if depth == 8:
                                                                                                        if i8 not in [starting_node,i1,i2,i3,i4,i5,i6]:                                                                                                    
                                                                                                            f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5)+distance+str(i6)+distance+str(i7)+distance+str(i8))
                                                                                                            f.write('\n')
                                                                                                    if depth>8:
                                                                                                        if i8<max_number_nodes and i8 not in [starting_node,i1,i2,i3,i4,i5,i6]:
                                                                                                            neig_9=neighbors_hash(destination_hash,i8)[0]
                                                                                                            for i9 in neig_9:
                                                                                                                 if depth == 9:
                                                                                                                     if i9 not in [starting_node,i1,i2,i3,i4,i5,i6,i7]:
                                                                                                                        f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5)+distance+str(i6)+distance+str(i7)+distance+str(i8)+distance+str(i9))
                                                                                                                        f.write('\n')
                                                                                                                 if depth>9:                                                                                                                                                                                                                                                                                           
                                                                                                                     if i9<max_number_nodes and i9 not in [starting_node,i1,i2,i3,i4,i5,i6,i7]:
                                                                                                                         neig_10=neighbors_hash(destination_hash,i9)[0]
                                                                                                                         for i10 in neig_10:
                                                                                                                             if depth ==10:
                                                                                                                                 if i10 not in [starting_node,i1,i2,i3,i4,i5,i6,i7,i8]:
                                                                                                                                     f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5)+distance+str(i6)+distance+str(i7)+distance+str(i8)+distance+str(i9)+distance+str(i10))
                                                                                                                                     f.write('\n')
                                                                                                                             if depth>10:
                                                                                                                                 if i10<max_number_nodes and i10 not in [starting_node,i1,i2,i3,i4,i5,i6,i7,i8]:
                                                                                                                                     neig_11=neighbors_hash(destination_hash,i10)[0]
                                                                                                                                     for i11 in neig_11:
                                                                                                                                         if depth==11:
                                                                                                                                             if i11 not in [starting_node,i1,i2,i3,i4,i5,i6,i7,i8,i9]:
                                                                                                                                                 f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5)+distance+str(i6)+distance+str(i7)+distance+str(i8)+distance+str(i9)+distance+str(i10)+distance+str(i11))
                                                                                                                                                 f.write('\n')
#        b=psutil.virtual_memory()
#        hash_memory_after=b[3]/1000000
#        hash_usage=hash_memory_after-hash_memory_before
#
#        hash_memory=(mem_profile.memory_usage()[0]-hash_memory_before)*1000                                                   
        hash_final=process_time()-start_hash1                                                                                
        f.close()
                
        new_line=pd.DataFrame({"Date": [now], "Edges": [str(edges_number)],"Depth": [str(depth)], "Starting node": [str(starting_node)], "Method": ['HASH'], "Time [s]": [str(hash_final)], "Size table/vectors [kB]" :[str(hash_size)]})  
            
        if  os.path.isfile('Queries Archive.xlsx'):
            archive=pd.read_excel('Queries Archive.xlsx', header=0)     
            archive=pd.concat([ archive,new_line], ignore_index=True)  
        if not os.path.isfile('Queries Archive.xlsx'):
            archive=new_line
        
        archive.to_excel("Queries Archive.xlsx",index=False)  
               
    if mode ==2 or mode ==3:
        
        distance=' '*5
        csr_memory_before=mem_profile.memory_usage()[0]
        
        c=psutil.virtual_memory()
        csr_memory_before=c[3]/1000000

            
        f= open("CSR.txt","w+")
        f.write('The selected starting node is ' +str(starting_node))
        f.write('\n')
        f.write('Depth: '+str(depth))
        neig_1=neighbors_csr(ptr,idx,starting_node)[0]
        neig_1_number=neighbors_csr(ptr,idx,starting_node)[0]
        
        f.write('\n')
#        start_csr=time.clock()
        start_csr1=process_time()
        if depth>=1:    
            for i1 in neig_1:
                if depth==1:
                    f.write(str(starting_node) + distance + str(i1))
                    f.write('\n')                
                if depth>1:
                    if i1<max_number_nodes:
                        neig_2=neighbors_csr(ptr,idx,i1)[0]            
                        for i2 in neig_2:            
                            if depth==2: 
                                if i2 != starting_node:
                                    f.write(str(starting_node) + distance + str(i1)+distance+ str(i2))
                                    f.write('\n')                
                            if depth>2:
                                if i2<max_number_nodes and i2 != starting_node:
                                    neig_3=neighbors_csr(ptr,idx,i2)[0] 
                                    for i3 in neig_3:
                                        if depth==3: 
                                            if i3 not in [starting_node, i1]:
                                                f.write(str(starting_node) + distance + str(i1) + distance + str(i2) + distance +str(i3))
                                                f.write('\n')
                                        if depth>3:
                                            if i3<max_number_nodes and i3 not in [starting_node, i1]:
                                                neig_4=neighbors_csr(ptr,idx,i3)[0]                                                 
                                                for i4 in neig_4:
                                                    if depth==4: 
                                                        if i4 not in [starting_node,i1,i2]:
                                                            f.write(str(starting_node) + distance + str(i1) + distance + str(i2) + distance + str(i3) + distance+str(i4))
                                                            f.write('\n')
                                                    if depth>4:
                                                        if i4<max_number_nodes and i4 not in [starting_node,i1,i2]:
                                                            neig_5=neighbors_csr(ptr,idx,i4)[0] 
                                                            for i5 in neig_5:
                                                                if depth==5:
                                                                    if i5 not in [starting_node,i1,i2,i3]:
                                                                        f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5))
                                                                        f.write('\n')
                                                                if depth>5:
                                                                    if i5<max_number_nodes and i5 not in [starting_node,i1,i2,i3]:
                                                                        neig_6=neighbors_csr(ptr,idx,i5)[0]
                                                                        for i6 in neig_6:
                                                                            if depth==6:
                                                                                if i6 not in [starting_node,i1,i2,i3,i4]:
                                                                                    f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5)+distance+str(i6))
                                                                                    f.write('\n')
                                                                            if depth>6:
                                                                                if i6<max_number_nodes and i6 not in [starting_node,i1,i2,i3,i4]:
                                                                                    neig_7=neighbors_csr(ptr,idx,i6)[0]
                                                                                    for i7 in neig_7:
                                                                                        if depth==7:
                                                                                            if i7 not in [starting_node,i1,i2,i3,i4,i5]:
                                                                                                f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5)+distance+str(i6)+distance+str(i7))
                                                                                                f.write('\n')
                                                                                        if depth>7:
                                                                                            if i7<max_number_nodes and i7 not in [starting_node,i1,i2,i3,i4,i5]:
                                                                                                neig_8=neighbors_csr(ptr,idx,i7)[0]
                                                                                                for i8 in neig_8:
                                                                                                    if depth == 8:
                                                                                                        if i8 not in [starting_node,i1,i2,i3,i4,i5,i6]:                                                                                                    
                                                                                                            f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5)+distance+str(i6)+distance+str(i7)+distance+str(i8))
                                                                                                            f.write('\n')
                                                                                                    if depth>8:
                                                                                                        if i8<max_number_nodes and i8 not in [starting_node,i1,i2,i3,i4,i5,i6]:
                                                                                                            neig_9=neighbors_csr(ptr,idx,i8)[0]
                                                                                                            for i9 in neig_9:
                                                                                                                 if depth == 9:
                                                                                                                     if i9 not in [starting_node,i1,i2,i3,i4,i5,i6,i7]:
                                                                                                                        f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5)+distance+str(i6)+distance+str(i7)+distance+str(i8)+distance+str(i9))
                                                                                                                        f.write('\n')
                                                                                                                 if depth>9:                                                                                                                                                                                                                                                                                           
                                                                                                                     if i9<max_number_nodes and i9 not in [starting_node,i1,i2,i3,i4,i5,i6,i7]:
                                                                                                                         neig_10=neighbors_csr(ptr,idx,i9)[0]
                                                                                                                         for i10 in neig_10:
                                                                                                                             if depth ==10:
                                                                                                                                 if i10 not in [starting_node,i1,i2,i3,i4,i5,i6,i7,i8]:
                                                                                                                                     f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5)+distance+str(i6)+distance+str(i7)+distance+str(i8)+distance+str(i9)+distance+str(i10))
                                                                                                                                     f.write('\n')
                                                                                                                             if depth>10:
                                                                                                                                 if i10<max_number_nodes and i10 not in [starting_node,i1,i2,i3,i4,i5,i6,i7,i8]:
                                                                                                                                     neig_11=neighbors_csr(ptr,idx,i10)[0]
                                                                                                                                     for i11 in neig_11:
                                                                                                                                         if depth==11:
                                                                                                                                             if i11 not in [starting_node,i1,i2,i3,i4,i5,i6,i7,i8,i9]:
                                                                                                                                                 f.write(str(starting_node) + distance + str(i1)+distance + str(i2) + distance+str(i3) +distance+str(i4)+distance+str(i5)+distance+str(i6)+distance+str(i7)+distance+str(i8)+distance+str(i9)+distance+str(i10)+distance+str(i11))
                                                                                                                                                 f.write('\n')
#        d=psutil.virtual_memory()
#        csr_memory_after=d[3]/1000000
#        csr_usage=csr_memory_after-csr_memory_before
# 
#
#        csr_memory=(mem_profile.memory_usage()[0]-csr_memory_before)*1000                                                         
    
        csr_final = process_time()-start_csr1
        f.close()
        
        new_line=pd.DataFrame({"Date": [now], "Edges": [str(edges_number)],"Depth": [str(depth)], "Starting node": [str(starting_node)], "Method": ['CSR'], "Time [s]": [str(csr_final)], "Size table/vectors [kB]" :[str(csr_size)]})  
            
        if  os.path.isfile('Queries Archive.xlsx'):
            archive=pd.read_excel('Queries Archive.xlsx', header=0)     
            archive=pd.concat([ archive,new_line], ignore_index=True)  
        if not os.path.isfile('Queries Archive.xlsx'):
            archive=new_line
        
        archive.to_excel("Queries Archive.xlsx",index=False)  
    
    if operator==1:
        print("""Select if you want to perform another query
              [0]:NO
              [1]:YES
              
              """)
        another=int(input())
        #### Depth of walk
        if another==1:
            print("""
            Insert depth of the walk.
            For example:
            depth=1      a->b     
            depth=2      a->b->c
            depth=3      a->b->c->d
              
            Minimum depth=1
            Maximum depth=11
            """)
            
            depth=int(input())
            
  
memory=psutil.virtual_memory()   
percent=memory.percent
print("Percentage memory usage "+str(percent)) 
print('END')
