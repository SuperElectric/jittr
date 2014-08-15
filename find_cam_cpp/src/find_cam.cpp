#include "glog/logging.h"
#include "ceres/ceres.h"
#include "ceres/rotation.h"
#include <iostream>

using ceres::AutoDiffCostFunction;
using ceres::CostFunction;
using ceres::Problem;
using ceres::Solver;
using ceres::Solve;
using std::cout;
using std::endl;

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
        p[0] = p[0]*camera[6]/p[2] + camera[8]
        p[1] = p[1]*camera[7]/p[2] + camera[9]
        
        
        

        return true;
    }

    private:
    double x, y, z, u, v;
};

int main(int argc, char* argv[]) {
    google::InitGoogleLogging(argv[0]);
    double p[3];
    double camera[3] = {0.0,0.0,3.14};
    double xyz[3] = {1.0,0.0,0.0};

    UVResidual uv_res;
    uv_res(camera,p);

    for (int i=0; i<3; i++){
        cout << p[i] << endl;
    }

  return 0;
}
