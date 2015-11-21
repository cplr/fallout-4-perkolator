# Fallout 4 Perkolator
# github.com/cplr/fallout-4-perkolator
# Perk details copied from http://fallout.wikia.com/wiki/Fallout_4_perks
#
# Copyright 2015 Danny Patterson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from Tkinter import *
# from ttk import *
import plistlib
import pprint
import os.path

prefsFileName = './CharPrefs.plist'
maxLevel = 150
maxPriority = 11

# model for reading perk data
class Perks:
    def __init__(self):
        self.perks = plistlib.readPlist("./Fallout 4 Perks.plist")
        loadedPrefs = False
        if os.path.isfile(prefsFileName):
            self.perkPrefs = plistlib.readPlist(prefsFileName)
            loadedPrefs = True
        else:
            self.perkPrefs = {'Stats':{'S' : 1, 'P' : 1, 'E' : 1, 'C' : 1, 'I' : 1, 'A' : 1, 'L' : 1}}
        
        self.levelToPerkMap = [[] for i in range(maxLevel)]
        self.nameToPerkRanksMap = {}
        for attr, attrLevels in self.perks.iteritems():
            for attrLevel, perk in enumerate(attrLevels):
                name = perk['Name']
                self.nameToPerkRanksMap[name] = perk['Ranks']
                if not loadedPrefs:
                    self.perkPrefs[name] = {}
                for rankNum, rank in enumerate(self.nameToPerkRanksMap[name]):
                    # desc = rank['Description']
                    if not loadedPrefs:
                        self.perkPrefs[name][str(rankNum)] = {'Priority' : -1, 'Unlocked' : 0}
                    charLevel = int(rank['CharLevel'])
                    self.levelToPerkMap[charLevel-1].append((name, rank, rankNum))
    
    def savePrefs(self):
        plistlib.writePlist(self.perkPrefs, prefsFileName)
                        
    def perksForLevel(self, charLevel):
        # returns [(name, rank, rankNum)]
        return self.levelToPerkMap[charLevel - 1]
    
    def perkRanksForName(self, name):
        return self.nameToPerkRanksMap[name]
        
    def setUnlockPerkAndRank(self, perkName, rankNum, unlockLevel):
        # sets level that a perk was unlocked at
        self.perkPrefs[perkName][str(rankNum)]['Unlocked'] = unlockLevel
        self.savePrefs()
    
    def unlockedPerkAndRank(self, perkName, rank):
        # returns level that a perk is unlocked at. 0 if not chosen yet
        return self.perkPrefs[perkName][str(rank)]['Unlocked']
    
    def allForcedPerks(self):
        # returns [(perkName, int(rankNumStr), level)]
        f = []
        for perkName, rankNums in self.perkPrefs.iteritems():
            if perkName == 'Stats':
                continue
            for rankNumStr, info in rankNums.iteritems():
                level = info['Unlocked']
                if level > 0:
                    f.append((perkName, int(rankNumStr), level))
        # print(f)
        return f
        
    def setPriorityForPerkAndRank(self, perkName, rank, priority):
        # print('setting '+perkName+'('+str(rank+1)+') to '+str(priority))
        self.perkPrefs[perkName][str(rank)]['Priority'] = priority
        self.savePrefs()
    
    def priorityForPerkAndRank(self, perkName, rank):
        return self.perkPrefs[perkName][str(rank)]['Priority']
    
    def effectivePriorityForPerkAndRank(self, perkName, rankNum, level=0):
        # If priority is -1, it is inhereted from an earlier rank
        pri = self.perkPrefs[perkName][str(rankNum)]['Priority']
        if pri > -1:
            return pri
        else:            
            for rankNum_i, rank in enumerate(reversed(self.nameToPerkRanksMap[perkName])):
                pri = self.perkPrefs[perkName][str(rankNum_i)]['Priority']
                if pri > -1:
                    return pri
        return -1
        
    def availablePerksForSpecial(self, specialStats, _cache={}):
        # returns [(perkName, special_attr_letter)]
        if 'specialStats' in _cache:
            if _cache['specialStats'] == specialStats:
                # print('using cache')
                return _cache['availablePerks']
        
        availablePerks = []
        for k in 'SPECIAL':
            attrPerks = self.perks[k]
            for i in range(0, specialStats[k]):
                availPerk = attrPerks[i]
                perkName = availPerk['Name']
                availablePerks.append((perkName, k, self.priorityForPerkAndRank(perkName, 0)))
        _cache['availablePerks'] = availablePerks
        _cache['specialStats'] = dict(specialStats)
        return availablePerks
        
    def availablePerksForLevel(self, charLevel):
        # returns (name, rank, rankNum)
        # print('         BEGIN availablePerksForLevel')
        perksForLevel = self.perksForLevel(charLevel)
        # print(len(perksForLevel))
        available = self.availablePerksForSpecial(self.perkPrefs['Stats'])
        # print(len(available))
        availableNames = [x[0] for x in available]
        # print(len(availableNames))
        availablePerksForLevel = filter(lambda p: p[0] in availableNames, perksForLevel)
        # print(len(availablePerksForLevel))
        # print('         END availablePerksForLevel')
        # print(availablePerksForLevel)
        return availablePerksForLevel[:] # return a copy
    
    def generatedPerkList(self, empty=False):
        # returns [(perkName, int(rankNum), level, bool(forced))]
        genList = []
        perks = self.availablePerksForLevel(1)
        delayedPerks = []
        allForcedPerks = self.allForcedPerks()
        
        for (perkName, rankNum, level) in allForcedPerks:
            match = filter(lambda p: p[0] == perkName and p[2] == rankNum,perks)
            if len(match) > 0:
                perks.remove(match[0])
            
        for lvl in range(2, maxLevel+1):
            matchedUnlocks = filter(lambda p: p[2] == lvl, allForcedPerks)
            if len(matchedUnlocks) > 0:
                # print(matchedUnlocks)
                matchedUnlock = matchedUnlocks[0]
                genList.append((matchedUnlock[0], matchedUnlock[1], lvl, True))
                continue   
            
            if empty:
                genList.append((None, 0, lvl, False))
                continue 
            
            # print('level '+str(lvl))
            # first scan delayed perks
            for (name, rank, rankNum) in delayedPerks:
                if name not in [x[0] for x in perks]:
                    perks.append((name, rank, rankNum))
                    delayedPerks.remove((name, rank, rankNum))
                    
            availPerks = perkModel.availablePerksForLevel(lvl)
            if availPerks is not None:
                for (name, rank, rankNum) in availPerks:
                    if (name, rankNum) in [(u[0], u[1]) for u in allForcedPerks]:
                        continue
                    elif name not in [x[0] for x in perks]: # if we already have a previous perk's rank in the list to choose from, don't add it again
                        perks.append((name, rank, rankNum))
                    else:
                        delayedPerks.append((name, rank, rankNum))
            
            
            sortedPerks = sorted(perks, key=lambda p: perkModel.effectivePriorityForPerkAndRank(p[0], p[2]), reverse=True)
            if len(sortedPerks) > 0:
                selectedPerk = sortedPerks[0]
                # print(selectedPerk)
                perks.remove(selectedPerk)
                genList.append((selectedPerk[0], selectedPerk[2], lvl, False))
        return genList

class Application(Frame):
    def dec(self, attr, label):
        special = perkModel.perkPrefs['Stats']
        special[attr] = special[attr] - 1
        label.config(text=str(special[attr]))
        perkModel.savePrefs()
        self.updatePerkList()
        
    def inc(self, attr, label):
        special = perkModel.perkPrefs['Stats']
        special[attr] = special[attr] + 1
        label.config(text=str(special[attr]))
        perkModel.savePrefs()
        self.updatePerkList()
        
    def selectedPerkNameInPerkList(self):
        if len(self.perkList.curselection()) > 0:
            avail = perkModel.availablePerksForSpecial(perkModel.perkPrefs['Stats'])
            selectedPerk = avail[self.perkList.curselection()[0]][0] # curselection[0] is selected index, avail[i][0] is the perk name (avail[i][1] is the stat/attribute type (SPECIAL))
            return selectedPerk
        return None
    
    def forceSelectedPerkAtSelectedLevel(self):
        if len(self.resultsPerkList.curselection()) > 0:
            selectedPerkName = self.selectedPerkNameInPerkList()
            selectedLevel = self.resultsPerkList.curselection()[0] + 2
            # print(selectedLevel)
            ranks = perkModel.perkRanksForName(selectedPerkName)
            for rankNum_i, rank in enumerate(ranks):
                # print(rankNum_i)
                # print(perkModel.unlockedPerkAndRank(selectedPerkName, rankNum_i))
                # print(rank['CharLevel'])
                if perkModel.unlockedPerkAndRank(selectedPerkName, rankNum_i) >= selectedLevel:
                    # invalid selection as a previous rank was already unlocked an an earlier level - just return
                    return
                elif perkModel.unlockedPerkAndRank(selectedPerkName, rankNum_i) == 0 and int(rank['CharLevel']) <= selectedLevel:
                    # succeed
                    perkModel.setUnlockPerkAndRank(selectedPerkName, rankNum_i, selectedLevel)
                    break
            # perkModel.allForcedPerks()
            self.generateList(empty=True)
    
    def forceSelectedPerksInResults(self):
        genList = perkModel.generatedPerkList()
        for i in range(0, len(self.resultsPerkList.curselection())):
            selectedIndex = self.resultsPerkList.curselection()[i]
            selectedLevel = selectedIndex + 2
            selectedPerk = genList[selectedIndex]
            perkModel.setUnlockPerkAndRank(selectedPerk[0], selectedPerk[1], selectedLevel)
        self.generateList(empty=True)
    
    def clearForcedSelectedPerkAtSelectedLevel(self):
        for i in range(0, len(self.resultsPerkList.curselection())):
            selectedLevel = self.resultsPerkList.curselection()[i] + 2
            matchedUnlocks = filter(lambda p: p[2] == selectedLevel, perkModel.allForcedPerks())
            if (len(matchedUnlocks) > 0):
                matchedUnlock = matchedUnlocks[0]
                perkModel.setUnlockPerkAndRank(matchedUnlock[0], matchedUnlock[1], 0)
        self.generateList(empty=True)
    
    def showSetPerks(self):
        self.generateList(empty=True)
    
    def perkListDoubleClick(self, event):
        # print('double click')
        pass
    
    def perkListSelectionChanged(self, event):
        self.ignorePriorityChanges = TRUE
        # print('selected')
        selectedPerk = self.selectedPerkNameInPerkList()
        details = perkModel.perkRanksForName(selectedPerk)
        # print(selectedPerk)
        # print(details)
        for rankNum, rank in enumerate(details):
            # print(rankNum)
            labels = self.perkDetails[rankNum]
            perkDetailLabel1, perkDetailLabel2, perkDetailLabel3, perkDetailLabel4, spinVar = labels[0], labels[1], labels[2], labels[3], labels[4]
            # perkDetailLabel1.grid(row=rankNum,column=0)
            # perkDetailLabel2.grid(row=rankNum,column=1)
            # perkDetailLabel3.grid(row=rankNum,column=2,sticky=N+E+S+W)
            # perkDetailLabel4.grid(row=rankNum,column=3,sticky=E)
            desc = rank['Description']
            charLevel = int(rank['CharLevel'])
            perkDetailLabel2["text"] = str(charLevel)
            perkDetailLabel3["text"] = desc
            # print('priority: '+str(perkModel.priorityForPerkAndRank(selectedPerk,rankNum)))
            spinVar.set(str(perkModel.priorityForPerkAndRank(selectedPerk,rankNum)))
        for i in range(len(details), 5):
            labels = self.perkDetails[i]
            perkDetailLabel1, perkDetailLabel2, perkDetailLabel3, perkDetailLabel4, spinVar = labels[0], labels[1], labels[2], labels[3], labels[4]
            # perkDetailLabel1.grid_forget()
            # perkDetailLabel2.grid_forget()
            # perkDetailLabel3.grid_forget()
            # perkDetailLabel4.grid_forget()
            perkDetailLabel2["text"] = ""
            perkDetailLabel3["text"] = ""
            spinVar.set("0")
        self.ignorePriorityChanges = FALSE
        self.updateButtonStates()
    
    def optimizedListSelectionChanged(self, event, _selectRelatedPerk=False):
        self.updateButtonStates()
        if _selectRelatedPerk:
            # if only a single level is selected, select the related perk on the left
            genList = perkModel.generatedPerkList()
            avail = perkModel.availablePerksForSpecial(perkModel.perkPrefs['Stats'])
            if len(self.resultsPerkList.curselection()) == 1:
                selectedIndex = self.resultsPerkList.curselection()[0]
                selectedPerk = genList[selectedIndex]
                selectedPerkName = selectedPerk[0]
                for ndx, p in enumerate(avail):
                    if selectedPerkName == p[0]:
                        self.perkList.selection_clear(0, END)
                        self.perkList.selection_set(ndx)
                        self.perkListSelectionChanged(None)
                        return
            
    def priorityChanged(self,widget,x,y):
        if self.ignorePriorityChanges:
            return
        selectedPerk = self.selectedPerkNameInPerkList()
        if selectedPerk is None:
            return
        details = perkModel.perkRanksForName(selectedPerk)
        for rankNum, rank in enumerate(details):
            labels = self.perkDetails[rankNum]
            if widget == labels[5]:
                # we matched the traced widget name to the Spinbox's textvariable name
                spinVar = labels[4]
                val = spinVar.get()
                if len(val) > 0:
                    newPriority = int(spinVar.get())
                    perkModel.setPriorityForPerkAndRank(selectedPerk,rankNum,newPriority)
                return
    
    def updateButtonStates(self):
        leftSelected = len(self.perkList.curselection())
        rightSelected = len(self.resultsPerkList.curselection())
        selectedPerkText = '(Selected Perk)'
        selectedLevelText = '(Level)'
        if leftSelected > 0 and rightSelected == 1:
            selectedPerkText = self.selectedPerkNameInPerkList()
            selectedLevelText = 'Level '+str(self.resultsPerkList.curselection()[0] + 2)
            self.forcePerk.config(state=NORMAL)
        else:
            self.forcePerk.config(state=DISABLED)
        self.forcePerk.config(text='Force '+selectedPerkText+' at '+selectedLevelText)
        
        if rightSelected == 1:
            self.clearPerk.config(state=NORMAL, text='Clear Forced Perk')
        elif rightSelected > 1:
            self.clearPerk.config(state=NORMAL, text='Clear Forced Perks')
        else:
            self.clearPerk.config(state=DISABLED, text='Clear Forced Perk')
        
        if rightSelected > 0:
            self.forcePerkFromRightSelection.config(state=NORMAL)
        else:
            self.forcePerkFromRightSelection.config(state=DISABLED)
        
    def createWidgets(self):
        self.perkListFrame = LabelFrame(self, text='Perks')
        self.perkListFrame.pack({"side": "bottom"})
        
        availPerkListFrame = LabelFrame(self.perkListFrame, text='Available')
        availPerkListFrame.grid(row=0,column=0)
        self.perkList = Listbox(availPerkListFrame, height=35, width=25, exportselection=0)
        self.perkList.bind('<Double-1>', self.perkListDoubleClick)
        self.perkList.bind('<<ListboxSelect>>', self.perkListSelectionChanged)
        self.perkList.pack({"side": "left"})
        
        middleButtonsFrame = Frame(self.perkListFrame)
        middleButtonsFrame.grid(row=0,column=1)
        generate = Button(middleButtonsFrame, text='Show Optimized Build')
        generate.grid(row=0,column=0)
        generate.config(command = self.generateList)
        
        showSetPerks = Button(middleButtonsFrame, text='Show Forced Perks')
        showSetPerks.grid(row=0,column=1)
        showSetPerks.config(command = self.showSetPerks)
        
        self.forcePerk = Button(middleButtonsFrame, text='Force (Selected Perk) at (Level)', state=DISABLED)
        self.forcePerk.grid(row=1,column=0, columnspan=2)
        self.forcePerk.config(command = self.forceSelectedPerkAtSelectedLevel)
        
        self.forcePerkFromRightSelection = Button(middleButtonsFrame, text='Save Selected Levels as Forced Perks', state=DISABLED)
        self.forcePerkFromRightSelection.grid(row=2,column=0, columnspan=2)
        self.forcePerkFromRightSelection.config(command = self.forceSelectedPerksInResults)
        
        self.clearPerk = Button(middleButtonsFrame, text='Clear Forced Perk', state=DISABLED)
        self.clearPerk.grid(row=3,column=0, columnspan=2)
        self.clearPerk.config(command = self.clearForcedSelectedPerkAtSelectedLevel)
        
        resultsPerkListFrame = LabelFrame(self.perkListFrame, text='Optimized Build')
        resultsPerkListFrame.grid(row=0,column=2)
        self.resultsPerkList = Listbox(resultsPerkListFrame, height=35, width=25, exportselection=0, selectmode=EXTENDED)
        # self.resultsPerkList.bind('<Double-1>', self.perkListDoubleClick)
        self.resultsPerkList.bind('<<ListboxSelect>>', self.optimizedListSelectionChanged)
        self.resultsPerkList.pack({"side": "left"})
        
        self.perkDetailFrame = LabelFrame(self.perkListFrame, text='Details')
        self.perkDetailFrame.grid(row=1,column=0,columnspan=3,sticky=N+E+S+W)
        self.perkDetails = []
        for i in range(0, 5):
            perkDetailLabel1 = Label(self.perkDetailFrame, text='Rank '+str(i+1))
            perkDetailLabel1.grid(row=i,column=0)
            perkDetailLabel2 = Label(self.perkDetailFrame, text='0', width=3)
            perkDetailLabel2.grid(row=i,column=1)
            perkDetailLabel3 = Label(self.perkDetailFrame, text='Details',anchor=W,justify=LEFT,relief=RIDGE,height=2,width=75,wraplength=650)
            perkDetailLabel3.grid(row=i,column=2,sticky=N+E+S+W)
            spinVar = StringVar()
            spinVar.set('')
            spinVar.trace_variable('w',self.priorityChanged)
            varName = spinVar.__str__()
            perkDetailLabel4 = Spinbox(self.perkDetailFrame, from_=-1, to=maxPriority, justify=CENTER, width=3,textvariable=spinVar,exportselection=0)
            perkDetailLabel4.grid(row=i,column=3,sticky=E)
            self.perkDetails.append((perkDetailLabel1,perkDetailLabel2,perkDetailLabel3,perkDetailLabel4,spinVar,varName))
        
        self.attributes = LabelFrame(self, text='Stats')
        self.attributes.pack({"side": "top"})
        
        for k in 'SPECIAL':
            labelframe = LabelFrame(self.attributes, text=k)
            labelframe.pack({"side": "left"})
            decreaseVal = Button(labelframe, text='<')
            decreaseVal.pack({"side": "left"})
            valLabel = Label(labelframe, text=str(perkModel.perkPrefs['Stats'][k]))
            valLabel.pack({"side": "left"})
            increaseVal = Button(labelframe, text='>')
            increaseVal.pack({"side": "left"})
            decreaseVal.config(command = lambda k=k, valLabel=valLabel: self.dec(k, valLabel))
            increaseVal.config(command = lambda k=k, valLabel=valLabel: self.inc(k, valLabel))
            
        # self.QUIT = Button(self)
        # self.QUIT["text"] = "QUIT"
        # # self.QUIT["fg"]   = "red"
        # self.QUIT["command"] =  self.quit
        # self.QUIT.pack({"side": "bottom"})
                
    def generateList(self, empty=False):
        self.resultsPerkList.delete(0, END)
        genList = perkModel.generatedPerkList(empty)
        for i, v in enumerate(genList):
            name, rank, level, forced = v
            if name is not None:
                self.resultsPerkList.insert(END, str(level)+': '+name+' '+str(rank+1))
                if forced:
                    self.resultsPerkList.itemconfig(END, fg="blue")
            else:
                self.resultsPerkList.insert(END, str(level)+': ')
        self.resultsPerkList.pack()
        self.updateButtonStates()
            
    def updatePerkList(self):
        self.perkList.delete(0, END)
        avail = perkModel.availablePerksForSpecial(perkModel.perkPrefs['Stats'])
        for i, p in enumerate(avail):
            perkName = p[0]
            firstRankPri = p[2]
            self.perkList.insert(END, p[1] + ': ' + perkName)
            
        self.perkList.pack()
        self.updateButtonStates()
        # print('updated')

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.ignorePriorityChanges = True
        self.pack()
        self.createWidgets()
        self.updatePerkList()
        self.generateList(empty=True)
        self.ignorePriorityChanges = False

# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(levelToPerkMap)

perkModel = Perks()
root = Tk()
app = Application(master=root)
root.title('Fallout 4 Perkolator') 
app.mainloop()
root.destroy()