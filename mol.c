#include "mol.h"


//info -> atom
void atomset(atom *atom, char element[3] , double *x, double *y, double *z ){
    for(int i = 0; i<3; i++){
        atom->element[i] = element[i];
    }
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}


//atom -> info
void atomget(atom *atom, char element[3] , double *x , double *y , double *z ){
    
    
    for(int i = 0; i<3; i++){
        element[i] = atom->element[i];
    }
    
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}


//info -> bond
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ){
    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->epairs = *epairs;
}

//bond -> info
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ){
    *a1 = bond->a1;
    *a2 = bond->a2;
    *epairs = bond->epairs;
}

void compute_coords( bond *bond ){
    bond->x1 = bond->atoms[bond->a1].x;
    bond->y1 = bond->atoms[bond->a1].y;

    bond->x2 = bond->atoms[bond->a2].x;
    bond->y2 = bond->atoms[bond->a2].y;

    bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z)/2;
    bond->len = sqrt( pow(bond->x2 - bond->x1,2) + pow(bond->y2 - bond->y1,2) );

    bond->dx = (bond->x2 - bond->x1 )/bond->len;
    bond->dy = (bond->y2 - bond->y1 )/bond->len;
}

int bond_comp( const void *a, const void *b ){//only here because the assignment specified
    bond *bond1 = (bond*)a;
    bond *bond2 = (bond*)b;
    return bond1->z - bond2->z;
}


//set atom and bond # to 0, malloc space for bond and atom array
molecule *molmalloc(unsigned short atom_max, unsigned short bond_max  ){
    molecule* newMolecule = malloc(sizeof(molecule));

    newMolecule->atom_max = atom_max;
    newMolecule->atom_no = 0;
    newMolecule->atoms = calloc(atom_max,sizeof(atom));
    newMolecule->atom_ptrs = calloc(atom_max,sizeof(atom*));

    newMolecule->bond_max = bond_max;
    newMolecule->bond_no = 0;
    newMolecule->bonds = calloc(bond_max, sizeof(bond));
    newMolecule->bond_ptrs = calloc(bond_max, sizeof(bond*));

    return newMolecule;
}


//make a new molecule that has the properties of src
molecule *molcopy(molecule *src ){
    molecule *newMolecule = molmalloc(src->atom_max, src->bond_max);//malloc the bond and atom array
    
    
    //create a new atom and
    //use molappend_atom to add atom
    for(int i = 0; i< src->atom_no; i++){
        atom newAtom;
        
        double newX, newY, newZ;
        char newName[3];

        atomget(src->atom_ptrs[i], newName, &newX, &newY, &newZ);
        atomset(&newAtom, src->atoms[i].element, &newX, &newY, &newZ);
        molappend_atom(newMolecule, &newAtom);
        
    }
    
    
    //same as atom
    for(int i = 0; i< src->bond_no; i++){
        bond newBond;
        unsigned short newA1, newA2;
        unsigned char newEpairs;
        bondget(&(src->bonds[i]),&newA1, &newA2, &(src->atoms), &newEpairs);
        bondset(&(src->bonds[i]),&newA1, &newA2, &(src->atoms), &newEpairs);
        molappend_bond(newMolecule, &newBond);
    }

    
    return newMolecule;
}

//free the molecule ptr
void molfree( molecule *ptr ){
    free(ptr->atom_ptrs);
    free(ptr->atoms);
    free(ptr->bond_ptrs);
    free(ptr->bonds);
    free(ptr);

}



//add atom to molecule
void molappend_atom( molecule *molecule, atom *atom ){
    if(molecule->atom_max == molecule->atom_no){
        if(molecule->atom_max == 0){//expand max array to one
            molecule->atom_max = 1;
            molecule->atoms = realloc(molecule->atoms,sizeof(struct atom)*1);
            molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom *)*1);
        }else{//double the max atom
            molecule->atom_max *= 2;
            molecule->atoms = realloc(molecule->atoms,sizeof(struct atom)*molecule->atom_max);
            molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom *)*molecule->atom_max);

            for(int i = 0; i< molecule->atom_no; i++){//repoint each atom_ptrs to atom
                molecule->atom_ptrs[i] = &(molecule->atoms[i]);
            }
        }
    }
    
    molecule->atoms[molecule->atom_no] = *atom;//add the atoms
    molecule->atom_ptrs[molecule->atom_no] = &(molecule->atoms[molecule->atom_no]);//add pointer of atom
    molecule->atom_no = molecule->atom_no + 1;
}


void molappend_bond( molecule *molecule, bond *bond ){
    if(molecule->bond_max == molecule->bond_no){
        if(molecule->bond_max == 0){
            molecule->bond_max = 1;
            molecule->bonds = realloc(molecule->bonds, sizeof(struct bond)*1);
            molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*)*1);
        }else{
            molecule->bond_max *=2;
            molecule->bonds = realloc(molecule->bonds, sizeof(struct bond)*molecule->bond_max);
            molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*)*molecule->bond_max);

            for(int i = 0; i< molecule->bond_no; i++){//repoint each atom_ptrs to atom
                molecule->bond_ptrs[i] = &(molecule->bonds[i]);
            }
        }
    }

    molecule->bonds[molecule->bond_no] = *bond;
    molecule->bond_ptrs[molecule->bond_no] = &(molecule->bonds[molecule->bond_no]);
    molecule->bond_no = molecule->bond_no + 1;


}


int atomPartition(atom **list, int start, int end){
    double pivot = list[end]->z;
    int i = start;
    for(int j = start; j<end; j++){
        if( list[j]->z < pivot){
            atom* temp = list[i];
            list[i] = list[j];
            list[j] = temp;
            i++;
        }
    }
    atom* temp = list[i];
    list[i] = list[end];
    list[end] = temp;
    return i;
}

int bondPartition(bond **list, int start, int end){
    double pivot = list[end]->z;
    int i = start;
    for(int j = start; j< end; j++){
        if( list[j]->z< pivot){
            bond* temp = list[i];
            list[i] = list[j];
            list[j] = temp;
            i++;
        }
    }
    bond* temp = list[i];
    list[i] = list[end];
    list[end] = temp;
    return i;
}


void quickSort(void **list, int start, int end, int type){
    
    if(start < end ){
        int middle = start;
        if(type == 0){
            middle = atomPartition((atom **)list, start, end);
        }else if(type == 1){
            middle = bondPartition((bond **)list, start, end);
        }     
        quickSort(list, start, middle-1, type);
        quickSort(list, middle+1, end, type);
    }
}


//arrange from lowest z value to highest z value for both of the arrays
void molsort( molecule *molecule ){

    quickSort((void**)molecule->atom_ptrs, 0, molecule->atom_no-1, 0);
    quickSort((void**)molecule->bond_ptrs, 0, molecule->bond_no-1, 1);

}


//rotate matrix by deg degree along the x axis
void xrotation( xform_matrix xform_matrix, unsigned short deg ){
    /*
    1   0    0 
    0  cos -sin
    0  sin  cos
    */
    double rad = deg* 3.14159265359/180;
    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = -sin(rad);
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(rad);
    xform_matrix[2][2] = cos(rad);
}

//rotate on y axis
void yrotation( xform_matrix xform_matrix, unsigned short deg ){
    /*
    cos  0  sin 
    0    1    0
    -sin 0  cos
    */
    double rad = deg* 3.14159265359/180;
    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(rad);
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = -sin(rad);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(rad);
}

//rotate on z axis
void zrotation( xform_matrix xform_matrix, unsigned short deg ){
    /*
    cos -sin  0
    sin  cos  0
    0     0   1
    */
    double rad = deg* 3.14159265359/180;
    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = -sin(rad);
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = sin(rad);
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}


void mol_xform( molecule *molecule, xform_matrix matrix ){
    /*
    x = [0][0]x + [0][1]y + [0][2]z
    y = [1][0]x + [1][1]y + [1][2]z
    z = [2][0]x + [2][1]y + [2][2]z
    */

    for(int i = 0; i< molecule->atom_no; i++){
        double tempX, tempY, tempZ;

        tempX = matrix[0][0]*molecule->atoms[i].x 
                            + matrix[0][1]*molecule->atoms[i].y
                            + matrix[0][2]*molecule->atoms[i].z;

        tempY = matrix[1][0]*molecule->atoms[i].x 
                            + matrix[1][1]*molecule->atoms[i].y
                            + matrix[1][2]*molecule->atoms[i].z; 
        
        tempZ = matrix[2][0]*molecule->atoms[i].x 
                            + matrix[2][1]*molecule->atoms[i].y
                            + matrix[2][2]*molecule->atoms[i].z; 
        
        molecule->atoms[i].x = tempX;
        molecule->atoms[i].y = tempY;
        molecule->atoms[i].z = tempZ;
        
    }
    for(int i = 0; i<molecule->bond_no; i++){
        compute_coords(&(molecule->bonds[i]));
    }
    
}

