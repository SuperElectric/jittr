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

using std::endl;

void parseObj(const std::string& filePath, std::vector<double>* vector_data){
    std::ifstream in(filePath);
}

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
    for (int i=0; i<12; i++){
        double noiseFactor = 1 + 2.0*2*(dis(gen) - 0.5);
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

void parseObj(const std::string& filePath, std::vector<vec3>* xyzPtr,
               std::vector<vec2>* uvPtr, std::vector<index3>* indexPtr,
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

int main(int argc, char* argv[]) {
    google::InitGoogleLogging(argv[0]);
    double camera[12] = {0,0,0,  0,0,-10.0, 1,1,0,0, 0.1,0.1};
    double cameraGuess[12];
    addNoise(camera, cameraGuess);
    int nVerts = 100;
    double* verts = new double[5*nVerts];
    calculateVerts(verts, nVerts, camera);
    jittr::solveCamera(verts, nVerts, cameraGuess);
    printCamera(cameraGuess);
    return 0;
}







