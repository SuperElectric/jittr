#include "jittr/find_cam.h"
#include "ceres/ceres.h"
#include "ceres/rotation.h"

namespace jittr{

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

void solveCamera(const double* const verts, int nVerts, double* camera){
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
        problem.AddResidualBlock(function, NULL, camera);
    }
    ceres::Solver::Options options;
    options.linear_solver_type = ceres::DENSE_SCHUR;
    options.minimizer_progress_to_stdout = true;
    options.num_threads = 8;
    ceres::Solver::Summary summary;
    ceres::Solve(options, &problem, &summary);
    std::cout << summary.BriefReport() << "\n";
}

}
