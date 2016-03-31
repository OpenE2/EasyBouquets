# EasyBouquets
# Feel free to add comments and pas extra stuff You would have fitted in.
# gravatasufoca@yahoo.com.br
# Bruno Teixeira canto de Lima

from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.config import config, getConfigListEntry, ConfigText, \
    ConfigSubsection
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
import utils
from rules import RuleScreenConf
from Screens.MessageBox import MessageBox




config.plugins.BouquetConf = ConfigSubsection()
config.plugins.BouquetConf.name = ConfigText(fixed_size=False)

class BouquetScreenConf(ConfigListScreen, Screen):

    skin = """
        <screen name="bouquet" title="%s" position="center,center" size="750,600">            
              
            <ePixmap pixmap="$PLUGINDIR$/buttons/green.png" position="15,560" size="26,26" alphatest="on" />
            <widget source="key_green" render="Label" position="55,560" size="220,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

            <widget name="config" position="10,15" size="740,30" scrollbarMode="showOnDemand" selectionPixmap="$PLUGINDIR$/buttons/sel.png" />
            <widget transparent="1" name="menu" position="10,45" size="740,510" scrollbarMode="showOnDemand" />
         </screen>""" %(_("Bouquets Configuration"))   

    skinEdit = """
        <screen name="bouquet" title="%s" position="center,center" size="750,600">            
              
            <ePixmap pixmap="$PLUGINDIR$/buttons/green.png" position="15,560" size="26,26" alphatest="on" />
            <widget source="key_green" render="Label" position="55,560" size="220,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

            <ePixmap pixmap="$PLUGINDIR$/buttons/yellow.png" position="190,560" size="26,26" alphatest="on" />
            <widget source="key_yellow" render="Label" position="230,560" size="220,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

            <ePixmap pixmap="$PLUGINDIR$/buttons/blue.png" position="345,560" size="26,26" alphatest="on" />
            <widget source="key_blue" render="Label" position="385,560" size="220,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

            <widget name="config" position="10,15" size="740,30" scrollbarMode="showOnDemand" selectionPixmap="$PLUGINDIR$/buttons/sel.png" />
            <widget transparent="1" name="menu" position="10,45" size="740,510" scrollbarMode="showOnDemand" />
         </screen>""" %(_("Bouquets Configuration"))                 
        
    def __init__(self, session, favname):
        
        self.favname = ""
        self.old_name = ""
        
        self.edit = False
        if favname is not -1:
            self.edit = True
            self.favname = favname
            self.old_name = favname
        
        if not self.edit:
            self.skin=BouquetScreenConf.skin.replace("$PLUGINDIR$", utils.easybouquet_plugindir)
        else:
            self.skin=BouquetScreenConf.skinEdit.replace("$PLUGINDIR$", utils.easybouquet_plugindir)
        
        self.session = session
        Screen.__init__(self, session)
        self.menuList = []
        self.onShow.append(self.updateMenu)
        self["menu"] = MenuList(self.menuList, enableWrapAround=True)
        
        self.list = []
        
        config.plugins.BouquetConf.name.value = self.favname

        self.list.append(getConfigListEntry(_("Bouquet"), config.plugins.BouquetConf.name))
        
        ConfigListScreen.__init__(self, self.list,session=self.session)
        
        

        self["key_green"] = StaticText(_("Save"))
        self["key_yellow"] = StaticText(_("Add rule"))
        self["key_blue"] = StaticText(_("Remove rule"))
        
        self["actions"] = ActionMap(["SetupActions", "OkCancelActions", "ColorActions", "DirectionActions"], {
            "blue": self.remover,
            "cancel": self.cancel,
            "save": self.save,
            "green": self.save,
            "ok": self.go,
            "yellow": self.addRule
        }, -2)


    def addRule(self):
        config.plugins.BouquetConf.name.onDeselect(self.session)
        self.session.open(RuleScreenConf,-1,self.favname)
        
    
    def remover(self):
        returnValue = self["menu"].l.getCurrentSelection()[1]
        print "regra %s"%returnValue
        if returnValue is not None:  
            self.session.openWithCallback(self.removeRule, MessageBox, _("Do you really want to remove the rule?"), MessageBox.TYPE_YESNO)
        else:
            self.session.open(MessageBox,_("Select a rule first!"), MessageBox.TYPE_ERROR, close_on_any_key=True, timeout=20)

    
    def removeRule(self,answer):
        if answer:
            returnValue = self["menu"].l.getCurrentSelection()[1]
            if returnValue is not None:  
                channellist=utils.gerarChannellist(utils.removerRegra(returnValue, utils.obterRegras(self.favname)))
                
                
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
                        if favname==self.favname:
                            new_file.write("%s=%s\n"%(favname,channellist))
                        else:
                            new_file.write(rule+"\n")
                
                new_file.close()
                arq.close()
                
                close(fh) 
                #Remove original file 
                remove(utils.rules) 
                #Move new file 
                move(abs_path, utils.rules)
                self.updateMenu()
                

    def updateMenu(self):
        menuItens=[]
        regras=utils.obterRegras(self.favname)
        for regra in regras:
            menuItens.append((_(regra["rule"]), regra))
            
        self.menuList=menuItens
        self["menu"].setList(self.menuList)                            

    def go(self):
        returnValue = self["menu"].l.getCurrentSelection()[1]
        if returnValue is not None:  
            config.plugins.BouquetConf.name.onDeselect(self.session)
            self.session.open(RuleScreenConf,returnValue,self.favname)

    def cancel(self):
        for i in self["config"].list:
            i[1].cancel()
        self.close(True)
                
    def save(self):
        if not config.plugins.BouquetConf.name.value:
            self.session.open(MessageBox,_("The field is required!"), MessageBox.TYPE_ERROR, close_on_any_key=True, timeout=20)
            return False
            
        arq=open(utils.rules,"rw")
        if self.edit:
            arqtmp=open(utils.rulestmp,"w")
            
            for rule in arq:
                rule = rule.replace('\n','')
                rule=rule.strip()
                if rule:
                    favname, channellist = rule.partition("=")[::2]
                    favname = favname.strip()
                    if favname==self.old_name:
                        favname=config.plugins.BouquetConf.name.value
                    
                    arqtmp.write("%s=%s\n"%(favname,channellist))
            
            arqtmp.close()
            arq.close()
        else:
            favname=config.plugins.BouquetConf.name.value
            arq.write("%s=\n"%favname.strip())
            arq.close()
