#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pickle
import os

class Closet:
    def __init__(self, filename="closet.pkl"):
        self.filename=filename
        self.load()
            
    def NewOutfit(self,section,piece,color,material,professionalism,image,favorited=False,canwash=True):
        #add piece to our closet
       if piece not in self.closet[section]:
           self.closet[section][piece]={}
           self.sectioncount[section][piece]=0
       if not image:
           image="unknown.jpg"
       #Python Documentation and Stackoverflow for os.path understanding
       elif not os.path.exists(os.path.join("static", "clothes", image)):
           image="unknown.jpg"
       self.closet[section][piece][self.count]=[color,material,professionalism,image,favorited,canwash]
       self.sectioncount[section][piece]+=1
       self.count+=1
       if section in self.preset["settings"]:
           self.preset["settings"][section][piece][self.count]=[color,material,professionalism,image,favorited,canwash]
    #GeeksforGeeks for saving/loading to pkl
    def save(self):
        #save the file
        with open(self.filename, "wb") as file:
            pickle.dump((self.closet,self.favorites,self.count, self.laundry,self.sectioncount,self.favcount, self.nowash, self.preset),file)
    def load(self):
        #load the file
        if os.path.exists(self.filename):
            with open(self.filename, "rb") as file:
                self.closet, self.favorites,self.count,self.laundry,self.sectioncount,self.favcount, self.nowash, self.preset=pickle.load(file)
            self.preset["preset"]=[]
            self.trashed={}
            self.error=1
        else:
            self.closet={}
            self.favorites={}
            self.count=0
            self.laundry={}
            self.sectioncount={}
            self.favcount={}
            self.preset={"settings":[],"preset":[], "POTD":True, "Changed":False}
            self.nowash={"sections":[],"pieces":[]}
            self.trashed={}
            self.error=1
            
    def reset(self):
        #reset everything
        self.closet={}
        self.favorites={}
        self.count=0
        self.laundry={}
        self.sectioncount={}
        self.favcount={}
        self.preset={"settings":[],"preset":[], "POTD":True, "Changed":False}
        self.nowash={"sections":[],"pieces":[]}
        self.trashed={}
        self.error=1
        
  
                    
            
