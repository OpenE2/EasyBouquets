# EasyBouquets
# Feel free to add comments and pas extra stuff You would have fitted in.
# gravatasufoca@yahoo.com.br
# Bruno Teixeira canto de Lima
from . import _
import os

from Components.Sources.StaticText import StaticText
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigSelection, \
	ConfigYesNo
from Components.ConfigList import ConfigList, ConfigListScreen
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox

from ProvidersScreen import ProvidersScreen
import utils
from loading import LoadingScreen
from help import HelpScreen
from bouquetsList import BouquetsList
from enigma import eConsoleAppContainer
from Screens.Console import Console


config.plugins.Easy = ConfigSubsection()
config.plugins.Easy.pref = ConfigSelection(choices=[])
config.plugins.Easy.addSat = ConfigYesNo(default=False)
config.plugins.Easy.ordenar = ConfigYesNo(default=False)


# Class EasyBouquetScreen
class EasyBouquetScreen(ConfigListScreen, Screen):
	skin = """
	    <screen name="bouquet" title="" position="center,center" size="736,250">

	        <ePixmap pixmap="$PLUGINDIR$/buttons/red.png" position="15,210" size="126,26" alphatest="on" />
	        <widget source="key_red" render="Label" position="47,210" size="269,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

	        <ePixmap pixmap="$PLUGINDIR$/buttons/green.png" position="230,210" size="126,26" alphatest="on" />
	        <widget source="key_green" render="Label" position="264,210" size="268,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular;24" halign="left" />

	        <ePixmap pixmap="$PLUGINDIR$/buttons/yellow.png" position="457,211" size="126,26" alphatest="on" />
	        <widget source="key_yellow" render="Label" position="498,210" size="224,28" backgroundColor="#A9A9A9" zPosition="2" transparent="1" foregroundColor="grey" font="Regular; 24" halign="left" />

	        <widget name="config" position="16,14" size="708,90" scrollbarMode="showOnDemand" font="Regular;24" />
	        <widget source="status" render="Label" position="16,145" zPosition="10" size="708,55" halign="center" valign="center" font="Regular;20" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
	        <widget source="provider" render="Label" position="336,98" size="387,26"  zPosition="10"  halign="right" valign="center" font="Regular;20" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
	    </screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.skin = EasyBouquetScreen.skin.replace("$PLUGINDIR$", utils.easybouquet_plugindir)

		self.onFirstExecBegin.append(self.verificarVersao)

		try:
			self.configuracoes = utils.getConfiguracoes()
			self.versao=self.configuracoes["versao"]
		except:
			self.versao = utils.easybouquet_version

		# self.skinName = [ "Setup" ]
		self.list = []
		self["config"] = ConfigList(self.list)

		self.sats = utils.obterSatelites()

		config.plugins.Easy.pref.setChoices(self.sats)

		self.list.append(getConfigListEntry(_("Preferential Satellite"), config.plugins.Easy.pref))
		self.list.append(getConfigListEntry(_("Add satellite name"), config.plugins.Easy.addSat))
		self.list.append(getConfigListEntry(_("Ordered by provider"), config.plugins.Easy.ordenar))

		ConfigListScreen.__init__(self, self.list)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Create"))
		self["key_yellow"] = StaticText(_("Rules"))
		self["status"] = StaticText(_("The \"Favourites (Tv)\" bouquet will be created based on the \"Preferential Satellite\" chosen."))
		self["provider"]= StaticText()

		self["actions"] = ActionMap(["OkCancelActions", "InputActions", "ColorActions", "DirectionActions"],
		                            {
			                            "green": self.confirma,
			                            "red": self.cancel,
			                            "cancel": self.cancel,
			                            "ok": self.confirma,
			                            "yellow": self.abrirListaBouquets
		                            }, -2)

		self.setTitle("%s-%s by %s" % (utils.easybouquet_title, utils.easybouquet_version, utils.easybouquet_developer))

		config.plugins.Easy.ordenar.addNotifier(self.abrirProviders,initial_call=False,immediate_feedback=True)
		self.provider=None
		self.gerados=[]


	def abrirProviders(self,elemento):
		if elemento:
			if config.plugins.Easy.pref.value != "DVB-C":
				if elemento.value:
					self.session.openWithCallback(self.selecaoCallback, ProvidersScreen, config.plugins.Easy.pref.value)
				else:
					self.provider=None
					self["provider"].text=""
			else:
				if elemento.value:
					self.provider="DVB-C"
					self["provider"].text="DVB-C"
				else:
					self.provider=None
					self["provider"].text=""

	def selecaoCallback(self,provider,gerados):
		if provider is None:
			config.plugins.Easy.ordenar.value=False
			self["provider"].text
			self.gerados=None
			return

		self.gerados=gerados
		self.provider=provider
		self["provider"].text=provider[0]


	def verificarVersao(self):
		if float(self.versao) > float(utils.easybouquet_version):
			self.session.openWithCallback(self.atualizarVersao, MessageBox,
			                              _("There is a new version avaiable!\nDo you want to update it?"),
			                              MessageBox.TYPE_YESNO)

	def atualizarVersao(self, answer):
		if answer:
			self.container = eConsoleAppContainer()
			import urllib
			try:
				testfile = urllib.URLopener()
				testfile.retrieve(self.configuracoes["url"], "/tmp/easyBouquets.ipk")

				if os.path.isfile('/usr/bin/opkg'):
					self.ipkg = '/usr/bin/opkg'
					self.ipkg_install = self.ipkg + ' install'
					self.ipkg_remove = self.ipkg + ' remove --autoremove'
				else:
					self.ipkg = 'ipkg'
					self.ipkg_install = 'ipkg install -force-defaults'
					self.ipkg_remove = self.ipkg + ' remove'

				self.session.openWithCallback(self.chamarReiniciar, Console, cmdlist = [self.ipkg_install + " /tmp/easyBouquets.ipk"], closeOnSuccess = True)

			except:
				self.session.open(MessageBox,
				                  text="Was not possible to download the new version!\nTry again later, maybe it will be working...",
				                  type=MessageBox.TYPE_WARNING, close_on_any_key=True, timeout=10)


	def chamarReiniciar(self):
		self.session.openWithCallback(self.reiniciar, MessageBox,
				                              _("You must restart GUI for the update to take effect!\nOk?"),
				                              MessageBox.TYPE_YESNO)
	def reiniciar(self, answer):
		if answer:
			from Screens.Standby import TryQuitMainloop
			self.session.open(TryQuitMainloop, 3)

	def abrirListaBouquets(self):
		self.session.open(BouquetsList)

	def cancel(self):
		for i in self["config"].list:
			i[1].cancel()
		self.close(False)

	def confirma(self):
		self.session.openWithCallback(self.showLoading, MessageBox, _(
			"All your current favorites will be deleted!\nDo you confirm the creating of the new ones?"),
		                              MessageBox.TYPE_YESNO)

	def showLoading(self, answer):
		if answer:
			self.session.open(LoadingScreen,self.gerados)

	def mostraAjuda(self):
		self.session.open(HelpScreen)
