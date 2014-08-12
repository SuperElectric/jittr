#include "glog/logging.h"
#include "gflags/gflags.h"
#include "jittr/hello_world.h"

// The google-gflags library lets you easily set up command line args like this
// For flags with other data types, see:
// https://gflags.googlecode.com/git-history/master/doc/gflags.html
DEFINE_string(name,  // variable to store flag in
              "stranger",    // default value
              "your name");  // description, to go in help message

int main(int argc, char* argv[]) {
  google::InitGoogleLogging(argv[0]);
  google::ParseCommandLineFlags(&argc, &argv, true);

  jittr::hello_world(FLAGS_name);
  return 0;
}
