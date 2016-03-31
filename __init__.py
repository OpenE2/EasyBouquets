# -*- coding: utf-8 -*-

# EasyBouquets
# Feel free to add comments and pas extra stuff You would have fitted in.
# gravatasufoca@yahoo.com.br
# Bruno Teixeira canto de Lima

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
	gettext.bindtextdomain("EasyBouquets", resolveFilename(SCOPE_PLUGINS, "Extensions/EasyBouquets/locale"))

def _(txt):
	t = gettext.dgettext("EasyBouquets", txt)
	if t == txt:
		print "[EasyBouquets] fallback to default translation for", txt
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)