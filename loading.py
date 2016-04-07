# EasyBouquets
# Feel free to add comments and pas extra stuff You would have fitted in.
# gravatasufoca@yahoo.com.br
# Bruno Teixeira canto de Lima

from Components.config import config
from Screens.Screen import Screen
from Components.ActionMap import NumberActionMap

from Screens.MessageBox import MessageBox
import re
from Components.Label import Label
from Components.Pixmap import Pixmap
from enigma import eTimer
from Components.ProgressBar import ProgressBar
import utils

# Class ChannelScreenConf
class LoadingScreen(Screen):
    
    
    skin = """<screen name="EasyBouquet" position="677,649" size="600,70" flags="wfNoBorder">
                <widget name="action" halign="center" valign="center" position="65,10" size="520,20" font="Regular;16" transparent="1" />
                <widget name="status" halign="center" valign="center" position="65,30" size="520,20" font="Regular;16" transparent="1" />
                <widget name="progress" position="65,55" size="520,5" borderWidth="1" />
        </screen>"""
            

    def __init__(self, session):
        self.skin = LoadingScreen.skin
        self.session = session
        Screen.__init__(self, session)

        self.onFirstExecBegin.append(self.processar)
        
        self.rulesdict = {}
        self.bouquets={}
        self.bouquetsOrder=[]
        self.favouritesTv=[]
        self.favouritesRadio=[]
        self.satPref=""
        
        self["action"] = Label(_("Creating favorites"))
        self["status"] = Label()        
        self["progress"] = ProgressBar()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions"],
        {
        "back": self.close
        }, -1)


        self.atualizar=eTimer()

        self.atualizar.callback.append(self.atualizaProgresso)

        self.fechar = eTimer()
        self.fechar.callback.append(self.close)
    
        self["progress"].setValue(0)

        
    def processar(self):  
        if self.gerarBouquets():
            self.mudaSituacao(40, _("Deleting all favorites"))
            utils.removeoldfiles()
            self.mudaSituacao(50, _("Writing favorites"))
            self.escreveBouquets()
            self.mudaSituacao(70, _("Writing favorites"))
            self.escreveFavoritos()
            self.mudaSituacao(90, _("Writing blacklist"))
            self.escreveBlacklist()   
            self.mudaSituacao(100, _("Finished"))          
           
            self.reloadList()
        else:
            self.close()
    
    def mudaSituacao(self,porcentagem,mensagem):
        self.mensagem=mensagem
        self.porcentagem=porcentagem
        self.atualizar.start(1,True)
        # self["action"].hide()
        # self["progress"].hide()
        #
        # self["action"].text = mensagem
        # self["progress"].value=porcentagem
        #
        # self["action"].show()
        # self["progress"].show()

    def atualizaProgresso(self):
        print "atualizando progresso"
        self["action"].text = self.mensagem
        self["progress"].value=self.porcentagem
        self.hide()
        self.show()

    
    def reloadList(self):
        from enigma import eDVBDB
        eDVBDB = eDVBDB.getInstance()
        self.mudaSituacao(100, _("Reloading bouquets"))      
        eDVBDB.reloadBouquets()

        
        self.fechar.start(2000, 1)
          

    def gerarBouquets(self):
            from enigma import eServiceReference, eServiceCenter, iServiceInformation
            from Components.Sources.ServiceList import ServiceList        
                    
            if self.parserules():
                
                self.satPref=config.plugins.Easy.pref.value if config.plugins.Easy.pref.value=="DVB-C" else utils.positionToSat(config.plugins.Easy.pref.value)
      
                currentServiceRef = self.session.nav.getCurrentlyPlayingServiceReference()
                servicelist = ServiceList("")
                servicelist.setRoot(currentServiceRef)
                canais = servicelist.getServicesAsList()
#                tmp=open("/tmp/teste","w")
                servicehandler = eServiceCenter.getInstance()
                for item in canais:
                    canal = eServiceReference(item[0])            
                    if canal:

                        # nome = servicehandler.info(canal).getName(canal)
                        nome = item[1].strip()

                        if nome=="(...)" or re.match("\d+",nome): continue

                        tipo=str(canal.type)

                        # tipo=item[0].split(":")[2]

                        transponder_info = servicehandler.info(canal).getInfoObject(canal, iServiceInformation.sTransponderData)

                        cabo = True if transponder_info["tuner_type"]=="DVB-C" else False

                        if cabo and nome.strip().lower().endswith("hd"):
                            tipo="25"

                        if str(tipo) in ["1","19","25"]:
                            if transponder_info["tuner_type"]=="DVB-C":
                                satName="DVB-C"
                                sat=satName
                                position=satName
                            else:
                                position = int(transponder_info["orbital_position"])

                                if position>1800:
                                    sat= str(int(((float(position)/10)-360)*10))
                                    satName= "%sW" % str(int(((float(position)/10)-360)*-1))
                                else:
                                    sat= str(int(((float(position)/10)+180)*10))
                                    satName= "%sE" % str(int(((float(position)/10)-180)*-1))


                            frequencia=str(int(transponder_info["frequency"])/1000)

                            sid = canal.toString().split(":")[3]
                            sid=str(int(sid,16))
                            #                                tmp.write("%s:%s\n"%(nome,sid))
                            bouqs=self.whichBouquets(nome,sat,frequencia,sid,tipo)
                            for bq in bouqs:
                                if config.plugins.Easy.addSat.value:
                                    self.bouquets[bq].append("%s:%s (%s)"%(item[0],nome,satName))
                                else:
                                    self.bouquets[bq].append("%s:%s"%(item[0],nome))

                            if not self.fazParte(nome, self.rulesdict["exclude"], sat, frequencia,sid,tipo):
                                tmpCanal=self.fazParteFavorito(nome, sat, frequencia,sid,tipo)
                                if tmpCanal:
                                    if not isinstance(tmpCanal, bool):
                                        if tmpCanal["order"]:
                                            indice=int(tmpCanal["order"])-1
                                            if config.plugins.Easy.addSat.value:
                                                self.favouritesTv.insert(indice , "%s:%s (%s)"%(item[0],nome,satName))
                                            else:
                                                self.favouritesTv.insert(indice , "%s:%s"%(item[0],nome))

                                            try:
                                                tmp=self.favouritesTv.pop(indice+1)
                                                self.favouritesTv.append(tmp)
                                            except:
                                                pass
                                        else:
                                            if config.plugins.Easy.addSat.value:
                                                self.favouritesTv.append("%s:%s (%s)"%(item[0],nome,satName))
                                            else:
                                                self.favouritesTv.append("%s:%s"%(item[0],nome))
                                    else:
                                        if config.plugins.Easy.addSat.value:
                                            self.favouritesTv.append("%s:%s (%s)"%(item[0],nome,satName))
                                        else:
                                            self.favouritesTv.append("%s:%s"%(item[0],nome))

                        elif tipo=="2":
                            if(position==config.plugins.Easy.pref.value):
                                self.favouritesRadio.append("%s:%s"%(item[0],nome))
                return True
            else:
#                tmp=open("/tmp/teste","w")
#                
#                for regra in self.rulesdict.itervalues():
#                    for rule in regra:
#                        tmp.write("%s - %s - %s - %s \n"%(rule["rule"],rule["sat"],rule["tp"],rule["not"]))
#                
#                tmp.close()
                return False
                
        
                  
    
    def escreveBouquets(self):
        arq_name="%s/bouquets.tv"%(utils.outdir)
        arq = open(arq_name, "w")
        arq.write("#NAME User - bouquets (TV)\n")
        arq.write("#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET \"userbouquet.favourites.tv\" ORDER BY bouquet\n")
    
        escritos={}
        for ordem in self.bouquetsOrder:
            key= ordem.keys()[0]
            if not escritos.has_key(key):
                if not key in ["blacklist","exclude","favourites"]:
                    bouquet=self.bouquets[key]
                    if len(bouquet)>0:
                        escritos[key]=True
                        arq_name="userbouquet.%s.tv"%(re.sub("\W","",key).lower())
                        arq.write("#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET \"%s\" ORDER BY bouquet\n"%arq_name)
                        self.escreveArquivo(arq_name,key, bouquet)
            
        arq.close()
        arq_name="%s/bouquets.radio"%(utils.outdir)
        arq = open(arq_name, "w")
        arq.write("#NAME User - bouquets (Radio)\n")
        arq.write("#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET \"userbouquet.favourites.radio\" ORDER BY bouquet\n")
        arq.close()
           
            
    def escreveArquivo(self,nome_arquivo,nome,canais):
        arq_name="%s/%s"%(utils.outdir,nome_arquivo)
        arq = open(arq_name, "w")
        arq.write("#NAME %s\n"%nome)
        for canal in canais:
            arq.write("#SERVICE %s\n"%canal)
        arq.close()
        
    def escreveFavoritos(self):
        arq_name="%s/userbouquet.favourites.tv"%(utils.outdir)
        arq = open(arq_name, "w")
        arq.write("#NAME Favourites (TV)\n")
        
#        self.favouritesTv.extend(self.bouquets["favourites"])
#        self.favouritesTv.sort(key=lambda x: x.split(":")[-1].strip())
        for canal in self.favouritesTv:
            arq.write("#SERVICE %s\n"%canal)
            
        arq.close() 
        arq_name="%s/userbouquet.favourites.radio"%(utils.outdir)
        arq = open(arq_name, "w")
        arq.write("#NAME Favourites (Radio)\n")
        arq.close()
        
    def escreveBlacklist(self):
        if self.bouquets.has_key("blacklist"):
            arq_name="%s/blacklist"%(utils.outdir)
            arq = open(arq_name, "w")
            
           
            blacklist=self.bouquets["blacklist"]
            for canal in blacklist:
                arq.write("#SERVICE %s\n"%canal)
                
            arq.close()
    
    def parserules(self):
#        tmp=open("/tmp/teste","w")
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
                self.rulesdict[favname]=utils.preparaRegras(channellist)
    #            tmp.write("%s - %s\n"%(favname,self.rulesdict[favname]))
                self.bouquetsOrder.append({favname:channellist})
                if favname!="exclude":
                    self.bouquets[favname]=[]
        
        if not self.rulesdict.has_key("exclude"):
            self.rulesdict["exclude"]=[]
            self.bouquetsOrder.append({"exclude":""})
            
        if not self.rulesdict.has_key("blacklist"):
            self.rulesdict["blacklist"]=[]
            self.bouquetsOrder.append({"blacklist":""})
            
        if not self.rulesdict.has_key("favourites"):
            self.rulesdict["favourites"]=[]
            self.bouquetsOrder.append({"favourites":""})
            
#        tmp.close()
        return True
    
                                    
    
    def trocaSatTp(self,canais):
        todos=canais.split(",")
        novaLinha=[]
        for canal in todos:
            novoCanal=""
            try:
                sat=re.findall("(sat\[\-?\d+\])",canal)[0]
                sat=re.findall("\-?\d+",sat)[0]
            except:
                sat=""
                
            try:
                tp=re.findall("(tp\[\d+\])",canal)[0]
                tp=re.findall("\d+",tp)[0]
            except:
                tp=""   
                
            if sat and tp:
                novoCanal="%s:%s:%s"%(sat,tp,canal.split(":")[-1])
            elif sat and not tp:
                novoCanal="%s:[TP]:%s"%(sat,canal.split(":")[-1])
            elif not sat and tp:
                novoCanal="%s:%s"%(tp,canal.split(":")[-1])
            elif not sat and not tp:
                novoCanal="[TP]:%s"%canal
            
            novaLinha.append(novoCanal)
            
        retorno=",".join(novaLinha)
        return retorno
            
    
    def whichBouquets(self,channel,sat,frequencia,sid,tipo):
        
        bouqs=[]
        exclude=self.rulesdict["exclude"]

        for key,value in self.rulesdict.items():
            if not key in ["favourites","blacklist","exclude"]:
                if not self.fazParte(channel, exclude,sat, frequencia,sid,tipo):
                    if self.fazParte(channel, value,sat, frequencia,sid,tipo):
                        bouqs.append(key)
        
        return bouqs
    
    def fazParte(self,canal,lista,sat,tp,sid,tipo):
        channel=canal.lower().strip()
#        tmp=open("/tmp/teste","a")
        check=False

        for regra in lista:
            if regra["sat"]:
                if regra["sat"]!=sat:
                    continue
            elif sat!=self.satPref:
                continue

            if regra["tp"]:
                if regra["tp"]!=tp:
                    continue

            if regra["sid"]:
                if regra["sid"]!=sid:
                    continue

            if regra["hd"]:
                if not tipo in ["19","25"]:
                    continue

            regra["rule"]=regra["rule"].lower().strip()
                                    
            retorno=False
            if regra["rule"].startswith("*") and regra["rule"].endswith("*"):
                if regra["rule"].replace("*","") in channel:
                    retorno=True
            elif regra["rule"].startswith("*"):
                if channel.endswith(regra["rule"].replace("*","")):
                    retorno=True
            elif regra["rule"].endswith("*"):
                if channel.startswith(regra["rule"].replace("*","")):
                    retorno=True
            elif regra["rule"]==channel:
                    retorno=True
#            tmp.write("%s - %s=%s-%s - %s\n"%(sat,regra["rule"],channel,regra["not"],retorno))
            if not retorno:
                continue
            
            if retorno:
                if regra["not"]:
                    continue
            
            check=True   
                      
#        tmp.close() 
        return check

    def fazParteFavorito(self,canal,sat,tp,sid,tipo):
        channel=canal.lower()
        channel=channel.strip()
        lista=self.rulesdict["favourites"]
        retorno=False
        check=False
        for regra in lista:
            
            retorno=False                        
            if regra["rule"].startswith("*") and regra["rule"].endswith("*"):
                if regra["rule"].replace("*","") in channel:
                    retorno=True
            elif regra["rule"].startswith("*"):
                if channel.endswith(regra["rule"].replace("*","")):
                    retorno=True
            elif regra["rule"].endswith("*"):
                if channel.startswith(regra["rule"].replace("*","")):
                    retorno=True
            elif regra["rule"]==channel:
                    retorno=True
            
            if retorno:
                print "%s sat(%s - %s) tp(%s - %s) sid(%s - %s)"%(canal,regra["sat"],sat,regra["tp"],tp,regra["sid"],sid)
                if regra["sat"]:
                    if regra["sat"]!=sat:
                        continue
                elif self.satPref!=sat:
                    continue
            
                if regra["tp"]:
                    if regra["tp"]!=tp:
                        continue
    
                if regra["sid"]:
                    if regra["sid"]!=sid:
                        continue  
                            
                if regra["hd"]:
                    if not tipo in ["19","25"]:
                        continue
                
                if regra["not"]:  
                    continue
                else:
                    #print "%s - %s %s"%(canal,tp,regra["tp"])
                    return regra
            elif self.satPref==sat:
                check=regra.copy()
           
        if not isinstance(check, bool):
            return check;        
        return False