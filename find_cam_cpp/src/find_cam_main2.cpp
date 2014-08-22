#include "glog/logging.h"
//include "gflags/gflags.h"
#include "ceres/ceres.h"
#include "ceres/rotation.h"
#include "jittr/find_cam.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <random>
#include <vector>
#include <map>

//DEFINE_string(objFile, "", ".obj file");

using std::endl;

void calculateVerts(double* verts, int nVerts, const double* const camera){    
    double xyz[3];
    double p[3];
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis (0,1);
    for(int i=0; i<nVerts; i++){
        xyz[0] = verts[5*i] = dis(gen);
        xyz[1] = verts[5*i+1] = dis(gen);
        xyz[2] = verts[5*i+2] = dis(gen);        
        ceres::AngleAxisRotatePoint(camera, xyz, p);
        p[0] += camera[3]; p[1]+= camera[4]; p[2]+= camera[5];
        verts[5*i+3] = p[0]*camera[6]/p[2] + camera[8];
        verts[5*i+4] = p[1]*camera[7]/p[2] + camera[9];
    }
}

void addNoise(const double* const oldCamera, double* newCamera){
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis (0,1);
    for (int i=3; i<6; i++){
        double noiseFactor = 1 + 10.0*2*(dis(gen) - 0.5);
        newCamera[i] = noiseFactor*oldCamera[i];
    }
}

void printCamera(double camera[]){
    std::cout << "rotation: "
    << camera[0] << ", " 
    << camera[1] << ", "
    << camera[2] <<  endl;
    std::cout << "location: "
    << camera[3] << ", "
    << camera[4] << ", "
    << camera[5] <<  endl;
    std::cout << "scale u,v: " << camera[6] << ", " << camera[7] << endl;
    std::cout << "offset u,v: " << camera[8] << ", " << camera[9] << endl;
    std::cout << "Distortion: " << camera[10] << ", " << camera[11] << endl;
}

void parseObj(const std::string& filePath,
              std::vector<vec3>* xyzPtr,
              std::vector<vec2>* uvPtr,
              std::vector<index3>* indexPtr,
              std::map<std::string, int>* materialsPtr){
    using namespace std;
    ifstream in(filePath.c_str());
    xyzPtr->clear();
    uvPtr->clear();
    indexPtr->clear();

    map<string, int>& materialIDs = *materialsPtr;
    int materialID = 0;

    while (in.good()){

        char line[1000];
        in.getline(line, 1000);
        stringstream strStream(line);
        string firstWord;
        strStream >> firstWord;

        if (firstWord == "v"){
            vec3 xyz;
            strStream >> xyz.x;
            strStream >> xyz.y;
            strStream >> xyz.z;
            xyzPtr->push_back(xyz);
        }

        else if (firstWord == "vt"){
            vec2 uv;
            strStream >> uv.u;
            strStream >> uv.v;
            uvPtr->push_back(uv);
        }

        else if (firstWord == "f"){
            string word;
            while (strStream.good()){
                strStream >> word;
                stringstream wordstream(word);
                index3 mvvt;
                mvvt.mid = materialID;
                char tempchars[1000];
                wordstream.getline(tempchars, 1000, '/');
                stringstream(tempchars) >> mvvt.vid;
                wordstream.getline(tempchars, 1000, '/');
                stringstream(tempchars) >> mvvt.vtid;
                if (mvvt.vtid == 0){
                    mvvt.vtid = mvvt.vid;
                }
                indexPtr->push_back(mvvt);
            }
        }

        else if (firstWord == "usemtl"){
            string material;
            strStream >> material;
            if (materialIDs.count(material) == 0){
                int nMats = materialIDs.size();
                materialIDs[material] = nMats;
            }
            materialID = materialIDs[material];
        }
    }
}

void createUvxyzLists (const std::vector <vec3>& xyzList, const std::vector <vec2>& uvList,
                       const std::vector <index3>& indexList,
                       std::vector<vec5>* const arrayOfVectors){
    int uvxyzCount = indexList.size();
    vec3 xyz;
    vec2 uv;
    vec5 uvxyz;
    index3 mvvt;
    for (int i=0; i<uvxyzCount; i++){
        mvvt = indexList[i];
        uv = uvList[mvvt.vtid-1];
        xyz = xyzList[mvvt.vid-1];
        uvxyz.x = xyz.x; uvxyz.y = xyz.y; uvxyz.z = xyz.z;
        uvxyz.u = uv.u; uvxyz.v = uv.v;
        arrayOfVectors[mvvt.mid].push_back(uvxyz);
    }
}

void selectRandomVerts(const std::vector<vec5>& vectorOfVerts,
                       int nVerts,
                       vec5*const arrayOfVerts){
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis (0, vectorOfVerts.size()-1);
    for (int i=0; i<nVerts; i++){
        arrayOfVerts[i] = vectorOfVerts[dis(gen)];
    }
}




int main(int argc, char* argv[]) {
    //google::InitGoogleLogging(argv[0]);
    //double camera[12] = {0,0,0,  0,0,-10.0, 1,1,0,0, 0.1,0.1};
    //double cameraGuess[12];
    //addNoise(camera, cameraGuess);
    //int nVerts = 100;
    //double* verts = new double[5*nVerts];
    //calculateVerts(verts, nVerts, camera);
    //jittr::solveCamera(verts, nVerts, cameraGuess);
    
    using namespace std;
    //google::ParseCommandLineFlags(&argc, &argv, true);
    vector <vec3> xyzList;
    vector <vec2> uvList;
    vector <index3> indexList;
    map<string, int> materialIDs;
   // string file = FLAGS_objFile;
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
    jittr::solveCamera(arrayOfVerts, nVerts, cameraGuess);
    printCamera(cameraGuess);
    return 0;
}







