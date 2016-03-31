# EasyBouquets
# Feel free to add comments and pas extra stuff You would have fitted in.
# gravatasufoca@yahoo.com.br
# Bruno Teixeira canto de Lima

from Components.Sources.StaticText import StaticText
from Components.config import config, getConfigListEntry, ConfigSubsection,ConfigSelection,\
    ConfigYesNo
from Components.ConfigList import ConfigList,ConfigListScreen
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
import utils
from loading import LoadingScreen
from help import HelpScreen
from bouquetsList import BouquetsList


config.plugins.Easy = ConfigSubsection()
config.plugins.Easy.pref = ConfigSelection(choices=[])
config.plugins.Easy.addSat=ConfigYesNo(default=True)

# Class EasyBouquetScreen
class EasyBouquetScreen(ConfigListScreen, Screen):
    
    skin = """
        <screen name="bouquet" title="" position="center,center" size="500,250">            
              
            <ePixmap pixmap="$PLUGINDIR$/buttons/red.png" position="15,210" size="26,26" alphatest="on" />
            <widget source="key_red" render="Label" position="55,210" size="220,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

            <ePixmap pixmap="$PLUGINDIR$/buttons/green.png" position="190,210" size="26,26" alphatest="on" />
            <widget source="key_green" render="Label" position="230,210" size="220,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

            <ePixmap pixmap="$PLUGINDIR$/buttons/yellow.png" position="345,210" size="26,26" alphatest="on" />
            <widget source="key_yellow" render="Label" position="385,210" size="220,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

            <widget name="config" position="10,15" size="490,140" scrollbarMode="showOnDemand" selectionPixmap="$PLUGINDIR$/buttons/sel.png" />
            <widget source="status" render="Label" position="5,85" zPosition="10" size="490,55" halign="center" valign="center" font="Regular;20" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
         </screen>"""            
    
    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.skin=EasyBouquetScreen.skin.replace("$PLUGINDIR$", utils.easybouquet_plugindir)
#        self.skinName = [ "Setup" ]
        self.list = []
        self["config"] = ConfigList(self.list)

        self.sats=utils.obterSatelites()
           
        config.plugins.Easy.pref.setChoices(self.sats)
        
        self.list.append(getConfigListEntry(_("Preferential Satellite"), config.plugins.Easy.pref))
        self.list.append(getConfigListEntry(_("Add satellite name"), config.plugins.Easy.addSat))

        ConfigListScreen.__init__(self, self.list)
         
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("Create"))
        self["key_yellow"] = StaticText(_("Rules"))
        self["status"]=StaticText(_("The \"Favourites (Tv)\" bouquet will be created based on the \"Preferential Satellite\" chosen."))
        
        self["actions"] = ActionMap(["OkCancelActions","InputActions","ColorActions", "setupActions"],
        {
            "green": self.confirma,
            "red": self.cancel,
            "cancel": self.cancel,
            "ok":self.confirma,
            "yellow":self.abrirListaBouquets
        }, -2)
        
        self.setTitle("%s-%s by %s"%(utils.easybouquet_title,utils.easybouquet_version,utils.easybouquet_developer))
        

    def abrirListaBouquets(self):
        self.session.open(BouquetsList)
        
    def cancel(self):
        for i in self["config"].list:
            i[1].cancel()
        self.close(False)
        
    def confirma(self):
        self.session.openWithCallback(self.showLoading, MessageBox, _("All your current favorites will be deleted!\nDo you confirm the creating of the new ones?"), MessageBox.TYPE_YESNO)
                

    def showLoading(self,answer):
        if answer: 
            self.hide()               
            self.session.open(LoadingScreen)
            self.close()

    def mostraAjuda(self):
        self.session.open(HelpScreen)