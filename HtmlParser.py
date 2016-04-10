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
				id=int(float(idx))
				if "." in idx:
					if canais.has_key(id):
						continue

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

def is_number(s):
    try:
        float(s) # for int, long and float
    except ValueError:
        try:
            complex(s) # for complex
        except ValueError:
            return False

    return True

#
# canais=getCanais("operadora.php?idO=39")
# for canal in sorted(canais) :
# 	print "%s - %s"%(canal,[canal.nome for canal in canais[canal]])
