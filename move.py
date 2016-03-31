# EasyBouquets
# Feel free to add comments and pas extra stuff You would have fitted in.
# gravatasufoca@yahoo.com.br
# Bruno Teixeira canto de Lima

from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.config import  getConfigListEntry,ConfigSelection,ConfigSelectionNumber
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
import utils

class OrderScreenConf(ConfigListScreen, Screen):

    skin = """
        <screen name="bouquet" title="%s" position="center,center" size="500,300">            
              
            <ePixmap pixmap="$PLUGINDIR$/buttons/red.png" position="15,260" size="26,26" alphatest="on" />
            <widget source="key_red" render="Label" position="55,260" size="220,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

            <ePixmap pixmap="$PLUGINDIR$/buttons/green.png" position="190,260" size="26,26" alphatest="on" />
            <widget source="key_green" render="Label" position="230,260" size="220,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

            <widget name="config" position="10,15" size="490,100" scrollbarMode="showOnDemand" selectionPixmap="$PLUGINDIR$/buttons/sel.png" />
         </screen>"""%(_("Sort Bouquets"))         
        
    def __init__(self, session, favname,ordem):
        
        self.skin=OrderScreenConf.skin.replace("$PLUGINDIR$", utils.easybouquet_plugindir)
        
        self.session = session
        Screen.__init__(self, session)
            
        self.list = []
        self.favname = favname  
        self.ordem=int(ordem)
        self.direcao=ConfigSelection(default="down", choices=[
                    ("up",_("Up")),
                    ( "down",_("Down"))
                    ])
        self.quantidade=ConfigSelectionNumber(1, 5, 1, default=1, wraparound=True)
        
        self.list.append(getConfigListEntry(_("Direction"), self.direcao))
        self.list.append(getConfigListEntry(_("Amount"), self.quantidade))
        
        ConfigListScreen.__init__(self, self.list)
        

        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("Save"))
        self["actions"] = ActionMap(["SetupActions", "OkCancelActions", "ColorActions", "DirectionActions"], {
            "red": self.close,
            "cancel": self.close,
            "save": self.save,
            "green": self.save,
            "ok": self.save
        }, -2)
        
    def save(self):
        
        from tempfile import mkstemp 
        from shutil import move 
        from os import remove, close 
        
        
        favoritos=[]
        filerules = open(utils.rules,"r")
        for rule in filerules:
            favoritos.append(rule)
            
        filerules.close()
        
        fav=favoritos.pop(self.ordem)
        
        if self.direcao.value=="down":
            novaordem=int(self.ordem)+int(self.quantidade.value)
        else:
            novaordem=int(self.ordem)-int(self.quantidade.value)
            if novaordem<0:
                novaordem=0
            
        favoritos.insert(novaordem, fav)
        
        
        #Create temp file 
        fh, abs_path = mkstemp() 
        new_file = open(abs_path, 'w') 
        
        for rule in favoritos:
            new_file.write(rule)
        
        new_file.close()
        close(fh) 
        #Remove original file 
        remove(utils.rules) 
        #Move new file 
        move(abs_path, utils.rules) 
        self.close()
     