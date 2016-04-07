# EasyBouquets
# Feel free to add comments and pas extra stuff You would have fitted in.
# gravatasufoca@yahoo.com.br
# Bruno Teixeira canto de Lima
import re

from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

import utils
from bouquets import BouquetScreenConf
from move import OrderScreenConf


class BouquetsList(Screen):
        
    skin = """
        <screen name="bouquet" title="" position="center,center" size="750,600">
            <ePixmap pixmap="$PLUGINDIR$/buttons/red.png" position="15,560" size="26,26" alphatest="on" />
            <widget source="key_red" render="Label" position="43,560" size="180,26" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

            <ePixmap pixmap="$PLUGINDIR$/buttons/green.png" position="230,560" size="26,26" alphatest="on" />
            <widget source="key_green" render="Label" position="261,560" size="220,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

            <ePixmap pixmap="$PLUGINDIR$/buttons/yellow.png" position="488,560" size="26,26" alphatest="on" />
            <widget source="key_yellow" render="Label" position="522,560" size="220,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

            <widget name="tituloLabel" render="Label" position="55,12" size="640,40"  halign="center" />
            <widget transparent="1" name="menu" position="55,57" size="640,493" scrollbarMode="showOnDemand" render="Listbox" itemHeight="25" font="Regular;24"/>
        </screen>"""
        
    def __init__(self, session, args=0):
        self.skin=BouquetsList.skin.replace("$PLUGINDIR$", utils.easybouquet_plugindir)
        self.session = session
        Screen.__init__(self, session)

        self["Title"].text = _("Bouquets List")
        self["tituloLabel"] = StaticText(_("Bouquets List"))

        self.rulesdict={}
        self.bouquetsOrder=[]
        self.menuList = []
#        self.getMenuItens()
        self.menu = args
        self.onShow.append(self.updateMenu)
        self["menu"] = MenuList(self.menuList, enableWrapAround=True)
        self["key_red"] =  StaticText(_("Remove"))
        self["key_green"] =  StaticText(_("Add"))
        self["key_yellow"] =  StaticText(_("Move"))
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"],
                                    {
                                        "ok": self.go,
                                        "cancel": self.close,
                                        "back": self.close,
                                        "red": self.remover,
                                        "green": self.add,
                                        "yellow":self.move
                                    }, -1)
        
    
    def move(self):
        returnValue = self["menu"].l.getCurrentSelection()[1]
        
        ordem=self["menu"].getSelectedIndex()
        if returnValue is not None:
            self.session.open(OrderScreenConf,returnValue, ordem)
    
    def add(self):
        returnValue = -1
        self.session.open(BouquetScreenConf, returnValue)
    
    def updateMenu(self):
        self.getMenuItens()
        self["menu"].setList(self.menuList)
                          
        
    def fechar(self):
        self["menu"].setList([])
        self.close()
    
    def go(self):
        returnValue = self["menu"].l.getCurrentSelection()[1]
        if returnValue is not None:  
            self.session.open(BouquetScreenConf,returnValue)
    
    def getMenuItens(self):
        
        self.parserules()
        menuItens = []
        for bouquet in self.bouquetsOrder:
            key=bouquet.keys()[0]                  
            menuItens.append((_(key), key))

        self.menuList = menuItens
        
    def parserules(self):
#        tmp=open("/tmp/teste","w")  

        self.rulesdict={}
        self.bouquetsOrder=[]
      
        filerules = open(utils.rules)
        for rule in filerules:
            rule = rule.replace('\n','')
            rule=rule.strip()
            if rule:
                if not "=" in rule:
                    self.session.open(MessageBox,_("The equal character (=) was not found at this line!\n%s") % (rule), MessageBox.TYPE_ERROR, close_on_any_key=True, timeout=20)
                    return False
                favname, channellist = rule.partition("=")[::2]
                favname = favname.strip()  
                self.rulesdict[favname]=self.preparaRegras(channellist)
                self.bouquetsOrder.append({favname:self.rulesdict[favname]})
    #            tmp.write("%s - %s\n"%(favname,self.rulesdict[favname]))
        
        if not self.rulesdict.has_key("exclude"):
            self.rulesdict["exclude"]=[]
            
        if not self.rulesdict.has_key("blacklist"):
            self.rulesdict["blacklist"]=[]
            
        if not self.rulesdict.has_key("favourites"):
            self.rulesdict["favourites"]=[]
            
#        tmp.close()
        return True
    
    def preparaRegras(self,canais):
        regras=canais.split(",")
        novasRegras=[]
        
        for regra in regras:
            sat=re.findall("(sat\[\-?\d+\])",regra)
            if len(sat)>0:
                sat=re.findall("\-?\d+",sat[0])[0]
            else:
                sat=""
            
            
            tp=re.findall("(tp\[\d+\])",regra)
            if len(tp)>0:
                tp=re.findall("\d+",tp[0])[0]
            else:
                tp=""
                
            sid=re.findall("(sid\[\d+\])",regra)
            if len(sid)>0:
                sid=re.findall("\d+",sid[0])[0]
            else:
                sid=""                
                
            rule=regra.split(":")[-1].lower()
            negado=rule.startswith("!")
            if negado:
                rule=rule.replace("!","",1)
            novasRegras.append({"sat":sat.strip(),"tp":tp.strip(),"sid":sid.strip(),"rule":rule.strip(),"not":negado})
            
        return novasRegras    
    
    def remover(self):
        returnValue = self["menu"].l.getCurrentSelection()[1]
        print "regra %s"%returnValue
        if returnValue is not None:  
            self.session.openWithCallback(self.removeBouquet, MessageBox, _("Do you really want to remove the bouquet?"), MessageBox.TYPE_YESNO)
        else:
            self.session.open(MessageBox,_("Select a bouquet first!"), MessageBox.TYPE_ERROR, close_on_any_key=True, timeout=20)

    
    def removeBouquet(self,answer):
        if answer:
            returnValue = self["menu"].l.getCurrentSelection()[1]
            if returnValue is not None:  
                from tempfile import mkstemp 
                from shutil import move 
                from os import remove, close 
                
                #Create temp file 
                fh, abs_path = mkstemp() 
                new_file = open(abs_path, 'w') 
                
                arq=open(utils.rules,"r")
                
                for rule in arq:
                    rule = rule.replace('\n','')
                    rule=rule.strip()
                    if rule:
                        favname = rule.split("=")[0]
                        favname = favname.strip()
                        if favname!=returnValue:
                            new_file.write(rule+"\n")
                
                new_file.close()
                arq.close()
                
                close(fh) 
                #Remove original file 
                remove(utils.rules) 
                #Move new file 
                move(abs_path, utils.rules)
                self.updateMenu()
                
    
