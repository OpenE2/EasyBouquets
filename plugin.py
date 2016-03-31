# EasyBouquets
# Feel free to add comments and pas extra stuff You would have fitted in.
# gravatasufoca@yahoo.com.br
# Bruno Teixeira canto de Lima   
from . import _
from Plugins.Plugin import PluginDescriptor
from easybouquets import EasyBouquetScreen
import utils

    
# Function main
def main(session, **kwargs):
    session.open(EasyBouquetScreen)


# Plugin descriptor, name, icon, etc.
def Plugins(**kwargs):
    return [
        PluginDescriptor(where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main, icon="plugin.png", name=utils.easybouquet_title, description="Create favorites bouquets easily by adding rules"),
        PluginDescriptor(where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main, icon="plugin.png", name=utils.easybouquet_title, description="Create favorites bouquets easily by adding rules")

      ]
