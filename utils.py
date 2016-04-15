# EasyBouquets
# Feel free to add comments and pas extra stuff You would have fitted in.
# gravatasufoca@yahoo.com.br
# Bruno Teixeira canto de Lima
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_CONFIG, SCOPE_SYSETC

rules = resolveFilename(SCOPE_SYSETC, "easybouquets/rules.conf")
rulestmp = resolveFilename(SCOPE_SYSETC, "easybouquets/rules_tmp.conf")

etcDir= resolveFilename(SCOPE_SYSETC, "easybouquets")


easybouquet_version = "2.5"
easybouquet_plugindir = resolveFilename(SCOPE_PLUGINS, "Extensions/EasyBouquets")
easybouquet_title = "EasyBouquets"
easybouquet_developer = "gravatasufoca"
outdir = resolveFilename(SCOPE_CONFIG, "")
_urlConfiguracoes="https://dl.dropboxusercontent.com/u/12772101/easyBouquets/versao.conf"
_marker="1:832:1:0:0:0:0:0:0:0::"


def removeoldfiles():
    import glob,os
    userbouquets = glob.glob(outdir + '/userbouquet.*')
    for userbouquet in userbouquets:
        os.remove(userbouquet)

    bouquetindexes = glob.glob(outdir + '/bouquets.*')
    for bouquetindex in bouquetindexes:
        os.remove(bouquetindex)
        

def preparaRegras(canais):
    import re
    
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
            
        hd=re.findall("(hd\[.+\])",regra)
        if len(hd)>0:
            if re.findall("True|False",hd[0])[0] =="True":
                hd=True
            else:
                hd=False
        else:
            hd=False

        # ordem=re.findall("(order\[\d+\])",regra)
        # if len(ordem)>0:
        #     ordem=re.findall("\d+",ordem[0])[0]
        # else:
        #     ordem=""
            
        rule=regra.split(":")[-1].lower()
        negado=rule.startswith("!")
        if negado:
            rule=rule.replace("!","",1)
        novasRegras.append({"sat":sat.strip(),"tp":tp.strip(),"sid":sid.strip(),"rule":rule.strip(),"not":negado,"hd":hd})
        
    return novasRegras  


def obterRegras(favorito):
    filerules = open(rules)
    for rule in filerules:
        rule = rule.replace('\n','')
        rule=rule.strip()
        if rule:
            favname,channellist=rule.partition("=")[::2]
            favname = favname.strip()
            
            if favname==favorito:
                filerules.close()
                return preparaRegras(channellist)
    
    filerules.close()    
    return []   


def obterRegrasString(favorito):
    filerules = open(rules)
    for rule in filerules:
        rule = rule.replace('\n','')
        rule=rule.strip()
        if rule:
            favname,channellist=rule.partition("=")[::2]
            favname = favname.strip()
            
            if favname==favorito:
                filerules.close()
                return channellist
    
    filerules.close()    
    return "" 

def removerRegra(regra,regras):
    tmp=[]
    for rule in regras:
        if rule!=regra:
            tmp.append(rule)
    
    return tmp

        
def gerarChannellist(regras):
    channellist=[]
    for rule in regras:
        regra=rule["rule"]
        negado=rule["not"]
        sat=rule["sat"]
        tp=rule["tp"]
        sid=rule["sid"]
        hd=rule["hd"]
        # ordem=rule["order"]
     
        tmpregra={
                   "not":negado,
                   "sat":sat,
                   "tp":tp,
                   "sid":sid,
                   "rule":regra,
                   "hd":hd
                   # "order":ordem
              }
    
        channellist.append(addRule(tmpregra))
    
    return ",".join(channellist)

def addRule(regra):
    novaLinha=regra["rule"]
    
    negado=regra["not"]
    sat=regra["sat"]
    tp=regra["tp"]
    sid=regra["sid"]  
    hd=regra["hd"]  
    # ordem=regra["order"]

    if negado:
        novaLinha="!%s"%(novaLinha) 
        
    if sid:
        novaLinha="sid[%s]:%s"%(sid,novaLinha)

    if tp:
        novaLinha="tp[%s]:%s"%(tp,novaLinha)

    if sat:
        novaLinha="sat[%s]:%s"%(sat,novaLinha)
    
    if hd:
        novaLinha="hd[%s]:%s"%(hd,novaLinha)
        
    # if ordem:
    #     novaLinha="order[%s]:%s"%(ordem,novaLinha)
    
    return novaLinha


def obterSatelites():
    from Components.NimManager import nimmanager
    nimmanager.readTransponders()
    satConfigureds = nimmanager.getConfiguredSats()
    sats=[]
    for sat in satConfigureds:
        print sat
        nome=nimmanager.getSatName(sat)
                
        sats.append((sat,nome))


    if nimmanager.hasNimType("DVB-C"):
        sats.append(("DVB-C","DVB-C"))
    return sats


def obterTransponder(sat):
    from Components.NimManager import nimmanager
    tmp=[]
    
    tps = nimmanager.getTransponders(sat)
    for tp in tps:        
        freq=tp[1]
        freq=str(int(freq)/1000)
        tmp.append((freq,freq))
    
    return tmp
        

def satToPosition(sat):
    import math
    position=3600-math.fabs(float(sat))
#    if float(sat)%10>0:
#        position+=1
    return (int(position))  

def positionToSat(position):
    if position:
        if position>1800:
            sat= str(int(((float(position)/10)-360)*10))
        else:
            sat= str(int(((float(position)/10)+180)*10))   
            
        return sat
    return ""


def getConfiguracoes():
    import urllib, ConfigParser

    testfile = urllib.URLopener()
    testfile.retrieve(_urlConfiguracoes, "/tmp/versao.conf")

    config = ConfigParser.RawConfigParser()
    config.read('/tmp/versao.conf')

    items= config.items("arquivos")
    t={}
    for item in items:
        t[item[0]]=item[1]

    return {"versao": config.get("versao", "versao"), "url": config.get("url", "ipk"),
            "arquivos": t, "versaoArquivo": config.get("versao", "arquivos")}

def is_number(s):
    try:
        float(s) # for int, long and float
    except ValueError:
        try:
            complex(s) # for complex
        except ValueError:
            return False

    return True


def removerAcentos(input_str):
	from unicodedata import normalize
	return normalize('NFKD', input_str.decode("UTF-8")).encode('ASCII', 'ignore')


def isHd(ref):
    return ref.split(":")[2] in ["19","25"]

def ordenarCanais(canais,sat,gerados=[]):
    if sat=="DVB-C":
        canais.sort(key=lambda x: int(x.split(":")[3],16))
        tmp={}
        for canal in canais:
           sid= int(canal.split(":")[3],16)
           tmp[sid]=canal

        last= int(canais[-1].split(":")[3],16)

    else:
        tmpCanais=list(canais)
        tmpRepetidos=[]
        # seta os valores da ordenacao

        for canal in gerados:
            i=0
            for service in canais:
                # if "brasilia" in removerAcentos(canal.nome) and "brasilia" in removerAcentos(service.split(":")[-1]).lower():
                #     print "%s - %s - %s"%(removerAcentos(canal.nome),removerAcentos(service.split(":")[-1]).lower(),removerAcentos(canal.nome) == removerAcentos(service.split(":")[-1]).lower())

                if removerAcentos(canal.nome) == removerAcentos(service.split(":")[-1]).lower():
                    # if "brasilia" in removerAcentos(canal.nome) and "brasilia" in removerAcentos(service.split(":")[-1]).lower():
                    #     print "sim %s - %s"%(canal.hd,isHd(service))
                    if canal.hd != isHd(service):
                        continue

                    # if "brasilia" in removerAcentos(canal.nome) and "brasilia" in removerAcentos(service.split(":")[-1]).lower():
                    #     print service+"|"+str(canal.numero)

                    if "|" in tmpCanais[i]:
                        tmpRepetidos.append(service+"|"+str(canal.numero))
                    else:
                        tmpCanais[i]=service+"|"+str(canal.numero)
                i+=1

        tmpCanais.extend(tmpRepetidos)
        canais=[canal if "|" in canal else canal+"|0" for canal in tmpCanais]

        canais.sort(key=lambda x: int(x.split("|")[1]))
        tmp={}
        for canal in canais:
            sid= int(canal.split("|")[1])
            tmp[sid]=canal

        last= int(canais[-1].split("|")[1])

    novaLista=[]
    for i in range(1,last):
        if tmp.has_key(i):
            novaLista.append(tmp[i] if "|" not in tmp[i] else tmp[i].split("|")[0])
        else:
            novaLista.append(_marker)

    return novaLista

