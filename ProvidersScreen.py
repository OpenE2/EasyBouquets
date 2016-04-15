# EasyBouquets
# Feel free to add comments and pas extra stuff You would have fitted in.
# gravatasufoca@yahoo.com.br
# Bruno Teixeira canto de Lima
from . import _
from Components.ActionMap import ActionMap
from Components.SelectionList import SelectionList
from Components.Sources.StaticText import StaticText
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from enigma import eTimer

import HtmlParser as parser
import utils
from duvidasList import DuvidasCanaisScreen


class ProvidersScreen(Screen):

	skin = """
	    <screen name="providers" title="" position="center,center" size="750,600">
	        <ePixmap pixmap="$PLUGINDIR$/buttons/red.png" position="15,560" size="26,26" alphatest="on" />
	        <widget source="key_red" render="Label" position="43,560" size="180,26" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

	        <ePixmap pixmap="$PLUGINDIR$/buttons/green.png" position="230,560" size="26,26" alphatest="on" />
	        <widget source="key_green" render="Label" position="261,560" size="220,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

	        <widget source="tituloLabel" render="Label" position="55,12" size="640,60"  zPosition="10"  halign="center" valign="center" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
	        <widget transparent="1" name="menu" position="55,90" size="640,493" scrollbarMode="showOnDemand" render="Listbox" itemHeight="30" font="Regular;24"/>
	    </screen>"""

	def __init__(self, session, position):
		self.skin=ProvidersScreen.skin.replace("$PLUGINDIR$", utils.easybouquet_plugindir)
		Screen.__init__(self, session)
		self["Title"].text = _("Providers List")
		self["tituloLabel"] = StaticText(_("Loading options..."))
		self.onFirstExecBegin.append(self.loading)
		self.menuList = []

		self["menu"] = SelectionList(self.menuList, enableWrapAround=True)
		self["key_red"] =  StaticText(_("Cancel"))
		self["key_green"] =  StaticText(_("Ok"))
		self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"],
		                            {
			                            "ok":self.ok,
		                                "cancel": self.cancel,
		                                "back": self.cancel,
		                                "red": self.cancel,
		                                "green": self.go
		                            }, -1)
		self.selecionado=None
		self.configuracoes=None


	def loading(self):
		self["tituloLabel"].text = _("Loading options...")
		self.configuracoes=utils.getConfiguracoes()
		self.timer=eTimer()
		self.timer.callback.append(self.getOpcoes)
		self.timer.start(1000,True)


	def getOpcoes(self):
		self.menuList=parser.getOpcoes()
		if not self.menuList:
			self.session.open(MessageBox, text = _("There was a problem to access the %s!")%parser._urlPadrao, type = MessageBox.TYPE_ERROR,close_on_any_key=True, timeout=5)
			self.cancel()
		else:
			self.clearSelection()

			self.timerMsg=eTimer()
			self.timerMsg.callback.append(self.trocaMensagem)
			self.timerMsg.start(100,True)

	def trocaMensagem(self):
		self["tituloLabel"].text = _("Those options was gotten from %s")%(parser._urlPadrao)

	def clearSelection(self):
		self["menu"].setList([])
		i=0
		for item in self.menuList:
			if item[0].lower() in self.configuracoes["arquivos"].keys():
				self["menu"].addSelection(item[0], item[1], i, selected = False)
				i+=1


	def ok(self):
		idx=self["menu"].getSelectedIndex()
		self.selecionar(idx)

	def selecionar(self,idx):
		self.clearSelection()
		self["menu"].moveToIndex(idx)
		self["menu"].toggleSelection()

	def go(self):
		selecionados=self["menu"].getSelectionsList()
		if len(selecionados)>0:
			returnValue = selecionados[0]
			if returnValue is not None:
				self.selecionado=(returnValue[0],returnValue[1])

				self.tTimer=eTimer()
				self.tTimer.callback.append(self.getNumbers)
				self.tTimer.start(10,True)
		else:
			self.session.open(MessageBox, text = _("Choose one!"), type = MessageBox.TYPE_WARNING,close_on_any_key=True, timeout=5)


	def getNumbers(self):
		self["tituloLabel"].text = _("Getting services numbers...")

		numeros=parser.getCanais(self.selecionado)
		if not numeros:
			self.session.open(MessageBox, text = _("There was a problem to access the %s!")%parser._urlPadrao+"/"+self.selecionado[1], type = MessageBox.TYPE_ERROR,close_on_any_key=True, timeout=5)
			self.cancel()
		else:
			self.session.openWithCallback(self.selecaoCallback, DuvidasCanaisScreen, numeros)


	def selecaoCallback(self,gerados):
		if gerados is None: return
		self.close(self.selecionado,gerados)

	def cancel(self):
		self.close(None,None)
