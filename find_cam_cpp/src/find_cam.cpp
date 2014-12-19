#include "ceres/ceres.h"
#include "ceres/rotation.h"
#include "Eigen/Dense"
#include <iostream>
#include <fstream>
#include <sstream>
#include <random>
#include <vector>
#include <unordered_map>
#include "jittr/find_cam.h"

void linearEstimateCamera(const vec5* const arrayOfVerts, int nVerts,
                          double* camera){
    using namespace Eigen;
    using namespace std;
    MatrixXf M = MatrixXf::Zero(2*nVerts, 12);
    for (int i=0; i<nVerts; i++){
        vec5 s = arrayOfVerts[i];
        int j = 2*i;        
        M(j,0)  = s.x;      M(j,1)  = s.y;
        M(j,2)  = s.z;      M(j,3)  = 1.0;
        M(j,8)  = -s.u*s.x; M(j,9)  = -s.u*s.y;
        M(j,10) = -s.u*s.z; M(j,11) = -s.u;
        j = 2*i + 1;        
        M(j,4)  = s.x;      M(j,5)  = s.y;
        M(j,6)  = s.z;      M(j,7)  = 1.0;
        M(j,8)  = -s.v*s.x; M(j,9)  = -s.v*s.y;
        M(j,10) = -s.v*s.z; M(j,11) = -s.v;
    }

    JacobiSVD<MatrixXf>svd(M, ComputeFullU | ComputeFullV);
    MatrixXf V = svd.matrixV();
    VectorXf projectMatrix = V.col(0);
    double error = (M*projectMatrix).squaredNorm();
    for (int i=1; i<12; i++){
        VectorXf p = V.col(i);
        if ((M*p).squaredNorm() < error){
            projectMatrix = p;
            error = (M*projectMatrix).squaredNorm();
        }
    }

    MatrixXf R (3,3);
    VectorXf T (3);
    MatrixXf C = MatrixXf::Zero(3,3);
    for (int i=0; i<3; i++){
        for (int j=0; j<3; j++){
            R(i,j) = projectMatrix[4*i + j];
        }
        T[i] = projectMatrix[4*i + 3];
    }
    
    C(0,0) = -1.8;
    C(1,1) = -1.3;
    C(2,2) = 1.0;
    C(0,2) = 0.5;
    C(1,2) = 0.5;
    R = C.inverse()*R;
    double scale = cbrt(R.determinant());
    R = R / scale;
    // cout << endl << R<< endl;
    T = C.inverse()*T;
    T = T / scale;
    
    double rotationMatArray [9];    
    for (int i=0; i<3; i++){
        for (int j=0; j<3; j++){
            rotationMatArray[i + 3*j] = R(i,j);
        }
    }
    
    ceres::RotationMatrixToAngleAxis(rotationMatArray, camera);
    camera[3] = T[0], camera[4] = T[1], camera[5] = T[2];
    camera[6] = C(0,0), camera[7] = C(1,1);
    camera[8] = C(0,2), camera[9] = C(1,2);
    camera[10] = camera[11] = 0; 
    
}

struct UVResidual {
    UVResidual(){}
    UVResidual(double x, double y, double z, double u, double v):
        u_(u), v_(v), x_(x), y_(y), z_(z) {}
    UVResidual(vec5 uvxyz):
        u_(uvxyz.u), v_(uvxyz.v), x_(uvxyz.x), y_(uvxyz.y), z_(uvxyz.z) {}
    template <typename T>
    bool operator() (const T* const camera, T* residuals) const {
        // camera[0,1,2] = axis angle
        // camera[3,4,5] = translation
        // camera[6,7,8,9] = uScale, vScale, u0, v0
        // camera[10,11] = K1, K2
        const T xyz[3] = {T(x_), T(y_), T(z_)};
        // let p = rotated xyz about axis camera[0,1,2], by angle |camera[0,1,2]|
        T p[3];
        ceres::AngleAxisRotatePoint(camera, xyz, p);
        // translate p by camera[3,4,5]
        p[0] += camera[3];
        p[1] += camera[4];
        p[2] += camera[5];
        // divide by p[2] and apply distortion
        p[0] = p[0]/p[2];
        p[1] = p[1]/p[2];
        T rsqrd = p[0]*p[0] + p[1]*p[1];
        p[0] = p[0] + p[0]*(camera[10]*rsqrd + camera[11]*rsqrd*rsqrd);
        p[1] = p[1] + p[1]*(camera[10]*rsqrd + camera[11]*rsqrd*rsqrd);
        // multiply by camera calibration matrix
        p[0] = p[0]*camera[6] + camera[8];
        p[1] = p[1]*camera[7] + camera[9];
    	residuals[0] = p[0] - T(u_);
	    residuals[1] = p[1] - T(v_);
        return true;
    }
    private:
    double u_, v_, x_, y_, z_;
};

void solveCamera(const vec5* const arrayOfVerts, int nVerts, double* camera){
    ceres::Problem problem;
    for (int i=0; i < nVerts; i++){
        ceres::CostFunction* function =
            new ceres::AutoDiffCostFunction<UVResidual, 2, 12>(
                new UVResidual(arrayOfVerts[i])
            );
        problem.AddResidualBlock(function, NULL, camera);
    }
    ceres::Solver::Options options;
    options.linear_solver_type = ceres::DENSE_SCHUR;
    options.minimizer_progress_to_stdout = false;
    options.num_threads = 8;
    //options.function_tolerance = 0;
    //options.gradient_tolerance = 0;
   // options.parameter_tolerance = 0;
   // options.min_trust_region_radius = 0;
    ceres::Solver::Summary summary;
    ceres::Solve(options, &problem, &summary);
    std::cout << summary.BriefReport() << "\n";
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
    for (int i=3; i<6; i++){
        double noiseFactor = 1 + 10.0*2*(dis(gen) - 0.5);
        newCamera[i] = noiseFactor*oldCamera[i];
    }
}

void printCamera(double camera[]){
    using namespace std;    
    cout << "   Rotation: "
         << camera[0] << ", " 
         << camera[1] << ", "
         << camera[2] <<  endl;
    cout << "   Location: "
         << camera[3] << ", "
         << camera[4] << ", "
         << camera[5] <<  endl;
    cout << "   Scale u,v: " << camera[6] << ", " << camera[7] << endl;
    cout << "   Offset u,v: " << camera[8] << ", " << camera[9] << endl;
    cout << "   Distortion: " << camera[10] << ", " << camera[11] << endl;
}

void parseObj(const std::string& filePath,
              std::vector<vec3>* xyzPtr,
              std::vector<vec2>* uvPtr,
              std::vector<index3>* indexPtr,
              std::unordered_map<std::string, int>* materialIDsPtr,
              std::unordered_map<int, std::string>* materialNamesPtr,
              std::string& mtlFile){
    using namespace std;
    ifstream in(filePath.c_str());
    xyzPtr->clear();
    uvPtr->clear();
    indexPtr->clear();

    unordered_map<string, int>& materialIDs = *materialIDsPtr;
    unordered_map<int, string>& materialNames = *materialNamesPtr;
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
                index3 matXyzUvIDs;
                matXyzUvIDs.materialID = materialID;
                char tempchars[1000];
                wordstream.getline(tempchars, 1000, '/');
                stringstream(tempchars) >> matXyzUvIDs.xyzID;
                wordstream.getline(tempchars, 1000, '/');
                stringstream(tempchars) >> matXyzUvIDs.uvID;
                if (matXyzUvIDs.uvID == 0){
                    matXyzUvIDs.uvID = matXyzUvIDs.xyzID;
                }
                indexPtr->push_back(matXyzUvIDs);
            }
        }

        else if (firstWord == "usemtl"){
            string material;
            strStream >> material;
            if (materialIDs.count(material) == 0){
                int nMats = materialIDs.size();
                materialIDs[material] = nMats;
                materialNames[nMats] = material;
            }
            materialID = materialIDs[material];
        }
        
        else if (firstWord == "mtllib"){
            strStream >> mtlFile;
        }
    }
}

void createUvxyzLists (const std::vector <vec3>& xyzList,
                       const std::vector <vec2>& uvList,
                       const std::vector <index3>& indexList,
                       std::vector<vec5>* arrayOfVectors){
    int uvxyzCount = indexList.size();
    vec3 xyz;
    vec2 uv;
    vec5 uvxyz;
    index3 matXyzUvIDs;
    for (int i=0; i<uvxyzCount; i++){
        matXyzUvIDs = indexList[i];
        uv = uvList[matXyzUvIDs.uvID-1];
        xyz = xyzList[matXyzUvIDs.xyzID-1];
        uvxyz.x = xyz.x; uvxyz.y = xyz.y; uvxyz.z = xyz.z;
        uvxyz.u = uv.u; uvxyz.v = uv.v;
        arrayOfVectors[matXyzUvIDs.materialID].push_back(uvxyz);
    }
}

void selectRandomVerts(const std::vector<vec5>& vectorOfVerts,
                       int nVerts,
                       vec5* arrayOfVerts){
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis (0, vectorOfVerts.size()-1);
    for (int i=0; i<nVerts; i++){
        arrayOfVerts[i] = vectorOfVerts[dis(gen)];
    }
}

std::string cameraDataToString(int indents, const double* camera,
                               std::string materialName){
    using namespace std;
    stringstream data;
    string indentString = "";
    for (int i=0; i<indents; i++){
        indentString = indentString + "    ";
    }
    data << indentString << "axisAngle: [" << camera[0] << ", "
         << indentString << camera[1] << ", " << camera[2] << "] \n"
         << indentString << "translation: [" << camera[3] << ", "
         << indentString << camera[4] << ", " << camera[5] << "] \n"
         << indentString << "scaleU : " << camera[6] << endl
         << indentString << "scaleV : " << camera[7] << endl
         << indentString << "offsetU : " << camera[8] << endl
         << indentString << "offsetV : " << camera[9] << endl
         << indentString << "K1 : " << camera[10] << endl
         << indentString << "K2 : " << camera[11] << endl;
    double col0[3], col1[3], col2[3];
    double x[3] = {1,0,0};
    double y[3] = {0,1,0};
    double z[3] = {0,0,1};
    ceres::AngleAxisRotatePoint(camera, x, col0);
    ceres::AngleAxisRotatePoint(camera, y, col1);
    ceres::AngleAxisRotatePoint(camera, z, col2);
    data << indentString << "rotationMatrix: [["
         << col0[0] << ", " << col1[0] << ", " << col2[0] << "], ["
         << col0[1] << ", " << col1[1] << ", " << col2[1] << "], ["
         << col0[2] << ", " << col1[2] << ", " << col2[2] << "]]"
         << endl;
    return data.str();
}
