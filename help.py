# EasyBouquets
# Feel free to add comments and pas extra stuff You would have fitted in.
# gravatasufoca@yahoo.com.br
# Bruno Teixeira canto de Lima
from . import _
from enigma import getDesktop
from Screens.Screen import Screen
from Components.ActionMap import NumberActionMap

from Components.Label import Label

class HelpScreen(Screen):
    width=getDesktop(0).size().width()
    heigth=getDesktop(0).size().height()
    skin = """<screen position="center,center" size="%s,%s" title="EasyBouquet - %s">
                <widget name="about" position="10,10" size="%s,%s" font="Regular;23" />                                            
            </screen>"""%(width-70,heigth-80, _("Help"),width-120,heigth-100)
            

    def __init__(self, session):
        self.skin = HelpScreen.skin
        self.session = session
        Screen.__init__(self, session)

        self["about"] = Label(_("The rules file is at /etc/easyBouquet/rules.conf. You can open it using a text editor and edit it.\nThe rule syntax is simple like this:\n\tNews=CNN,Deutsche Welle\nIt will create the bouquet \"News\" and add \"CNN\", and \"Deutsche Welle\" services in it.\nA more complex rule could be made like this:\n\tNews=CNN*,!CNNi,*News*\nIt means that every service which the name begins with \"CNN\" and IS NOT \"CNNi\" and every service that have the word \"News\" in it will be added in the \"News\" bouquet.\nYou can also specify the satellite that the service should be used:\n\tNew=-610:CNN,-431:*News*,Deutsche Welle\nIt will include the CNN service from the -610 satellite and every service that have the word \"News\", and finally the \"Deutsche Welle\" service from the preferential satellite.\n\nThere are 3 reserved rules:\n\texclude: All the rules here will exclude the services to be added on the bouquets.\n\tfavourites: It will include the services in its bouquet based on its rules.\n\t\tAll the services from the Preferential Satellite will be added in the Favourites (Tv) bouquet, except the excluded ones.\n\tblacklist: Will add the parentol control for the services based on the blacklist rules."))
        
        self["actions"] = NumberActionMap(["WizardActions", "InputActions"],
        {
        "back": self.close
        }, -1)