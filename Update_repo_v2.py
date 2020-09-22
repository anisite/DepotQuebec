#!/usr/bin/env python3
# -*- coding: cp1252 -*-
# *  Modification by CB (2016)

# *  Copyright (C) 2012-2013 Garrett Brown
# *  Copyright (C) 2010      j48antialias
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# *  Based on code by j48antialias:
# *  https://anarchintosh-projects.googlecode.com/files/addons_xml_generator.py

""" addons.xml generator """
import codecs
import os
import sys
import zipfile
import hashlib
import re
baseP = os.path.dirname(os.path.abspath(__file__))+"/"

# Compatibility with 3.0, 3.1 and 3.2 not supporting u"" literals
if sys.version < '3':
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x

class Generator:
    addons_xml=""
    
    def __init__( self ):
        # generate files
        # final addons text
        log("RECHERCHE DE FICHIERS .ZIP")
        log("--------------------------")
        self.addons_xml = u("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n")
        self._generate_addons_file(baseP)
        log("--------------------------")
        
        # clean and add closing tag
        self.addons_xml = self.addons_xml.strip() + u("\n</addons>\n")
        # save file
        log("Sauvegarde du nouveau addon.xml")
        #Needed to remove .encode("utf-8") to make it work.... don't know why
        self._save_file( self.addons_xml, file=baseP+"/addons.xml" , codec= "utf-8")
        self._generate_md5_file(baseP+"addons.xml")
        
        # notify user
        log("Finished updating addons xml and md5 files")
    
    def _generate_addons_file( self , basePath ):
        # addon list
        addons = os.listdir( basePath+"." )
        most_recent_file = ""
        versionMostRecent = self.getVersion("")
        #log(addons)

        # loop thru and add each addons addon.xml file
        for addon in addons:
            fullPath = basePath + addon
            #log(fullPath)
            _path=""
            #try:
            # skip any file or .svn folder or .git folder
            if (fullPath.endswith(".zip")):
                #log("ZIP FILE : " + fullPath)
                self._generate_md5_file(fullPath)
                thisVersion = self.getVersion(fullPath)
                self.scanZip(fullPath)

            elif ( not os.path.isdir(fullPath ) or addon == ".svn" or addon == ".git" ):
               # log("Je rejete " + addon)
               pass
            elif (os.path.isdir(fullPath)):
               # log(fullPath + " Est un path")
                self._generate_addons_file(fullPath+"/")

            #except Exception as e:
                # missing or poorly formatted addon.xml
                #log("Excluding %s for %s" % ( _path, e ))
                #pass

    def scanZip(self,path):
        log("---")
        log("   --Most recent : " + path)
        log("---")
        zf = zipfile.ZipFile(path)
        datas = zf.infolist()
        #log(datas)
        for data in datas:
            filen = data.filename
            if (filen.endswith("/addon.xml")):
                self.__addToAddonXML(zf.open(data,'r'))
            elif (filen.endswith("/icon.png")):
                zf.extract(data)
            elif (filen.endswith("/fanart.jpg")):
                zf.extract(data)
            elif (filen.endswith("/changelog.txt")):
                zf.extract(data)
    def getVersion(self,filename):
        try:
            versionStr= filename[filename.rfind('-')+1:filename.rfind('.')]
            m = re.match('(?P<_0>.+)\.(?P<_1>.+)\.(?P<_2>.+)', versionStr)
            mdict = m.groupdict()
            return [mdict['_0'],mdict['_1'],mdict['_2']]

        except Exception:
            return ['0','0','0']
    def isRecent(self, thisVersion, versionMostRecent):
        return (versionMostRecent[0] < thisVersion[0] or \
                    (versionMostRecent[0] == thisVersion[0] and versionMostRecent[1] < thisVersion[1]) or \
                    (versionMostRecent[0] == thisVersion[0] and versionMostRecent[1] == thisVersion[1] and versionMostRecent[2] < thisVersion[2])) 

    def __addToAddonXML(self, data):
        read = data.read().decode("utf-8") 
        xml_lines = read.splitlines()
        log(read)
        # new addon
        addon_xml = ""
        # loop thru cleaning each line
        for line in xml_lines:
            # skip encoding format line
            if ( line.find( "<?xml" ) >= 0 ): continue
            # add line
            if sys.version < '3':
                addon_xml += unicode( line.rstrip() + "\n", "UTF-8" )
            else:
                addon_xml += line.rstrip() + "\n"
        # we succeeded so add to our final addons.xml text
        self.addons_xml += addon_xml.rstrip() + "\n\n"
        
    
    def _generate_md5_file( self,filename ):
        # create a new md5 hash
        m = hashlib.md5( open( filename, "rb" ).read() ).hexdigest()
        log("MD5 of " + filename + " : " + m)
        # save file
        try:
            self._save_file( m, file=filename+".md5" )
        except Exception as e:
            # oops
            log("An error occurred creating " + filename + ".md5 file!\n%s" % e)
    
    def _save_file( self, data, file ,codec=None):
        try:
            # write data to the file (use b for Python 3)
            #removed b.... don't know why
            if codec==None:
                open( file, "w" ).write( data )
            else:
                codecs.open( file,"w",encoding=codec ).write( data )
        except Exception as e:
            # oops
            log("An error occurred saving %s file!\n%s" % ( file, e ))

def log(arg):
    print(arg)

if ( __name__ == "__main__" ):
    # start
    Generator()
