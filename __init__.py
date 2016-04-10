# -*- coding: utf-8 -*-

# EasyBouquets
# Feel free to add comments and pas extra stuff You would have fitted in.
# gravatasufoca@yahoo.com.br
# Bruno Teixeira canto de Lima

import gettext

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

PluginLanguageDomain = "EasyBouquets"
PluginLanguagePath = "Extensions/EasyBouquets/locale"

def localeInit():
	gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))

def _(txt):
	if gettext.dgettext(PluginLanguageDomain, txt):
		return gettext.dgettext(PluginLanguageDomain, txt)
	else:
		print "[" + PluginLanguageDomain + "] fallback to default translation for " + txt
		return gettext.gettext(txt)

language.addCallback(localeInit())