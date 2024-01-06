import os
import sqlite3
import MolDisplay
import molecule
from MolDisplay import Molecule, Atom, Bond

class Database:

    def __init__( self, reset=False ):
        if(reset):
            if(os.path.exists("molecules.db")):
                os.remove("molecules.db")
        
        self.conn = sqlite3.connect("molecules.db")
            
    def create_tables(self):
        tableList = self.conn.execute("""SELECT name FROM sqlite_master WHERE type='table';""").fetchall()
        #above returns a list of tuples, need to create a tuple containing the table name to compare to
        
        

        if( ("Elements",) not in tableList):
            #print("new elements")
            self.conn.execute("""
                                    CREATE TABLE Elements(
                                        ELEMENT_NO    INTEGER       NOT NULL,
                                        ELEMENT_CODE  VARCHAR(3)    PRIMARY KEY NOT NULL,
                                        ELEMENT_NAME  VARCHAR(32)   NOT NULL,
                                        COLOUR1       CHAR(6)       NOT NULL,
                                        COLOUR2       CHAR(6)       NOT NULL,
                                        COLOUR3       CHAR(6)       NOT NULL,
                                        RADIUS        DECIMAL(3)    NOT NULL
                                    );
                            """)
            
        if( ("Atoms",) not in tableList):
            #print("new atoms")
            self.conn.execute("""
                                CREATE TABLE Atoms(
                                    ATOM_ID        INTEGER          PRIMARY KEY   AUTOINCREMENT  NOT NULL,
                                    ELEMENT_CODE   VARCHAR(3)       NOT NULL,
                                    X              DECIMAL(7,4)     NOT NULL,
                                    Y              DECIMAL(7,4)     NOT NULL,
                                    Z              DECIMAL(7,4)     NOT NULL,
                                    FOREIGN KEY    (ELEMENT_CODE)   REFERENCES  Elements(ELEMENT_CODE)
                                );
                            """)
        
        if( ("Bonds",) not in tableList):
            #print("new bonds")
            self.conn.execute("""
                                CREATE TABLE Bonds(
                                    BOND_ID  INTEGER  PRIMARY KEY  AUTOINCREMENT  NOT NULL,
                                    A1       INTEGER  NOT NULL,
                                    A2       INTEGER  NOT NULL,
                                    EPAIRS   INTEGER  NOT NULL
                                );
                            """)
        
        if( ("Molecules",) not in tableList):
            #print("new molecules")
            self.conn.execute("""
                                CREATE TABLE Molecules(
                                    MOLECULE_ID   INTEGER   PRIMARY KEY     AUTOINCREMENT   NOT NULL,
                                    NAME          TEXT      NOT NULL        UNIQUE
                                );
                            """)

        if( ("MoleculeAtom",) not in tableList):   
            #print("new mnol atom") 
            self.conn.execute("""
                                CREATE TABLE MoleculeAtom(
                                    MOLECULE_ID   INTEGER           NOT NULL,
                                    ATOM_ID       INTEGER           NOT NULL,
                                    PRIMARY KEY   (MOLECULE_ID, ATOM_ID),
                                    FOREIGN KEY   (MOLECULE_ID)     REFERENCES   Molecules(MOLECULE_ID),
                                    FOREIGN KEY   (ATOM_ID)         REFERENCES   Atoms(ATOM_ID)
                                );
                            """)

        if( ("MoleculeBond",) not in tableList): 
            #print("new molbond")   
            self.conn.execute("""
                                CREATE TABLE MoleculeBond(
                                    MOLECULE_ID   INTEGER           NOT NULL,
                                    BOND_ID       INTEGER           NOT NULL,
                                    PRIMARY KEY   (MOLECULE_ID, BOND_ID),
                                    FOREIGN KEY   (MOLECULE_ID)     REFERENCES   Molecules(MOLECULE_ID),
                                    FOREIGN KEY   (BOND_ID)         REFERENCES   Atoms(BOND_ID)
                                );
                            """)
            
    def __setitem__( self, table, values ):
        tableList = self.conn.execute(f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'""").fetchall()

        if(tableList == []):
            raise Exception(f"Table '{table}' does not exist in conn")
        else:
            self.conn.execute(f"""INSERT INTO {table}
                                    VALUES {values};""")
            
    def add_atom( self, molname:str, atom:Atom ):
        self.conn.execute(f"""INSERT INTO Atoms(ELEMENT_CODE, X, Y, Z)
                                    VALUES ('{atom.atom.element}', {atom.atom.x}, {atom.atom.y}, {atom.z})""")
        
        '''
        atomID = self.conn.execute(f"""SELECT ATOM_ID FROM Atoms
                                            WHERE (Atoms.ELEMENT_CODE = '{atom.atom.element}' 
                                                    AND Atoms.X = '{atom.atom.x}'
                                                    AND Atoms.Y = '{atom.atom.y}'
                                                    AND Atoms.Z = '{atom.z}')
                                    """).fetchone()
        '''
        atomID = self.conn.execute("SELECT last_insert_rowid()").fetchone()

        moleculeID = self.conn.execute(f"""SELECT MOLECULE_ID FROM Molecules
                                            WHERE (Molecules.NAME == '{molname}')
                                        """).fetchone()
        
        self.conn.execute(f"""INSERT INTO MoleculeAtom(MOLECULE_ID, ATOM_ID)
                                VALUES ({moleculeID[0]}, {atomID[0]})""")
        

    def add_bond( self, molname:str, bond:Bond ):

        self.conn.execute(f"""INSERT INTO Bonds(A1, A2, EPAIRS)
                                    VALUES ('{bond.bond.a1}', {bond.bond.a2}, {bond.bond.epairs})""")
        
        '''
        bondID = self.conn.execute(f"""SELECT BOND_ID FROM Bonds
                                            WHERE (Bonds.A1 = {bond.bond.a1}
                                                    AND Bonds.A2 = {bond.bond.a2}
                                                    AND Bonds.EPAIRS = {bond.bond.epairs})
                                    """).fetchone()
        '''
        bondID = self.conn.execute("SELECT last_insert_rowid()").fetchone()

        moleculeID = self.conn.execute(f"""SELECT MOLECULE_ID FROM Molecules
                                            WHERE (Molecules.NAME == '{molname}')
                                        """).fetchone()
        
        self.conn.execute(f"""INSERT INTO MoleculeBond(MOLECULE_ID, BOND_ID)
                                VALUES ({moleculeID[0]}, {bondID[0]})""")
        

    def add_molecule( self, name, fp ):
        newMolecule:Molecule = Molecule()
        newMolecule.parse(fp)

        self.conn.execute(f"""INSERT INTO Molecules (NAME)
                                VALUES ('{name}');""")
        
        for i in range(newMolecule.atom_no):
            tempAtom:Atom = Atom(newMolecule.get_atom(i))
            self.add_atom(name, tempAtom)
            
        for i in range(newMolecule.bond_no):
            tempBond:Bond = Bond(newMolecule.get_bond(i))
            self.add_bond(name, tempBond)
        
        
    def load_mol( self, name )->Molecule:
        newMolecule: Molecule = Molecule()
        atomList = self.conn.execute(f"""SELECT ELEMENT_CODE, X, Y, Z FROM Molecules, MoleculeAtom, Atoms
                                            WHERE (Molecules.MOLECULE_ID=MoleculeAtom.MOLECULE_ID
                                                    AND Molecules.NAME='{name}'
                                                    AND MoleculeAtom.ATOM_ID=Atoms.ATOM_ID) """).fetchall()
        for i in atomList:
            newMolecule.append_atom(i[0], i[1], i[2], i[3])

        bondList = self.conn.execute(f"""SELECT A1, A2, EPAIRS FROM Molecules, MoleculeBond, Bonds
                                            WHERE(
                                                Molecules.MOLECULE_ID=MoleculeBond.MOLECULE_ID
                                                AND Molecules.NAME = '{name}'
                                                AND MoleculeBond.BOND_ID=Bonds.BOND_ID
                                            )""").fetchall()
        
        for i in bondList:
            newMolecule.append_bond(i[0], i[1], i[2])
        
        return newMolecule
    
    def getMolecules( self ):
        return(self.conn.execute("SELECT NAME FROM Molecules").fetchall())
    
    
    def getElements( self ):
        return(self.conn.execute("SELECT * FROM Elements").fetchall())

    def getElementsName( self ):
        return(self.conn.execute("SELECT ELEMENT_NAME FROM Elements").fetchall())
    
    def deleteElement( self, elementName ):
        self.conn.execute(f"DELETE FROM Elements WHERE ELEMENT_NAME='{elementName}'")

    
    def radius( self ):
        radiusList = self.conn.execute("SELECT ELEMENT_CODE, RADIUS FROM Elements").fetchall()
        tempRadiusTuple = {}
        for i in radiusList:
            tempRadiusTuple[i[0]] = i[1]
        return(tempRadiusTuple)

    def element_name( self ):
        elementList = self.conn.execute("SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements").fetchall()
        tempElementTuple = {}
        for i in elementList:
            tempElementTuple[i[0]] = i[1]
        return(tempElementTuple)

    def radial_gradients( self ):
        colorList = self.conn.execute("SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements").fetchall()
        tempGradientString = ""

        for i in colorList:
            tempGradientString = tempGradientString + """<radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">\n"""%(i[0])
            tempGradientString = tempGradientString +   """\t<stop offset="0%%" stop-color="#%s"/>\n"""%(i[1])
            tempGradientString = tempGradientString +   """\t<stop offset="50%%" stop-color="#%s"/>\n"""%(i[2])
            tempGradientString = tempGradientString +   """\t<stop offset="100%%" stop-color="#%s"/>\n"""%(i[3])
            tempGradientString = tempGradientString + """</radialGradient>\n"""
            
        return(tempGradientString)

        


    


    