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

//void outputFile(std::string materialName){
//    
//}

int main(int argc, char* argv[]) {
    using namespace std;
    vector <vec3> xyzList;
    vector <vec2> uvList;
    vector <index3> indexList;
    map<string, int> materialIDs;
    string file = "/home/daniel/urop/jittr/jittr/assets/models/mouse/mouse.obj";
    parseObj(file, &xyzList, &uvList, &indexList, &materialIDs);
    vector<vec5>* arrayOfVectors = new vector<vec5> [materialIDs.size()];
    createUvxyzLists(xyzList, uvList, indexList, arrayOfVectors);
    int nVerts = 1000;
    int material = 3;
    vec5* arrayOfVerts = new vec5 [nVerts];
    selectRandomVerts(arrayOfVectors[material], nVerts, arrayOfVerts);
    double cameraGuess[12] = {-0.06,0.05,0.02,
                              -14.5,55.0,-189.2,
                              -1.77,-1.33,0.54,0.50,
                               0.012,-0.0029};
    solveCamera(arrayOfVerts, nVerts, cameraGuess);
    printCamera(cameraGuess);
    return 0;
}







