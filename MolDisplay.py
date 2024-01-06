from io import TextIOWrapper
import molecule


radius ={}
element_name =  {}


svgHeader = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">\n
<radialGradient id="default" cx="-50%" cy="-50%" r="220%" fx="20%" fy="20%">\n
\t<stop offset="0%" stop-color="#FFFFFF"/>\n
\t<stop offset="50%" stop-color="#050505"/>\n
\t<stop offset="100%" stop-color="#020202"/>\n
</radialGradient>\n"""
header = """"""




footer = """</svg>"""

offsetx = 500
offsety = 500

class Atom:

    def __init__(self, c_atom:molecule.atom):
        self.atom = c_atom
        self.z = c_atom.z
        
    def __str__(self)-> str:
        atomPoint = (self.atom.x*100+offsetx, self.atom.y*100+offsety)
        return(f"{self.atom.element} {atomPoint} {self.z}")
    
    def svg(self) -> str:
        rad = 50
        eName = "default"
        if(self.atom.element in radius):
            rad = radius[self.atom.element]
        if(self.atom.element in element_name):
            eName = element_name[self.atom.element]
        return('  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n'
                    %(
                        self.atom.x*100.0 + offsetx, 
                        self.atom.y*100.0 + offsety,
                        rad, 
                        eName
                    )
                )

class Bond:

    def __init__(self, c_bond:molecule.bond):
        self.bond = c_bond
        self.z = c_bond.z

    def __str__(self) -> str:
        atom1Point = (self.bond.x1*100.0 + offsetx, self.bond.y1*100.0 + offsety)
        atom2Point = (self.bond.x2*100.0 + offsetx, self.bond.y2*100.0 + offsety)

        return(f"\natom1: {atom1Point} atom2: {atom2Point}\nlength: {self.bond.len} z: {self.bond.z}\ndx: {self.bond.dx*10} dy: {self.bond.dy*10}\n")

    def svg(self) -> str:

        atom1Point = (self.bond.x1*100.0 + offsetx, self.bond.y1*100.0 + offsety)
        atom2Point = (self.bond.x2*100.0 + offsetx, self.bond.y2*100.0 + offsety)

        xsign = -1#use to figure out the orientation for the bond
        ysign = -1
        if(atom1Point[0] > atom2Point[0] ):
            ysign = 1

        if(atom1Point[1] < atom2Point[1]):
            xsign = 1
        
        
    
        return('  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n'
                %(
                    atom1Point[0] - xsign*abs(self.bond.dy)*10.0, atom1Point[1] - ysign*abs(self.bond.dx)*10.0,
                    atom1Point[0] + xsign*abs(self.bond.dy)*10.0, atom1Point[1] + ysign*abs(self.bond.dx)*10.0,
                    atom2Point[0] + xsign*abs(self.bond.dy)*10.0, atom2Point[1] + ysign*abs(self.bond.dx)*10.0,
                    atom2Point[0] - xsign*abs(self.bond.dy)*10.0, atom2Point[1] - ysign*abs(self.bond.dx)*10.0
                )
            )

class Molecule(molecule.molecule):

    def __str__(self) -> str:
        string = f"\n---------\nNumber of atoms: {self.atom_no}\nNumber of bonds: {self.bond_no}\nList of atoms:\n\n"
        
        for i in range(self.atom_no):
            string += Atom(self.get_atom(i)).__str__()
            string += "\n"

        string += "\nList of bonds\n"
        for i in range(self.bond_no):
            string += Bond(self.get_bond(i)).__str__()
            string += "\n"
        string += "\n---------\n"
        return(string)

    def svg(self) -> str:
        svgString = svgHeader + header
        i=0
        j=0
        while(i<self.atom_no and j<self.bond_no):
            if(self.get_atom(i).z < self.get_bond(j).z):
                tempAtom = Atom(self.get_atom(i))
                svgString = svgString + tempAtom.svg()
                i += 1
            else:
                tempBond = Bond(self.get_bond(j))
                svgString = svgString + tempBond.svg()
                j += 1
                #print(f"atom1: {tempBond.bond.x1},{tempBond.bond.y1}    atom2: {tempBond.bond.x2},{tempBond.bond.y2} ")
            
        
        while(i<self.atom_no):
            tempAtom = Atom(self.get_atom(i))
            svgString = svgString + tempAtom.svg()
            i += 1
        
        while(j<self.bond_no):
            tempBond = Bond(self.get_bond(j))
            svgString = svgString + tempBond.svg()
            j += 1
            #print(f"atom1: {tempBond.bond.x1},{tempBond.bond.y1}    atom2: {tempBond.bond.x2},{tempBond.bond.y2} ")

        svgString = svgString + footer
        return svgString

    def parse(self, file:TextIOWrapper):
        line = file.readline()#skip 
        line = file.readline()#three
        line = file.readline()#lines

        line = file.readline()#read the line that contains the number of atoms and number of bonds
        numAtom = int(line.split()[0])
        numBond = int(line.split()[1])

        #read atom, then read bond
        for i in range(numAtom):
            line = file.readline()
            x = float(line.split()[0])
            y = float(line.split()[1])
            z = float(line.split()[2])
            elementName = line.split()[3]
            self.append_atom(elementName,x,y,z)
        
        for i in range(numBond):
            line = file.readline()
            atom1 = int(line.split()[0])
            atom2 = int(line.split()[1])
            ePairs = int(line.split()[2]) 
            self.append_bond( atom1-1, atom2-1, ePairs)


if __name__ == "__main__":
    file = open("CID_31260.sdf", "r")
    mol = Molecule()
    mol.parse(file)
    
    mol.sort()
    print(mol)
    string = mol.svg()
    
    
    writeFile = open("water.svg", "w")
    
    writeFile.write(string)
    writeFile.close()
        

