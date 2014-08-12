#include "jittr/hello_world.h"
#include "ceres/ceres.h"
#include "glog/logging.h"
namespace jittr {

void hello_world() {
    std::cout << "hello from the jittr library" << std::endl;
    ceres::Problem problem;
}

}
