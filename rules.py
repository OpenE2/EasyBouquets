# EasyBouquets
# Feel free to add comments and pas extra stuff You would have fitted in.
# gravatasufoca@yahoo.com.br
# Bruno Teixeira canto de Lima
from . import _
from Components.ActionMap import ActionMap
from Screens.Screen import Screen
from Components.config import config,  getConfigListEntry,  ConfigText, ConfigSubsection, ConfigYesNo,ConfigSelection

from Components.ConfigList import ConfigListScreen

from Components.Sources.StaticText import StaticText
import utils
from Screens.MessageBox import MessageBox

config.plugins.RuleConf = ConfigSubsection()
config.plugins.RuleConf.name = ConfigText(fixed_size=False)
config.plugins.RuleConf.negado = ConfigYesNo(default=False)
config.plugins.RuleConf.sat = ConfigSelection(choices=[])
config.plugins.RuleConf.tp = ConfigSelection(choices=[])
config.plugins.RuleConf.sid = ConfigText(fixed_size=False)
config.plugins.RuleConf.hd = ConfigYesNo(default=False)
# config.plugins.RuleConf.ordem = ConfigText(fixed_size=False)


class RuleScreenConf(ConfigListScreen, Screen):

    skin = """
        <screen name="bouquet" position="center,center" size="759,609">
                <ePixmap pixmap="$PLUGINDIR$/buttons/red.png" position="35,560" size="26,26" alphatest="on" />
                <widget source="key_red" render="Label" position="72,560" size="271,26" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

                <ePixmap pixmap="$PLUGINDIR$/buttons/green.png" position="359,560" size="26,26" alphatest="on" />
                <widget source="key_green" render="Label" position="397,560" size="327,26" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

                <widget name="config" position="35,29" size="691,526" scrollbarMode="showOnDemand" selectionPixmap="$PLUGINDIR$/buttons/sel.png" font="Regular;24"/>
        </screen>"""
        
    def __init__(self, session,rule,favname):
        self.skin=RuleScreenConf.skin.replace("$PLUGINDIR$", utils.easybouquet_plugindir)
        self.session = session
        Screen.__init__(self, session)
        self["Title"].text = _("Rules Configuration")
        self.list = []
        self.favname = favname
        self.old = {"not":False,"sat":"","tp":"","sid":"","rule":"","hd":False,"order":""}
        
        self.edit = False
        if rule is not -1:
            self.edit = True
            self.old=rule   
            
        
        self.onFirstExecBegin.append(self.montaSatelites)
#        self.onFirstExecBegin.append(self.montaTransponder)
        
        config.plugins.RuleConf.name.value = self.old["rule"]            
        config.plugins.RuleConf.negado.value = self.old["not"]  
        config.plugins.RuleConf.tp.value = self.old["tp"]  
        config.plugins.RuleConf.sid.value = self.old["sid"]  
        config.plugins.RuleConf.hd.value = self.old["hd"]
        # config.plugins.RuleConf.ordem.value = self.old["order"]
        
        config.plugins.RuleConf.tp.setChoices(choices=[("",_("None"))])
        
        config.plugins.RuleConf.sat.addNotifier(notifier=self.montaTransponder, immediate_feedback=False)
        
        self.list.append(getConfigListEntry(_("Rule"), config.plugins.RuleConf.name))
        self.list.append(getConfigListEntry(_("Not"), config.plugins.RuleConf.negado))
        self.list.append(getConfigListEntry(_("SAT"), config.plugins.RuleConf.sat))
        self.list.append(getConfigListEntry(_("TP"), config.plugins.RuleConf.tp))
        self.list.append(getConfigListEntry(_("SID"), config.plugins.RuleConf.sid))
        self.list.append(getConfigListEntry(_("HD"), config.plugins.RuleConf.hd))
        # self.list.append(getConfigListEntry(_("Order"), config.plugins.RuleConf.ordem))
        
        ConfigListScreen.__init__(self, self.list,session=self.session)

        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("Save"))
        self["actions"] = ActionMap(["SetupActions", "OkCancelActions", "ColorActions", "DirectionActions"], {
            "red": self.cancel,
            "cancel": self.cancel,
            "save": self.save,
            "green": self.save,
            "ok": self.save
        }, -2)

    def montaSatelites(self):
        tmp=[("",_("None"))]
        tmp.extend(utils.obterSatelites())

        sat=self.old["sat"]
        if sat:
            sat = utils.satToPosition(self.old["sat"])
        print "satelite: %s"%sat
        config.plugins.RuleConf.sat.setChoices(choices=tmp)
        config.plugins.RuleConf.sat.value=sat
        print "satelite: %s"%config.plugins.RuleConf.sat.value

    def montaTransponder(self,configElement):
            tmp=[("",_("None"))]
            tmp.extend(utils.obterTransponder(config.plugins.RuleConf.sat.value))        
            config.plugins.RuleConf.tp.setChoices(tmp)
            config.plugins.RuleConf.tp.setValue("")
            config.plugins.RuleConf.tp.changedFinal()
        
    def cancel(self):
        for i in self["config"].list:
            i[1].cancel()
        self.close(True)
                
    def save(self):
        
        if not config.plugins.RuleConf.name.value:
            self.session.open(MessageBox,_("The field is required!"), MessageBox.TYPE_ERROR, close_on_any_key=True, timeout=20)
            return False        
        
        from tempfile import mkstemp 
        from shutil import move 
        from os import remove, close 
        
        sat=utils.positionToSat(config.plugins.RuleConf.sat.value)
        
        #Create temp file 
        fh, abs_path = mkstemp() 
        new_file = open(abs_path, 'w') 
        
        arq=open(utils.rules,"r")
        
        for rule in arq:
            rule = rule.replace('\n','')
            rule=rule.strip()
            if rule:
                favname,channellist = rule.partition("=")[::2]
                favname = favname.strip()
                if favname==self.favname:
                    
                    novaregra={
                                "not":config.plugins.RuleConf.negado.value,
                                "sat":sat,
                                "tp":config.plugins.RuleConf.tp.value,
                                "sid":config.plugins.RuleConf.sid.value,
                                "rule":config.plugins.RuleConf.name.value,
                                "hd":config.plugins.RuleConf.hd.value
                                # "order":config.plugins.RuleConf.ordem.value
                              }
                    if self.edit:
                        channellist=self.gerarChannellist(novaregra,self.old["rule"],utils.obterRegras(favname))
                    else:
                        channellist+=","+utils.addRule(novaregra)
                        
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
        
        self.close()
        
        
    def gerarChannellist(self,novaregra,regraantiga,regras):
        channellist=[]
        for rule in regras:
            regra=rule["rule"]
            negado=rule["not"]
            sat=rule["sat"]
            tp=rule["tp"]
            sid=rule["sid"]
            hd=rule["hd"]
            # ordem=rule["order"]
            
            if regra==regraantiga:
                regra=novaregra["rule"]
                negado=novaregra["not"]
                sat=novaregra["sat"]
                tp=novaregra["tp"]
                sid=novaregra["sid"]
                hd=novaregra["hd"]
                # ordem=novaregra["order"]
            
         
            tmpregra={
                       "not":negado,
                       "sat":sat,
                       "tp":tp,
                       "sid":sid,
                       "rule":regra,
                       "hd":hd
                       # "order":ordem
                  }
        
            channellist.append(utils.addRule(tmpregra))
        
        return ",".join(channellist)
            
            