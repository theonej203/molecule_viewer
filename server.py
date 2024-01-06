from http.server import HTTPServer, BaseHTTPRequestHandler

import urllib
import MolDisplay
import molecule
import molsql
import sqlite3
import os






files = {'/index.html': 'index.html', '/index.js': 'index.js', '/index.css':'index.css', '/molViewer.html': 'molViewer.html'}
contentType = {'/index.html': 'text/html', '/index.js': 'text/javascript', '/index.css':'text/css', '/molViewer.html': 'text/html'}


database = molsql.Database(reset=False)

numUnamed = 0

head = """
<!DOCTYPE html>
<html>
  <head>
    <title> Molecule Viewer </title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.3/jquery.min.js"></script>
    <script type="text/javascript" src="index.js"></script>
    <link rel="stylesheet" type="text/css" href="index.css"/>
  </head>
  <body>
    <h1 class="title"> Molecule Preview </h1>
    <ul class="nav">
      <li><a href="index.html">Home</a></li>
      <li><a href="molViewer.html">View Molecules</a></li>
    </ul>
    <br/><br/><br/><br/><br/>
"""

tail = """
    </div>
  </body>
</html>
"""


def isHex(string:str)->bool:
    for c in string:
        if( (c < '0' or c > '9') and (c < 'A' or c > 'F') ):
            return False
    
    return True



class HTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        
        if(self.path in files ):
            mainPage = open(files[self.path])
            self.send_response( 200 )
            self.send_header( "Content-type", contentType[self.path] )
            self.end_headers()
            self.wfile.write( bytes(mainPage.read(), 'utf-8'))
            mainPage.close()
            

        elif(self.path == "/getElements"):
            elements = database.getElements()
            sendString = ""
            for i in elements:
                for j in i:
                    sendString = sendString + str(j) + ','
                sendString = sendString + ';'
                
            self.send_response(200)
            self.send_header( "Content-type", "text/plain")
            self.end_headers()
            self.wfile.write( bytes(sendString, 'utf-8'))
            
        
        elif(self.path == "/getMolecules"):
            fetchedMolecules = database.getMolecules()
            sendString = ""
            for i in fetchedMolecules:
                sendString += i[0] + ';'
            
            self.send_response(200)
            self.send_header( "Content-type", "text/plain")
            self.end_headers()
            self.wfile.write( bytes(sendString, 'utf-8'))
        
        else:
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: not found", "utf-8" ) )
    
    def do_POST(self):
        
        if(self.path == "/molecule"):
            
            #get content
            length = int(self.headers['Content-Length'])
            content = self.rfile.read(length)
            content = content.decode("utf-8").split("\n")#convert byte to utf-8 string, then split it with newline
            
            
            #spaghetti to get extension of the uploaded file
            extention = content[1].split(";")[2][:-2].split(".")[-1]

            if(extention == "sdf"):
                fileName = content[0].split("-")[-1]#the header include "-" character and number, set the file name to the number
                fileName = fileName + ".sdf"
                file = open(fileName, "w")
                for i in range(4, len(content)):
                    file.write(content[i]+"\n")
                    
                file.close()#close the file to save work

                if("drop" in content[-3][:-1].lower() or "insert" in content[-3][:-1].lower() or "delete" in content[-3][:-1].lower() ):
                    message = "<h3>Invalid molecule name</h3>"
                    self.send_response(200)
                    self.send_header( "Content-type", "text/html" )
                    self.send_header( "Content-length", len(head+message+tail) )
                    self.end_headers()
                    self.wfile.write( bytes( head+message+tail , "utf-8") )
                    return

                name = content[-3][:-1]
                global numUnamed
                if(name == ""):
                    if(numUnamed == 0):
                        name = "Unamed molecule"
                    else:
                        name = "Unamed molecule " + str(numUnamed)
                    numUnamed+=1

                file = open(fileName, "r")# open the file for reading
                message = f"<p>Successfully uploaded molecule '{name}'! You can view this and all other molecules by clicking the View Molecules navigation button.</p>"
                moleculeBox = """<div class="moleculeWindow"> """


                
                try:
                    database.add_molecule(name, file)
                    database.conn.commit()
                except sqlite3.IntegrityError:
                    message = f"<p>Molecule '{name}' already exist. Below is the molecule:</p>"
                except:
                    os.remove(fileName)#remove the tempoary created file
                    message = "sdf file is either corrupt or invalid"
                    self.send_response( 200 )
                    self.send_header( "Content-type", "text/html" )
                    self.send_header( "Content-length", len(head+message+tail) )
                    self.end_headers()
                    self.wfile.write( bytes( head+message+tail , "utf-8") )
                    file.close()
                    return
                os.remove(fileName)#remove the tempoary created file

                newMolecule = database.load_mol(name)
                newMolecule.sort()
                

                #create and send svg
                svgString = newMolecule.svg()
                self.send_response( 200 )
                self.send_header( "Content-type", "text/html" )
                self.send_header( "Content-length", len(head+message+moleculeBox+svgString+tail) )
                self.end_headers()
                self.wfile.write( bytes( head+message+moleculeBox+svgString+tail , "utf-8") )
            else:
                message = "<h3>Invalid file format</h3>"
                self.send_response(200)
                self.send_header( "Content-type", "text/html" )
                self.send_header( "Content-length", len(head+message+tail) )
                self.end_headers()
                self.wfile.write( bytes( head+message+tail , "utf-8") )

        elif(self.path == "/deleteElement"):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            body = urllib.parse.parse_qs( body.decode( 'utf-8' ) )
            database.deleteElement(body['eName'][0])


            MolDisplay.radius = database.radius()
            MolDisplay.element_name = database.element_name()
            MolDisplay.header = database.radial_gradients()

            message="Delete successful"
            self.send_response( 200 ); 
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(message) )
            self.end_headers()

            self.wfile.write( bytes( message, "utf-8" ) )

        elif(self.path == "/displayMolecule"):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            body = urllib.parse.parse_qs( body.decode( 'utf-8' ) )
            
            moleculeName = body['molName'][0][1:][:-1]
            fetchedMolecule = database.load_mol(moleculeName)
            fetchedMolecule.sort()
            moleculeSvg = fetchedMolecule.svg()


            self.send_response(200)
            self.send_header( "Content-type", "text/html" )
            self.send_header( "Content-length", len(moleculeSvg) )
            self.end_headers()
            self.wfile.write( bytes( moleculeSvg , "utf-8") )

        elif(self.path == "/rotateMolecule"):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            body = urllib.parse.parse_qs( body.decode( 'utf-8' ) )
            
            message = ""
            moleculeName = body['molName'][0].split(" ")[1]
            xRotation = 360
            yRotation = 360
            zRotation = 360


            if('xRot' in body):
                try:
                    xRotation = int(body['xRot'][0])
                    if(xRotation == 0):
                        xRotation = 360
                except ValueError:
                    message = "Please enter number for x axis rotation"
            
            if('yRot' in body):
                try:
                    yRotation = int(body['yRot'][0])
                    if(yRotation == 0):
                        yRotation = 360
                except ValueError:
                    message = "Please enter number for y axis rotation"

            if('zRot' in body):
                try:
                    zRotation = int(body['zRot'][0])
                    if(zRotation == 0):
                        zRotation = 360
                except ValueError:
                    message = "Please enter number for z axis rotation"

            if(message != ""):
                self.send_response( 200 ); 
                self.send_header( "Content-type", "text/plain" )
                self.send_header( "Content-length", len(message) )
                self.end_headers()

                self.wfile.write( bytes( message, "utf-8" ) )
                return
            

            
            fetchedMolecule = database.load_mol(moleculeName)
            mx = molecule.mx_wrapper(xRotation,0,0)
            my = molecule.mx_wrapper(0,yRotation,0)
            mz = molecule.mx_wrapper(0,0,zRotation)

            fetchedMolecule.xform(mx.xform_matrix)
            fetchedMolecule.xform(my.xform_matrix)
            fetchedMolecule.xform(mz.xform_matrix)
            
            fetchedMolecule.sort()
            moleculeSvg = fetchedMolecule.svg()

            self.send_response(200)
            self.send_header( "Content-type", "text/html" )
            self.send_header( "Content-length", len(moleculeSvg) )
            self.end_headers()
            self.wfile.write( bytes( moleculeSvg , "utf-8") )

            
            
        
        
        elif(self.path == "/newElement"):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) )

            expectedField = {'eNum': "element number",
                             'eCode': "element code",
                             'eName': "element name",
                             'eCol1': "color 1",
                             'eCol2': "color 2",
                             'eCol3': "color 3",
                             'eRad': "element radius"}
            message = "Success!"
            
            valid = True
            
            for i in expectedField:
                if(i not in postvars):
                    message = "Please enter value for "+expectedField[i]
                    valid = False
                    break                

            
            if(valid):
                try:
                    eNum = int(postvars["eNum"][0])
                    eCode = postvars["eCode"][0][:3]
                    eName = postvars["eName"][0][:32]
                    eCol1 = postvars["eCol1"][0][:6]
                    eCol2 = postvars["eCol2"][0][:6]
                    eCol3 = postvars["eCol3"][0][:6]
                    eRad = int(postvars["eRad"][0])

                    print((eName,))
                    print(database.getElementsName())
                    
                    if("drop" in eName.lower() or "insert" in eName.lower() or "delete" in eName.lower() ):
                        message = "Invalid element name"
                    elif((eName,) in database.getElementsName()):
                        message = "Element already exist"
                    elif(len(eCol1) != 6 or len(eCol2) != 6 or len(eCol3) != 6):
                        message = "Please enter 6 hexadecimals in the element colors"
                    elif( not isHex(eCol1) or not isHex(eCol2) or not isHex(eCol3) ):
                        message = "Please enter only hexadecimal characters for element color"
                    elif(eRad > 999):
                        message = "Radius is too large"
                    else:
                        #database['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 )
                        database['Elements'] = (eNum, eCode, eName, eCol1, eCol2, eCol3, eRad)
                        database.conn.commit()

                except ValueError:
                    message = "Please enter only number in element number and element radius fields"
                    
            MolDisplay.radius = database.radius()
            MolDisplay.element_name = database.element_name()
            MolDisplay.header = database.radial_gradients()

            self.send_response( 200 ); # 200 or 400
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(message) )
            self.end_headers()

            self.wfile.write( bytes( message, "utf-8" ) )



              
          
if __name__ == "__main__":
    server = HTTPServer( ('localhost', 55508), HTTPRequestHandler ) #5 5508

    try:
        database.create_tables()
        database['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 )
        database['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 )
        database['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 )
        database['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 )
    except sqlite3.IntegrityError:
        pass
    finally:
        MolDisplay.radius = database.radius()
        MolDisplay.element_name = database.element_name()
        MolDisplay.header = database.radial_gradients()
            
    try:      
        server.serve_forever()
    except KeyboardInterrupt:#for ^c to exit
        server.shutdown()
        database.conn.commit()
        database.conn.close()
        


 
