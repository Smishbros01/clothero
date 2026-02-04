# -*- coding: utf-8 -*-

from flask import Flask, render_template, request,redirect,url_for
from ogenfunctions import Closet
import random
import os

app = Flask(__name__)
closetvar=Closet()

@app.route("/")
#starting page"
def home():
    """POTD is a randomly generated clothing item that will appear whenever the user opens the browser. 
    If POTD is true it will see if we have already generated one for this session and if we have we will display it. 
    If we havent generated a POTD we will loop through all POTD eligible pieces add them to a pool and randomly select one to display.
    This generated piece will be saved until our sesson expires. If there are no clothes just return nothing."""
    POTD=closetvar.preset["POTD"]
    if POTD==True:
        #Check for if we have already generated one for this session
        if not closetvar.preset["preset"]:
            poolofclothes=[]
            sections=closetvar.closet
            for section, pieces in sections.items():
                #Check if our preset settings have ever been altered
                if closetvar.preset["Changed"]==True:
                    #if they have check to see which sections we can select
                    if section not in closetvar.preset["settings"]:
                        continue
                for piece, clothes in pieces.items():
                    for clothe, details in clothes.items():
                        poolofclothes.append((clothe,details,section,piece))
            if closetvar.preset["Changed"]==True:
                #check if favorites have been added to settings
                if "favorites" in closetvar.preset["settings"]:
                    for section, pieces in closetvar.favorites.items():
                        for piece, clothes in pieces.items():
                            for clothe, details in clothes.items():
                                poolofclothes.append((clothe,details,section,piece))
            #randomly generate one
            if poolofclothes:
                            chosenpiece, info, section, piece = random.choice(poolofclothes)
                            closetvar.preset["preset"]=[chosenpiece, info, section, piece]
            #if we have no clothes return none
            else:
                section=""
                piece=""
                chosenpiece=""
                info=[]#
        #display already generated piece
        else:
            #this is done to assure our POTD is always up to date 
            found=False#
            pid=int(closetvar.preset["preset"][0])
            sections=closetvar.closet
            for section, pieces in sections.items():
                for piece, clothes in pieces.items():
                    for clothe, info in clothes.items():
                        if pid==clothe:
                            chosenpiece=pid
                            found=True
                            break
                    if found:   
                        break
                if found:
                    break
            sections=closetvar.laundry
            for section, pieces in sections.items():
                for piece, clothes in pieces.items():
                    for clothe, info in clothes.items():
                        if pid==clothe:
                            chosenpiece=pid
                            found=True
                            break 
                    if found:   
                        break
                if found:
                    break
        
    #if POTD=False return nothing
    else:
        section=""
        piece=""
        chosenpiece=""
        info=[]
    return render_template("home.html",section=section,piece=piece,pid=chosenpiece,traits=info,potd=POTD)

@app.route("/home/<section>/<piece>/favorite-piece/<pid>",methods=["POST"])
#favorite a homepage piece
def hfavpiece(section,piece,pid):
            pid=int(pid)
            #if not in closet check the laundry  
            try:
                closetvar.closet[section][piece][pid][4]=True  
            except:
                closetvar.laundry[section][piece][pid][4]=True  
            #add to favorites
            if section not in closetvar.favorites:
                closetvar.favorites[section] = {}
                closetvar.favcount[section]={}
            if piece not in closetvar.favorites[section]:
                closetvar.favorites[section][piece] = {}
                closetvar.favcount[section][piece]=0
            try:
                closetvar.favorites[section][piece][pid]=closetvar.closet[section][piece][pid]
                closetvar.favcount[section][piece]+=1
            except:
                closetvar.favorites[section][piece][pid]=closetvar.laundry[section][piece][pid]
            closetvar.save()
            return redirect(url_for("home"))
#
@app.route("/home/<section>/<piece>/unfavorite-piece/<pid>",methods=["POST"])
def hunfavpiece(section,piece,pid):
    #unfavorite a homepage piece
    pid=int(pid)
     #if not in closet change the laundry version 
    try:
        closetvar.closet[section][piece][pid][4]=False  
        closetvar.favcount[section][piece]-=1
    except:
        closetvar.laundry[section][piece][pid][4]=False   
    #remove from favorites
    del closetvar.favorites[section][piece][pid]
    if not closetvar.favorites[section][piece]:
                del closetvar.favorites[section][piece]
                del closetvar.favcount[section][piece]
    if not closetvar.favorites[section]:
                del closetvar.favorites[section]
                del closetvar.favcount[section]   
    closetvar.save()
    return redirect(url_for("home"))
    
@app.route("/gen")
def generate():
    #generation starting page
    return render_template("gens.html")

@app.route("/gen/random")
def randoms():
    #shows us all pieces available for generation
    sections=closetvar.closet
    piecescount=closetvar.sectioncount
    return render_template("gensrand.html", sections=sections,count=piecescount)

@app.route("/gen/random/go")
def rango():
    """Get list of selected pieces and randomly generate a piece from each selection"""
    selected = request.args.getlist('sec')
    outfit={}
    for sectionpair in selected:
        #W3Schools for string method understanding
        section, piece=sectionpair.split("-")
        clothes=closetvar.closet[section][piece]
        poolofclothes=[]
        for pid, details in clothes.items():
                    poolofclothes.append((pid,details))
        if poolofclothes:
                        #GeeksforGeeks for random library documentation
                        chosenpiece, info = random.choice(poolofclothes)
                        generated="Section: "+str(section)+", Piece: "+str(piece)
                        outfit[generated]={chosenpiece: info}
                        if info[5]==True:
                            if section not in closetvar.laundry:
                                closetvar.laundry[section] = {}
                            if piece not in closetvar.laundry[section]:
                                closetvar.laundry[section][piece] = {}
                            closetvar.laundry[section][piece][chosenpiece]=info
                            closetvar.sectioncount[section][piece]-=1
                            if info[4]==True:
                                closetvar.favcount[section][piece]-=1
                            del closetvar.closet[section][piece][chosenpiece]
    closetvar.save()
    return render_template("outfit.html", outfit=outfit)

@app.route("/gen/favorites")
def favortes():
    #shows us all pieces available for generation
    sections=closetvar.favorites
    piecescount=closetvar.favcount
    return render_template("favsrand.html", sections=sections,count=piecescount)

@app.route("/gen/favorites/go")
def favgo():
    """Get list of selected pieces and randomly generate a piece from each selection"""
    selected = request.args.getlist('sec')
    outfit={}
    for sectionpair in selected:
        section, piece=sectionpair.split("-")
        clothes=closetvar.closet[section][piece]
        poolofclothes=[]
        for pid, details in clothes.items():
            if details[4]==True:
                    poolofclothes.append((pid,details))
        if poolofclothes:
                        chosenpiece, info = random.choice(poolofclothes)
                        generated="Section: "+str(section)+", Piece: "+str(piece)
                        outfit[generated]={chosenpiece: info}
                        if info[5]==True:
                            if section not in closetvar.laundry:
                                closetvar.laundry[section] = {}
                            if piece not in closetvar.laundry[section]:
                                closetvar.laundry[section][piece] = {}
                            closetvar.laundry[section][piece][chosenpiece]=info
                            closetvar.sectioncount[section][piece]-=1
                            if info[4]==True:
                                closetvar.favcount[section][piece]-=1
                            del closetvar.closet[section][piece][chosenpiece]
    closetvar.save()
    return render_template("outfit.html", outfit=outfit)

@app.route("/gen/color")
def colors():
    #shows us all pieces available for generation
    seccolors={}
    seccolorcount={}
    for section, pieces in closetvar.closet.items():
        secolor=set()
        seccolorcount[section]={}
        for piece, clothes in pieces.items():
            for details in clothes.values():
                secolor.add(details[0])
                if details[0] not in seccolorcount[section]:
                    seccolorcount[section][details[0]]=0
                seccolorcount[section][details[0]]+=1
        seccolors[section]=secolor
    return render_template("genscolors.html", sectioncolors=seccolors, count=seccolorcount)

@app.route("/gen/color/go")
def colgo():
    """Get list of selected pieces and randomly generate a piece from each selection that match criteria"""
    selected = request.args.getlist('color')
    outfit={}
    for sectionpair in selected:
        section,color =sectionpair.split("-")
        pieces=closetvar.closet.get(section,{})
        poolofclothes=[]
        for piece, clothes in pieces.items():
                for clothe, details in clothes.items():
                        if color == details[0]: 
                            poolofclothes.append((clothe,details,section,piece))
        if poolofclothes:
            chosenpiece, info,section,piece= random.choice(poolofclothes)
            generated="Section: "+str(section)+" , Color: "+str(color)
            outfit[generated]={chosenpiece: info}
            if info[5]==True:
                if section not in closetvar.laundry:
                    closetvar.laundry[section] = {}
                if piece not in closetvar.laundry[section]:
                    closetvar.laundry[section][piece] = {}
                closetvar.laundry[section][piece][chosenpiece]=info
                closetvar.sectioncount[section][piece]-=1
                if info[4]==True:
                    closetvar.favcount[section][piece]-=1
                del closetvar.closet[section][piece][chosenpiece]
    closetvar.save()
    return render_template("outfit.html", outfit=outfit)

@app.route("/gen/professionalism")
def prof():
    #shows us all pieces available for generation
    secprofs={}
    secprofcount={}
    for section, pieces in closetvar.closet.items():
        secprof=set()
        secprofcount[section]={}
        for piece, clothes in pieces.items():
            for details in clothes.values():
                secprof.add(details[2])
                if details[2] not in secprofcount[section]:
                    secprofcount[section][details[2]]=0
                secprofcount[section][details[2]]+=1
        secprofs[section]=secprof
    return render_template("gensprofs.html", sectionprof=secprofs, count=secprofcount)

@app.route("/gen/professionalism/go")
def profgo():
    """Get list of selected pieces and randomly generate a piece from each selection that match criteria"""
    selected = request.args.getlist('profs')
    outfit={}
    for sectionpair in selected:
        section,prof =sectionpair.split("-")
        pieces=closetvar.closet.get(section,{})
        poolofclothes=[]
        for piece, clothes in pieces.items():
                for clothe, details in clothes.items():
                        if prof == details[2]: 
                            poolofclothes.append((clothe,details,section,piece))
        if poolofclothes:
            chosenpiece, info,section,piece= random.choice(poolofclothes)
            generated="Section: "+str(section)+" , Rating: "+str(prof)
            outfit[generated]={chosenpiece: info}
            if info[5]==True:
                if section not in closetvar.laundry:
                    closetvar.laundry[section] = {}
                if piece not in closetvar.laundry[section]:
                    closetvar.laundry[section][piece] = {}
                closetvar.laundry[section][piece][chosenpiece]=info
                closetvar.sectioncount[section][piece]-=1
                if info[4]==True:
                    closetvar.favcount[section][piece]-=1
                del closetvar.closet[section][piece][chosenpiece]
    closetvar.save()
    return render_template("outfit.html", outfit=outfit)

@app.route("/gen/material")
def material():
    #shows us all pieces available for generation
    secmaterials={}
    secmatcount={}
    for section, pieces in closetvar.closet.items():
        secmat=set()
        secmatcount[section]={}
        for piece, clothes in pieces.items():
            for details in clothes.values():
                secmat.add(details[1])
                if details[1] not in secmatcount[section]:
                    secmatcount[section][details[1]]=0
                secmatcount[section][details[1]]+=1
        secmaterials[section]=secmat
    return render_template("gensmats.html", sectionmats=secmaterials, count=secmatcount)

@app.route("/gen/material/go")
def matgo():
    """Get list of selected pieces and randomly generate a piece from each selection that match criteria"""
    selected = request.args.getlist('mats')
    outfit={}
    for sectionpair in selected:
        section,mat =sectionpair.split("-")
        pieces=closetvar.closet.get(section,{})
        poolofclothes=[]
        for piece, clothes in pieces.items():
                for clothe, details in clothes.items():
                        if mat == details[1]: 
                            poolofclothes.append((clothe,details,section,piece))
        if poolofclothes:
            chosenpiece, info,section,piece= random.choice(poolofclothes)
            generated="Section: "+str(section)+" , Material: "+str(mat)
            outfit[generated]={chosenpiece: info}
            if info[5]==True:
                if section not in closetvar.laundry:
                    closetvar.laundry[section] = {}
                if piece not in closetvar.laundry[section]:
                    closetvar.laundry[section][piece] = {}
                closetvar.laundry[section][piece][chosenpiece]=info
                closetvar.sectioncount[section][piece]-=1
                if info[4]==True:
                    closetvar.favcount[section][piece]-=1
                del closetvar.closet[section][piece][chosenpiece]
    closetvar.save()
    return render_template("outfit.html", outfit=outfit)

@app.route("/closet")
def closet():
    #show closet sections
    sections=closetvar.closet
    return render_template("closet.html",sections=sections)

@app.route("/closet/add-section",methods=["POST"])
def addsection():
    #add closet section if it is not already there
    nsection=request.form["secname"].strip().lower()
    nsection=nsection.replace("-","")
    if nsection=="":
        nsection=str(closetvar.error)+". Name Error"
        closetvar.error+=1
    if nsection not in closetvar.closet:
        closetvar.closet[nsection]={}
        closetvar.sectioncount[nsection]={}
    closetvar.save()
    return redirect(url_for("closet"))

#Stackoverflow for passing in function parameters
@app.route("/closet/remove-section/<section>",methods=["POST"])
def remsection(section):
    #remove closet section
    if section in closetvar.closet:
        closetvar.trashed[section]=closetvar.closet[section]
        del closetvar.closet[section]
        if section in closetvar.laundry:
            del closetvar.laundry[section]
        if section in closetvar.favorites:
            del closetvar.favorites[section]
        del closetvar.sectioncount[section]
    closetvar.save()
    return redirect(url_for("closet"))

@app.route("/closet/<section>")
def closetsec(section):
    #view pieces of closet section
    pieces=closetvar.closet.get(section,{})
    return render_template("closetsec.html",section=section, pieces=pieces)

@app.route("/closet/favorites")
def closetfaorites():
    #view pieces in favorites
    sections=closetvar.favorites
    return render_template("closetfavorites.html", sections=sections)

@app.route("/closet/<section>/add-piece",methods=["POST"])
def addpiece(section):
    """Add a piece and also make sure it does not contain any - that will mess up future code"""
    npiece=request.form["piecename"].strip().lower()
    color=request.form["color"].strip().lower()
    material=request.form["material"].strip().lower()
    professionalism=request.form["professionalism"].strip().lower()
    npiece=npiece.replace("-","")
    if npiece=="":
        npiece=str(closetvar.error)+". Name Error"
        closetvar.error+=1
    color=color.replace("-","")
    if color=="":
        color=str(closetvar.error)+". Name Error"
        closetvar.error+=1
    material=material.replace("-","")
    if material=="":
        material=str(closetvar.error)+". Name Error"
        closetvar.error+=1
    professionalism=professionalism.replace("-","")
    if professionalism=="":
        professionalism=str(closetvar.error)+". Name Error"
        closetvar.error+=1
    image=request.form["image"]
    canwash=True
    if section in closetvar.nowash["sections"]:
        canwash=False
    elif npiece in closetvar.nowash["pieces"]:
        canwash=False
    closetvar.NewOutfit(section, npiece, color, material, professionalism,image,False,canwash)
    closetvar.save()
    #Stackoverflow for page refreshing
    return redirect(url_for("closetsec", section=section))

@app.route("/closet/<section>/remove-piece/<pid>",methods=["POST"])
def rempiece(section,pid):
    """Remove a piece and also make sure its removed from every instance"""
    pid=int(pid)
    pieces=closetvar.closet.get(section,{})
    piecescount=closetvar.sectioncount.get(section,{})
    for piecen, items in pieces.items():
        if pid in items:
            if section not in closetvar.trashed:
                closetvar.trashed[section]={}
            if piecen not in closetvar.trashed[section]:
                closetvar.trashed[section][piecen]={}
            closetvar.trashed[section][piecen][pid]=closetvar.closet[section][piecen][pid]
            del items[pid] 
            piecescount[piecen]-=1 
            if section in closetvar.favorites:
                if piecen in closetvar.favorites[section]:
                    if pid in closetvar.favorites[section][piecen]:
                        del closetvar.favorites[section][piecen][pid]
                        closetvar.favcount[section][piecen]-=1
                        if not closetvar.favorites[section][piecen]:
                            del closetvar.favorites[section][piecen]
                            del closetvar.favcount[section][piecen]
                if not closetvar.favorites[section]:
                     del closetvar.favorites[section]
                     del closetvar.favcount[section]
            if not items:
                del pieces[piecen]
                del piecescount[piecen]
                if piecen in closetvar.nowash["pieces"]:
                    closetvar.nowash["pieces"].remove(piecen)      
            break
    if pid in closetvar.preset["preset"]:
        closetvar.preset["preset"]={}    
    closetvar.save()
    return redirect(url_for("closetsec", section=section))

@app.route("/closet/<section>/favorite-piece/<pid>",methods=["POST"])
def favpiece(section,pid):
    """Favorite a piece"""
    pid=int(pid)
    pieces=closetvar.closet.get(section,{})
    for piecen, items in pieces.items():
        if pid in items:
            items[pid][4]=True  
            if section not in closetvar.favorites:
                closetvar.favorites[section] = {}
                closetvar.favcount[section]={}
            if piecen not in closetvar.favorites[section]:
                closetvar.favorites[section][piecen] = {}
                closetvar.favcount[section][piecen]=0
            closetvar.favorites[section][piecen][pid]=items[pid]
            break     
    closetvar.favcount[section][piecen]+=1
    closetvar.save()
    return redirect(url_for("closetsec", section=section))

@app.route("/closet/<section>/unfavorite-piece/<pid>",methods=["GET","POST"])
def unfavpiece(section,pid):
    """Unfavorite a piece"""
    pid=int(pid)
    pieces=closetvar.closet.get(section,{})
    for piecen, items in pieces.items():
        if pid in items:
            items[pid][4]=False  
            del closetvar.favorites[section][piecen][pid]
            closetvar.favcount[section][piecen]-=1
            if not closetvar.favorites[section][piecen]:
                del closetvar.favorites[section][piecen]
                del closetvar.favcount[section][piecen]
            if not closetvar.favorites[section]:
                del closetvar.favorites[section]
                del closetvar.favcount[section]
            break
        elif section in closetvar.laundry:
            if piecen in closetvar.laundry[section]:
                    if pid in closetvar.laundry[section][piecen]:
                        closetvar.favorites[section][piecen][pid][4]=False
                        del closetvar.favorites[section][piecen][pid]
                        if not closetvar.favorites[section][piecen]:
                            del closetvar.favorites[section][piecen]
                            del closetvar.favcount[section][piecen]
                        if not closetvar.favorites[section]:
                            del closetvar.favorites[section]
                            del closetvar.favcount[section]     
                        break
    closetvar.save()
    if request.method=="POST":
        return redirect(url_for("closetsec", section=section))
    if request.method=="GET":
        sections=closetvar.favorites
        return redirect(url_for("closetfaorites", sections=sections))

@app.route("/laundry")
def laundry():
    #view all laundry sections
    sections=closetvar.laundry
    return render_template("laundry.html",sections=sections)

@app.route("/laundry/clean-all",methods=["POST"])
def cleanall():
    """Clean all pieces of laundry and reinstate them into the wearble pool"""
    for section,pieces in closetvar.laundry.items():
        for piecen, items in pieces.items():
            for pid in items:
                if section not in closetvar.closet:
                    closetvar.closet[section]={}
                if piecen not in closetvar.closet[section]:
                    closetvar.closet[section][piecen]={}
                closetvar.closet[section][piecen][pid]=items[pid]
                closetvar.sectioncount[section][piecen]+=1
                if items[pid][4]==True:
                    closetvar.favcount[section][piecen]+=1
    closetvar.laundry={}
    sections=closetvar.laundry
    closetvar.save()
    return render_template("laundry.html",sections=sections)

@app.route("/laundry/<section>")
def laundrysec(section):
    """View laundry section"""
    pieces=closetvar.laundry.get(section,{})
    return render_template("laundrysec.html",section=section, pieces=pieces)

@app.route("/laundry/<section>/clean-piece/<pid>",methods=["POST"])
def cleanpiece(section,pid):
    """Clean aspecific piece and make sure it is reinstated into the wearble pool"""
    pid=int(pid)
    pieces=closetvar.laundry.get(section,{})
    for piecen, items in pieces.items():
        if pid in items:
            if piecen not in closetvar.closet[section]:
                closetvar.closet[section][piecen]={}
            closetvar.closet[section][piecen][pid]=items[pid]
            closetvar.sectioncount[section][piecen]+=1
            if items[pid][4]==True:
                closetvar.favcount[section][piecen]+=1
            del items[pid]
            if not items:
                del pieces[piecen]
            break
    closetvar.save()
    return redirect(url_for("laundrysec", section=section))

@app.route("/laundry/<section>/clean-all",methods=["POST"])
def cleansecall(section):
    """Clean all pieces of laundry in section and reinstate them into the wearble pool"""
    pieces=closetvar.laundry.get(section,{})
    for piecen, items in pieces.items():
        for pid in items:
            closetvar.closet[section][piecen][pid]=items[pid]
            closetvar.sectioncount[section][piecen]+=1
            if items[pid][4]==True:
                closetvar.favcount[section][piecen]+=1
    del closetvar.laundry[section] 
    sections=closetvar.laundry
    closetvar.save()
    return render_template("laundry.html",sections=sections)
        
    closetvar.save()
    return redirect(url_for("laundrysec", section=section))

@app.route("/search")
def search():
    #bring up search template
    return render_template("search.html")

@app.route("/results", methods=["POST"])
def results():
    """Get all typed inputs. If an input is not empty and does not match 
    anything within whatever category we skip to the next loop iteration. 
    If input is empty we just continue to the next search category."""
    sectionsearch = request.form["section"].strip().lower()
    piecesearch = request.form["piece"].strip().lower()
    pidsearch = request.form["pid"].strip()
    colorsearch = request.form["color"].strip().lower()
    matsearch = request.form["material"].strip().lower()
    profsearch = request.form["professionalism"].strip().lower()
    selected = request.form.get("selected","")
    results = {}
    if not selected:
        selected=="random"
    if selected=="Favorited":
        for section, pieces in closetvar.favorites.items():
            if sectionsearch and sectionsearch not in section.lower():
                continue
            for piecen, items in pieces.items():
                if piecesearch and piecesearch not in piecen.lower():
                    continue
                for pid, traits in items.items():
                    if pidsearch and pidsearch != str(pid):
                        continue
                    if colorsearch and colorsearch not in traits[0].lower():
                        continue
                    if matsearch and matsearch not in traits[1].lower():
                        continue
                    if profsearch and profsearch not in traits[2].lower():
                        continue
                    if section not in results:
                        results[section] = {}
                    if piecen not in results[section]:
                        results[section][piecen] = {}
                    results[section][piecen][pid]=items[pid]     
    else:
        for section, pieces in closetvar.closet.items():
            if sectionsearch and sectionsearch not in section.lower():
                continue
            for piecen, items in pieces.items():
                if piecesearch and piecesearch not in piecen.lower():
                    continue
                for pid, traits in items.items():
                    if pidsearch and pidsearch != str(pid):
                        continue
                    if colorsearch and colorsearch not in traits[0].lower():
                        continue
                    if matsearch and matsearch not in traits[1].lower():
                        continue
                    if profsearch and profsearch not in traits[2].lower():
                        continue
                    if section not in results:
                        results[section] = {}
                    if piecen not in results[section]:
                        results[section][piecen] = {}
                    results[section][piecen][pid]=items[pid]      
            if selected=="Dirty":
               for section, pieces in closetvar.laundry.items():
                   if sectionsearch and sectionsearch not in section.lower():
                       continue
                   for piecen, items in pieces.items():
                       if piecesearch and piecesearch not in piecen.lower():
                           continue
                       for pid, traits in items.items():
                           if pidsearch and pidsearch != str(pid):
                               continue
                           if colorsearch and colorsearch not in traits[0].lower():
                               continue
                           if matsearch and matsearch not in traits[1].lower():
                               continue
                           if profsearch and profsearch not in traits[2].lower():
                               continue
                           if section not in results:
                               results[section] = {}
                           if piecen not in results[section]:
                               results[section][piecen] = {}
                           results[section][piecen][pid]=items[pid]       
    return render_template("results.html", sections=results)

@app.route("/settings")
def settings():
    #brings us to the available settings
    return render_template("settings.html")

@app.route("/settings/reset")
def settingchange():
    #Resets entire closet
    closetvar.reset()
    closetvar.save()
    return redirect(url_for("settings"))

@app.route("/settings/edit")
def edit():
    #shows us all available editable sections
    sections=closetvar.closet
    return render_template("edit.html",sections=sections)

@app.route("/settings/edit/<section>",methods=["GET","POST"])
def editsec(section):
    #if post we will edit the section to its new name and move everything over to it
    if request.method=="POST":
        if section  in closetvar.closet:
            newsecname = request.form["section"].strip().lower()
            closetvar.closet[newsecname]=closetvar.closet[section]
            if section in closetvar.laundry:
                closetvar.laundry[newsecname]=closetvar.laundry[section]
                del closetvar.laundry[section]
            if section in closetvar.favorites:
                closetvar.favorites[newsecname]=closetvar.favorites[section]
                closetvar.favcount[newsecname]=closetvar.favcount[section]
                del closetvar.favorites[section]
                del closetvar.favcount[section]
            if section in closetvar.preset["settings"]:
                closetvar.preset["settings"].append(newsecname)
                closetvar.preset["settings"].remove(section)
            if section in closetvar.nowash["sections"]:
                closetvar.nowash["sections"].append(newsecname)
                closetvar.nowash["sections"].remove(section)
            closetvar.sectioncount[newsecname]=closetvar.sectioncount[section]
            del closetvar.closet[section]
            del closetvar.sectioncount[section]
        closetvar.save()
        return redirect(url_for("edit"))
    #if get we just view the pieces in the section
    if request.method=="GET":
        pieces=closetvar.closet.get(section,{})
        return render_template("editsec.html",section=section, pieces=pieces)
   
@app.route("/settings/edit/<section>/<piece>/view")
def vieweditpiece(section,piece):
        #go to items in "pieces"
        items=closetvar.closet[section].get(piece,{})
        return render_template("editpiece.html",section=section, piece=piece, items=items)
    
@app.route("/settings/edit/<section>/<piece>",methods=["POST"])
def editpiece(section,piece):
        #edit a piece name and move everything over
        if piece in closetvar.closet[section]:
            newpiecename = request.form["piece"].strip().lower()
            closetvar.closet[section][newpiecename]=closetvar.closet[section][piece]
            del closetvar.closet[section][piece]
            if section in closetvar.laundry:
                if piece in closetvar.laundry[section]:
                    closetvar.laundry[section][newpiecename]=closetvar.laundry[section][piece]
                    del closetvar.laundry[section][piece]
            if section in closetvar.favorites:
                if piece in closetvar.favorites[section]:
                    closetvar.favorites[section][newpiecename]=closetvar.favorites[section][piece]
                    closetvar.favcount[section][newpiecename]=closetvar.favcount[section][piece]
                    del closetvar.favcount[section][piece]
                    del closetvar.favorites[section][piece]
            if piece in closetvar.nowash["pieces"]:
                closetvar.nowash["pieces"].append(newpiecename)
                closetvar.nowash["pieces"].remove(piece)
            closetvar.sectioncount[section][newpiecename]=closetvar.sectioncount[section][piece]
            del closetvar.sectioncount[section][piece]
        closetvar.save()
        return redirect(url_for("editsec",section=section))
    
@app.route("/settings/edit/<section>/<piece>/<pid>",methods=["POST"])
def editpid(section,piece,pid):
            #edit a specific item, can change anything about it
            pid=int(pid)
            npiece=request.form["piecename"].strip().lower()
            color=request.form["color"].strip().lower()
            material=request.form["material"].strip().lower()
            professionalism=request.form["professionalism"].strip().lower()
            image=request.form["image"]
            if not npiece:
                npiece=piece
            if not color:
                color=closetvar.closet[section][piece][pid][0]
            if not material:
                material=closetvar.closet[section][piece][pid][1]
            if not professionalism:
                professionalism=closetvar.closet[section][piece][pid][2]
            if not image:
                image=closetvar.closet[section][piece][pid][3]
            elif not os.path.exists(os.path.join("static", "clothes", image)):
                image="unknown.jpg"
            favorited=closetvar.closet[section][piece][pid][4]
            canwash=closetvar.closet[section][piece][pid][5]
            if npiece!=piece:
                if npiece not in closetvar.closet[section]:
                    closetvar.closet[section][npiece]={}
                    closetvar.sectioncount[section][npiece]=0
                closetvar.closet[section][npiece][pid]=[color,material,professionalism,image,favorited,canwash]
                closetvar.sectioncount[section][piece]-=1
                closetvar.sectioncount[section][npiece]+=1
                del closetvar.closet[section][piece][pid]
                if not closetvar.closet[section][piece]:
                    del closetvar.closet[section][piece]
                    del closetvar.sectioncount[section][piece]
            else:
                closetvar.closet[section][npiece][pid]=[color,material,professionalism,image,favorited,canwash]
            if favorited==True:
                        if npiece==piece:
                            closetvar.favorites[section][npiece][pid]=[color,material,professionalism,image,favorited]
                        else:
                            if npiece not in closetvar.favorites[section]:
                                closetvar.favorites[section][npiece]={}
                                closetvar.favcount[section][npiece]=0
                            closetvar.favorites[section][npiece][pid]=[color,material,professionalism,image,favorited]
                            closetvar.favcount[section][piece]-=1
                            closetvar.favcount[section][npiece]+=1
                            del closetvar.favorites[section][piece][pid]
                            if not closetvar.favorites[section][piece]:
                                del closetvar.favorites[section][piece]
                                del closetvar.favcount[section][piece]
            closetvar.save()
            return redirect(url_for("vieweditpiece", section=section, piece=npiece))

@app.route("/settings/laundry",methods=["GET","POST"])
def laundrysettings():
    #edit what sections of clothing can be washed
    
    #if get method, just view what sections get immunity to washing and which don't
    if request.method=="GET":
        sections=closetvar.closet
        nowashsec=[]
        washsec=[]
        for section in sections:
            if section in closetvar.nowash["sections"]:
                nowashsec.append(section)
            else:
                washsec.append(section)
        return render_template("laundsetting.html",sections=sections, nowashsec=nowashsec, washsec=washsec)
    
    #if post we change the edit setting to either immune or prone to washing
    if request.method=="POST":
        sectionadd = request.form.get("section","")
        ssection,setting =sectionadd.split("-")
        if setting=="NoWash":
            if ssection in closetvar.closet:
                closetvar.nowash["sections"].append(ssection)
                for pieces, clothes in closetvar.closet[ssection].items():
                    for clothe, details in clothes.items():
                        details[5]=False
        elif setting=="Wash":
            for item in closetvar.nowash["sections"]:
                if ssection==item:
                    closetvar.nowash["sections"].remove(item)
                    break
            for pieces, clothes in closetvar.closet[ssection].items():
                    for clothe, details in clothes.items():
                        details[5]=True
        closetvar.save()
        return redirect(url_for("laundrysettings"))
                
        

@app.route("/settings/laundry/<section>",methods=["GET","POST"])
def laundsec(section):
    #edit what pieces of clothing can be washed
    
    #if get method, just view what pieces get immunity to washing and which don't
    if request.method=="GET":
        pieces=closetvar.closet.get(section,{})
        nowashpiece=[]
        washpiece=[]
        for piece in pieces:
            if piece in closetvar.nowash["pieces"]:
                nowashpiece.append(piece)
            else:
                washpiece.append(piece)
        return render_template("laundsec.html",section=section, pieces=pieces, nowashpiece=nowashpiece, washpiece=washpiece)
    
    #if post we change the edit setting to either immune or prone to washing
    if request.method=="POST":
        pieceadd = request.form.get("piece","")
        ppiece,setting =pieceadd.split("-")
        if setting=="NoWash":
            if ppiece in closetvar.closet[section]:
                closetvar.nowash["pieces"].append(ppiece)
                for clothe, details in closetvar.closet[section][ppiece].items():
                        details[5]=False
                
        elif setting=="Wash":
            for item in closetvar.nowash["pieces"]:
                if ppiece==item:
                    closetvar.nowash["pieces"].remove(item)
                    break
            for clothe, details in closetvar.closet[section][ppiece].items():
                    details[5]=True
        closetvar.save()
        return redirect(url_for("laundsec",section=section))
        
    
@app.route("/settings/laundry/<section>/<piece>",methods=["GET","POST"])
def laundpiece(section,piece):
    #edit what specific piece of clothing can be washed
    
    #if get method, just view what specific pieces get immunity to washing and which don't
    if request.method=="GET":
        clothes=closetvar.closet[section].get(piece,{})
        nowashclothe=[]
        washclothe=[]
        for clothe, details in clothes.items():
            if details[5]==False:
                nowashclothe.append(clothe)
            else:
                washclothe.append(clothe)
        return render_template("laundpiece.html", section=section, piece=piece, clothes=clothes, nowashclothe=nowashclothe, washclothe=washclothe)
    #if post we change the edit setting to either immune or prone to washing
    if request.method=="POST":
        clotheadd = request.form.get("clothe","")
        cclothe,setting =clotheadd.split("-")
        cclothe=int(cclothe)
        if setting=="NoWash":
            if cclothe in closetvar.closet[section][piece]:
                closetvar.closet[section][piece][cclothe][5]=False
        elif setting=="Wash":
            if cclothe in closetvar.closet[section][piece]:
                closetvar.closet[section][piece][cclothe][5]=True
        closetvar.save()
        return redirect(url_for("laundpiece", section=section,piece=piece))
    
@app.route("/settings/potd",methods=["GET","POST"])
def potdsettings():
    #edit the home apges potd
    #
    #just view which sections are in potd
    if request.method=="GET": 
        sections=closetvar.closet
        potdsections=[]
        if closetvar.preset["Changed"]==False:
            for section in sections:
                potdsections.append(section)
        else:
            for section in sections:#
                if section in closetvar.preset["settings"]:
                    potdsections.append(section)
            if "favorites" in closetvar.preset["settings"]:
                potdsections.append("favorites")
        POTD=closetvar.preset["POTD"]
        return render_template("potd.html",sections=sections, favorites="favorites",potd=POTD, potdsections=potdsections)
    
    #change our "changed" to true so home knows that there is now a specific selection of selctions to select from
    #edit potd settings to either include or not include the section in potd generation
    if request.method=="POST":
        closetvar.preset["Changed"]=True
        sectionadd = request.form.get("section","")
        ssection,setting =sectionadd.split("-")
        if setting=="NOPOTD":
            closetvar.preset["POTD"]=False
        elif setting=="YESPOTD":
            closetvar.preset["POTD"]=True
        if setting=="POTD":
                if ssection in closetvar.closet:
                    closetvar.preset["settings"].append(ssection)
                elif ssection=="favorites":
                    closetvar.preset["settings"].append("favorites")
        elif setting=="DONTPOTD":
                if ssection in closetvar.preset["settings"]:
                    closetvar.preset["settings"].remove(ssection)
        closetvar.save()
        return redirect(url_for("potdsettings"))
    
@app.route("/settings/trashed",methods=["GET","POST"])
def trashedsettings():
    
    #view which sections have been reecently deleted
    if request.method=="GET":
        sections=closetvar.trashed
        return render_template("trashed.html", sections=sections)
    
    #readd everything in that section
    if request.method=="POST":
        sectionadd = request.form.get("section","")
        section,piece,pid =sectionadd.split("-")
        pid=int(pid)
        if section not in closetvar.closet:
            closetvar.closet[section]={}
            closetvar.sectioncount[section]={}
        if piece not in closetvar.closet[section]:
            closetvar.closet[section][piece]={}
            closetvar.sectioncount[section][piece]=0
        closetvar.closet[section][piece][pid]=closetvar.trashed[section][piece][pid]
        closetvar.sectioncount[section][piece]+=1
        if closetvar.closet[section][piece][pid][4]==True:
            if section not in closetvar.favorites:
                closetvar.favorites[section] = {}
                closetvar.favcount[section]={}
            if piece not in closetvar.favorites[section]:
                closetvar.favorites[section][piece] = {}
                closetvar.favcount[section][piece]=0
            closetvar.favorites[section][piece][pid]=closetvar.trashed[section][piece][pid]
            closetvar.favcount[section][piece]+=1
        del closetvar.trashed[section][piece][pid]
        if not closetvar.trashed[section][piece]:
            del closetvar.trashed[section][piece]
        if not closetvar.trashed[section]:
            del closetvar.trashed[section]
        closetvar.save()
        return redirect(url_for("trashedsettings"))
        

if __name__ == "__main__":
    app.run(debug=True)