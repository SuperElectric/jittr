#include "glog/logging.h"
#include "ceres/ceres.h"
#include "ceres/rotation.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <random>
#include <vector>
#include <map>
#include "jittr/find_cam.h"

using namespace std;

bool exists (const std::string& name) {
    ifstream f(name.c_str());
    if (f.good()) {
        f.close();
        return true;
    } else {
        f.close();
        return false;
    }   
}

int main(int argc, char* argv[]) {

    if (argc != 3){
        cout << "Invalid arguments" << endl;        
        return 1;
    }
    if (!exists(argv[1])){
        cout << "Obj file does not exist" << endl;
        return 1;
    }
    
    vector <vec3> xyzList;
    vector <vec2> uvList;
    vector <index3> indexList;
    map<string, int> materialIDs;
    map<int, string> materialNames;
    string file = argv[1];
    parseObj(file, &xyzList, &uvList, &indexList, &materialIDs, &materialNames);
    vector<vec5>* arrayOfVectors = new vector<vec5> [materialIDs.size()];
    createUvxyzLists(xyzList, uvList, indexList, arrayOfVectors);
        
    int materialID;
    stringstream(argv[2]) >> materialID;
    cout << "material = " << materialID;
    if (materialID >= materialIDs.size()){
        cout << "Material index is too high" << endl;
        return 1;
    }

    int nVerts = 1000;
    vec5* arrayOfVerts = new vec5 [nVerts];
    selectRandomVerts(arrayOfVectors[materialID], nVerts, arrayOfVerts);
    double cameraGuess[12] = {-0.06,0.05,0.02,
                              -14.5,55.0,-189.2,
                              -1.77,-1.33,0.54,0.50,
                               0.012,-0.0029};
    solveCamera(arrayOfVerts, nVerts, cameraGuess);
    printCamera(cameraGuess);
    outputFile(cameraGuess, materialNames[materialID]);
<<<<<<< HEAD

        vec5 uvxyz = arrayOfVectors[materialID][100];
        vec3 xyz;
        vec2 uvNew, uvOld;
        xyz.x = uvxyz.x; xyz.y = uvxyz.y; xyz.z = uvxyz.z;
        uvOld.u = uvxyz.u; uvOld.v = uvxyz.v;
        uvNew = xyzToUv(cameraGuess, xyz);
        cout << endl << "uvOld = "<< uvOld.u << ","<< uvOld.v << endl;
        cout << endl << "uvNew = "<< uvNew.u << ","<< uvNew.v << endl;
        
=======
    vec5 uvxyz = arrayOfVectors[materialID][100];
    cout << uvxyz.u << endl << uvxyz.v << endl << uvxyz.x << endl << uvxyz.y << endl << uvxyz.z << endl;
>>>>>>> ebe970b6a3755388d340d429e108a7dec4c1d6ae
    return 0;
}







