
from Canal import Canal
from pyquery import PyQuery as pq


_urlPadrao="http://www.lineup-br.com"


def getOpcoes():
	try:
		itens=[]
		d = pq(url=_urlPadrao)
		opcoes=d("#menu").find("a").filter(lambda i: pq(this).text() == 'Operadoras').parent().find("ul:eq(0)").find("a").filter(lambda i: pq(this).text() == 'DTH').parent().find("li").items()
		for i in opcoes:
			itens.append((i.text().replace("- ",""), i.find("a").attr("href")))
		return itens
	except:
		return False


def getCanais(sat):
	try:
		print "acessando: %s"%(_urlPadrao+"/"+sat[1])
		nomes=parseMapa(sat[0])
		print "fez o parse!"
		d = pq(url=_urlPadrao+"/"+sat[1])
		opcoes= d("table.fixo").eq(1).find("tr").items()

		canais={}
		for i in opcoes:
			nome=i.find("td").eq(1).find("a").eq(0).text().strip()
			if not i.find("td").eq(2).find("img[src*='hd']") and not i.find("td").eq(2).find("img[src*='sd']"): continue

			# if nome.lower()=="sound!": continue

			idx= i.find("td").eq(0).text().strip()
			if is_number(idx):
				id=int(float(idx))
				if "." in idx:
					if canais.has_key(id):
						continue
				if not canais.has_key(id):
					canais[id]=[]

				hd=False
				if i.find("td").eq(2).find("img[src*='hd']"):
					hd=True
				if nomes.has_key((nome.lower(),hd)):
					# print "%s - %s"%(nome,nomes[(nome.lower(),hd)]	)
					tmp=nomes[(nome.lower(),hd)]
					if tmp:
						nome=tmp

				if not Canal(id,nome,hd=hd) in canais[id]:
					canais[id].append(Canal(id,nome,hd=hd))
		return (canais)
	except Exception, e:
		print str(e)
		return False


def parseMapa(sat):
	import utils,os
	sat=sat.lower()
	print "entrei aqui %s"%(sat)
	arquivos=utils.getConfiguracoes()["arquivos"]
	versao=arquivos[sat][0]
	print arquivos
	arqNome=arquivos[sat][1].split("/")[-1]
	print arqNome

	atualiza=True
	if not os.path.exists(utils.etcDir+"/"+arqNome):
		import urllib
		try:
			testfile = urllib.URLopener()
			testfile.retrieve(rquivos[sat][1], utils.etcDir+"/"+arqNome)
			atualiza=False
		except Exception,e:
			print str(e)
			return {}

	arq=open(utils.etcDir+"/"+arqNome)
	versaoArq=int(arq.read(2)[-1])

	if atualiza and versaoArq < int(versao):
		import urllib
		try:
			testfile = urllib.URLopener()
			testfile.retrieve(arquivos[sat][1], utils.etcDir+"/"+arqNome)
		except Exception,e:
			print str(e)
			pass

	arq=open(utils.etcDir+"/"+arqNome)

	canais={}
	for linha in arq.readlines():
		if linha.startswith("#") or linha.strip()=="": continue

		canal,equivalente=linha.partition("=")[::2]
		hd=True if equivalente.split(";")[0]=="True" else False
		equivalente=equivalente.split(";")[1]
		equivalente=equivalente.strip()
		print canal.encode('utf-8').lower()
		canais[(canal.encode('utf-8').lower(),hd)]=equivalente.encode('utf-8')

	return canais



def is_number(s):
    try:
        float(s) # for int, long and float
    except ValueError:
        try:
            complex(s) # for complex
        except ValueError:
            return False

    return True


def getCanais2(sat):
	try:
		print "acessando: %s"%(_urlPadrao+"/"+sat)
		d = pq(url=_urlPadrao+"/"+sat)
		opcoes= d("table.fixo").eq(1).find("tr").items()

		canais={}
		for i in opcoes:
			nome=i.find("td").eq(1).find("a").eq(0).text().strip()
			if not i.find("td").eq(2).find("img[src*='hd']") and not i.find("td").eq(2).find("img[src*='sd']"): continue

			# if nome.lower()=="sound!": continue

			idx= i.find("td").eq(0).text().strip()
			if is_number(idx):
				id=idx
				if not canais.has_key(id):
					canais[id]=[]
				if not Canal(id,nome) in canais[id]:
					hd=False
					if i.find("td").eq(2).find("img[src*='hd']"):
						hd=True
					canais[id].append(Canal(id,nome,hd=hd))
		return (canais)
	except:
		return False



def parseMapa2(sat):
	import os
	sat=sat.lower()
	print "entrei aqui %s"%(sat)
	versao=getConfiguracoes()["versaoArquivo"]
	arquivos=getConfiguracoes()["arquivos"]
	print arquivos
	arqNome=arquivos[sat].split("/")[-1]
	print arqNome

	atualiza=True
	if not os.path.exists(arqNome):
		import urllib
		try:
			testfile = urllib.URLopener()
			testfile.retrieve(arquivos[sat], arqNome)
			atualiza=False
		except:
			return {}

	arq=open(arqNome)
	versaoArq=int(arq.read(2)[-1])

	print "%s - %s"%(versao,versaoArq)
	if atualiza and versaoArq < int(versao):
		import urllib
		try:
			testfile = urllib.URLopener()
			testfile.retrieve(arquivos[sat], arqNome)
		except:
			pass

	arq=open( arqNome)

	canais={}
	for linha in arq.readlines():
		if linha.startswith("#"): continue

		canal,equivalente=linha.partition("=")[::2]
		hd=True if equivalente.split(";")[0]=="True" else False
		equivalente=equivalente.split(";")[1]
		equivalente=equivalente.strip()

		canais[(canal.lower(),hd)]=equivalente.lower()

	for canal in canais:
		print canal
	return canais

def getConfiguracoes():
    import urllib, ConfigParser

    testfile = urllib.URLopener()
    testfile.retrieve("https://dl.dropboxusercontent.com/u/12772101/easyBouquets/versao.conf", "/tmp/versao.conf")

    config = ConfigParser.RawConfigParser()
    config.read('/tmp/versao.conf')

    items= config.items("arquivos")
    t={}
    for item in items:
        t[item[0]]=item[1]

    return {"versao": config.get("versao", "versao"), "url": config.get("url", "ipk"),
            "provedores": config.get("provedores", "provedores").lower().split(","),
            "arquivos": t, "versaoArquivo": config.get("versao", "arquivos")}



# parseMapa2("sky")

# canais=getCanais2("operadora.php?idO=33")
# t=open("canais2.csv","w")
# from sets import Set
# ctmp=Set()
# for canal in sorted(canais):
# 	for c in canais[canal]:
# 		ctmp.add("%s,%s\n"%(c.nome,str(c.hd)))
#
# for c in ctmp:
# 	t.write(c)