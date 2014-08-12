#include "jittr/hello_world.h"

#include <iostream>
#include "ceres/ceres.h"
#include "glog/logging.h"

namespace {

using std::endl;

}


namespace jittr {

void hello_world(const std::string& name) {

  std::cout << "hello, " << name << "! " << endl
            << "Log file saved to /tmp/<name of program>.<severity>." << endl
            << "Run with --logtostderr=1 to see log messages."
            << endl;

  // Logs to a text file in /tmp, with line number.
  LOG(INFO) << "A log message from the jittr library" << std::endl;

  ceres::Problem problem;

  // You can make sanity-checks with informative error messages using the
  // CHECK_... macros from google-glog.
  //
  // See here for more info:
  // http://google-glog.googlecode.com/svn/trunk/doc/glog.html

  // CHECK_EQ: equals
  // CHECK_LT: less than
  // CHECK_LE: less than or equal to
  // CHECK_GT: greater than
  // CHECK_GE: greater than or equal to
  CHECK_EQ(3, 3) << "oh god wtf";
}

}
