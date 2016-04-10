# -*- coding: utf-8 -*-
from . import _
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import SCOPE_SKIN_IMAGE
from enigma import eServiceCenter

from Canal import Canal
from DuvidaTemplate import *


class DuvidasCanaisScreen(Screen):
	skin="""
	        <screen name="duvidas" title="" position="center,center" size="750,600">

		         <widget name="list" position="44,10" size="630,444" font="Regular;26" scrollbarMode="showOnDemand" selectionPixmap="skin_default-HD/buttons/sel.png" />
		         <ePixmap pixmap="skin_default/buttons/red.png" position="131,560" size="26,26" alphatest="on" />
		        <widget source="key_red" render="Label" position="166,560" size="220,28" backgroundColor="darkgrey" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

		        <ePixmap pixmap="skin_default/buttons/green.png" position="415,560" size="26,26" alphatest="on" />
		        <widget source="key_green" render="Label" position="450,560" size="220,28" backgroundColor="darkgrey" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

		      </screen>
			"""
	def __init__(self, session, canais):
		Screen.__init__(self, session)

		self.skin=DuvidasCanaisScreen.skin

		self.onLayoutFinish.append(self.updateList)

		self.onFirstExecBegin.append(self.mostraMensagem)

		self["Title"].text=_("Channel order doubts")

		self.list = []
		self.lista=DuvidasList(self.list)
		self["list"] = self.lista
		self.duvidasList = {}
		self.expanded = []

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))

		self["actions"] = ActionMap(["OkCancelActions","InputActions","ColorActions", "DirectionActions"],
        {
            "green": self.enviar,
            "cancel": self.fechar,
            "red": self.fechar,
            "ok":self.selecionar,
	        "back": self.fechar,
	        "left": self.left,
	        "right": self.right

        }, -2)

		self.gerados={}
		duvidas={}

		for canal in canais:
			if len(canais[canal])>1:
				duvidas[canal]=canais[canal]
			else:
				self.gerados[canal]=canais[canal]


		self.prepareList(duvidas)


	def mostraMensagem(self):
		msg=_("There are services with the same order.\nPlease, choose the right service order.")
		self.session.open(MessageBox, text = msg, type = MessageBox.TYPE_WARNING,close_on_any_key=True, timeout=5)


	def enviar(self):
		for canal in self.duvidasList:
			picon= filter(lambda p: p.selected,self.duvidasList[canal])
			if len(picon)>0:
				self.gerados[canal]=[picon[0]]

		tmp=[]
		for canal in self.gerados:
			tmp.append(self.gerados[canal][0])

		self.gerados=tmp
		self.fechar()

	def selecionar(self):
		piconSelecionado = self["list"].l.getCurrentSelection()

		if piconSelecionado is None:
			return

		piconSelecionado=piconSelecionado[0]
		if isinstance(piconSelecionado, Canal):
			check=not piconSelecionado.selected

			for picon in self.getCategory(piconSelecionado.numero):
				picon.selected=False

			piconSelecionado.selected=check

			self.updateList()


	def updateList(self):

		list = []
		expandableIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/expandable-plugins.png"))
		expandedIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/expanded-plugins.png"))
		verticallineIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/verticalline-plugins.png"))

		listsize = self["list"].instance.size()
		self.listWidth = listsize.width()
		self.listHeight = listsize.height()

		from enigma import eServiceCenter
		servicehandler = eServiceCenter.getInstance()


		for x in sorted(self.duvidasList):
			list.append(PluginCategoryComponent(x, width=self.listWidth))
			list.extend([PluginDownloadComponent(picon, self.listWidth) for picon in self.duvidasList[x]])

		self.list = list
		self["list"].l.setList(list)

	def prepareList(self,lista={}):
		for canal in lista:
			lista[canal][0].selected=True
			self.addIntoCategory(canal,lista[canal])



	def addCategory(self,categoria):
		if not self.duvidasList.has_key(categoria):
			self.duvidasList[categoria]=[]


	def getCategory(self,categoria):
		self.addCategory(categoria)
		return self.duvidasList[categoria]

	def addIntoCategory(self,categoria,item):
		self.getCategory(categoria).extend(item)


	def right(self):
		selecionado=self.lista.getSelectedIndex()+1
		if selecionado<len(self.list):

			for i in range(selecionado,len(self.list)):
				if isinstance(self.list[i][0],int):
					self.lista.moveToIndex(i)
					break

	def left(self):
		selecionado=self.lista.getSelectedIndex()-1
		if selecionado < 0: pass

		for i in range(selecionado,0,-1):
			if isinstance(self.list[i][0],int):
				self.lista.moveToIndex(i)
				break

	def fechar(self):
		self.close(self.gerados)