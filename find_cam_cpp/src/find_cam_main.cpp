#include "glog/logging.h"
#include "ceres/ceres.h"
#include "ceres/rotation.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <random>
#include <vector>
#include <unordered_map>
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
        cout << "Usage: find_cam <.obj file> <material count>" << endl;        
        return 1;
    }
    if (!exists(argv[1])){
        cout << "Usage: find_cam <.obj file> <material count>" << endl;
        cout << argv[1] <<" not found." << endl;
        return 1;
    }
    
    vector <vec3> xyzList;
    vector <vec2> uvList;
    vector <index3> indexList;
    unordered_map<string, int> materialIDs;
    unordered_map<int, string> materialNames;
    string file = argv[1];
    string mtlFile;
    parseObj(file, &xyzList, &uvList, &indexList, &materialIDs, &materialNames,
             mtlFile);
    vector<vec5>* arrayOfVectors = new vector<vec5> [materialIDs.size()];
    createUvxyzLists(xyzList, uvList, indexList, arrayOfVectors);
        
    int materialIDMax;
    stringstream(argv[2]) >> materialIDMax;
    cout << endl << "Using materials 0 to " << materialIDMax-1 << endl << endl;
    if (materialIDMax == 0){
        materialIDMax = materialIDs.size();
    }
    else if (materialIDMax > materialIDs.size()){
        cout << "Material index is too high" << endl;
        return 1;
    }

    int nVerts = 10000;
    double cameraGuess[12] = {-0.06,0.05,0.02,
                              -14.5,55.0,-189.2,
                              -1.77,-1.33,0.54,0.50,
                               0.012,-0.0029};

    ofstream outputFile;
    outputFile.open(string(argv[1]) + ".yaml");
    outputFile << "mtlFile: " << mtlFile << endl << endl;

    for (int materialID=0; materialID<materialIDMax; materialID++){
        vec5* arrayOfVerts = new vec5 [nVerts];
        selectRandomVerts(arrayOfVectors[materialID], nVerts, arrayOfVerts);
        linearEstimateCamera(arrayOfVerts, 40, cameraGuess);
        cout << "Material = " << materialNames[materialID] << endl;
        cout << "  Camera estimate is: " << endl;        
        printCamera(cameraGuess);     
        solveCamera(arrayOfVerts, nVerts, cameraGuess);
        delete[] arrayOfVerts;
        cout << "  Final camera is: " << endl;
        printCamera(cameraGuess);
        cout << endl;
        outputFile << materialNames[materialID] << ":" << endl
             << cameraDataToString(1, cameraGuess, materialNames[materialID])
             << endl;
    }
    outputFile.close();

    delete[] arrayOfVectors;    

    return 0;
}







