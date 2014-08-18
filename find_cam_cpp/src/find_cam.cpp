#include "glog/logging.h"
#include "ceres/ceres.h"
#include "ceres/rotation.h"
#include <iostream>
#include <random>

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
    for (int i=0; i<12; i++){
        double noiseFactor = 1 + 1.0*2*(dis(gen) - 0.5);
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

struct UVResidual {
    UVResidual(){}
    UVResidual(double x, double y, double z, double u, double v):
        x(x), y(y), z(z), u(u), v(v) {}
    template <typename T>
    bool operator() (const T* const camera, T* residuals) const {
        // camera[0,1,2] = axis angle
        // camera[3,4,5] = translation
        // camera[6,7,8,9] = uScale, vScale, u0, v0
        // camera[10,11] = K1, K2
        const T xyz[3] = {T(x), T(y), T(z)};
        // let p = rotated xyz about axis camera[0,1,2], by angle |camera[0,1,2]|
        T p[3];
        ceres::AngleAxisRotatePoint(camera, xyz, p);
        // translate p by camera[3,4,5]
        p[0] += camera[3]; p[1]+= camera[4]; p[2]+= camera[5];
        // multiply p by calibration matrix and divide by p[2]
        p[0] = p[0]*camera[6]/p[2] + camera[8];
        p[1] = p[1]*camera[7]/p[2] + camera[9];
    	residuals[0] = p[0] - T(u);
	    residuals[1] = p[1] - T(v);
        return true;
    }
    private:
    double x, y, z, u, v;
};

int main(int argc, char* argv[]) {
    google::InitGoogleLogging(argv[0]);
    double camera[12] = {0,0,0,  0,0,-10.0, 1,1,0,0, 0.1,0.1};
    double cameraGuess[12];
    addNoise(camera, cameraGuess);
    int nVerts = 100;
    double* verts = new double[5*nVerts];
    calculateVerts(verts, nVerts, camera);
    ceres::Problem problem;
    for (int i=0; i < nVerts; i++){
        ceres::CostFunction* function =
            new ceres::AutoDiffCostFunction<UVResidual, 2, 12>(
                new UVResidual(verts[5*i],
                               verts[5*i+1],
                               verts[5*i+2],
                               verts[5*i+3],
                               verts[5*i+4])
            );
        problem.AddResidualBlock(function, NULL, cameraGuess);
    }
    ceres::Solver::Options options;
    options.linear_solver_type = ceres::DENSE_SCHUR;
    options.minimizer_progress_to_stdout = true;
    ceres::Solver::Summary summary;
    ceres::Solve(options, &problem, &summary);
    std::cout << summary.FullReport() << "\n";
    printCamera(cameraGuess);
    
    return 0;
}







