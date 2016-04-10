from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN,SCOPE_ACTIVE_SKIN
from Tools.LoadPixmap import LoadPixmap
from enigma import eListboxPythonMultiContent, gFont

# selectionpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/selectioncross.png"))

selectiononpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_ACTIVE_SKIN, 'icons/lock_on.png'))
selectionoffpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_ACTIVE_SKIN, 'icons/lock_off.png'))

def PluginCategoryComponent(name, width=440):
	res= [
		name,
		MultiContentEntryText(pos=(5, 5), size=(width-80, 25), font=0, text=str(name))
	]

	return res

def PluginDownloadComponent(picon, width=440):

	res= [
		picon,
		MultiContentEntryText(pos=(80, 0), size=(width-80, 25),font=1, text=picon.nome)
	]

	if picon.selected:
		res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 40, 0, 30, 30, selectiononpng))
	else:
		res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 40, 0, 30, 30, selectionoffpng))

	return res
	

class DuvidasList(MenuList):
	def __init__(self, list, enableWrapAround=False):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		self.l.setFont(0, gFont("Regular", 26))
		self.l.setFont(1, gFont("Regular", 20))
		self.l.setItemHeight(35)

