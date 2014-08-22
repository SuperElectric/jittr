struct vec3{double x,y,z;};
struct vec2{double u,v;};
struct index3{int mid,vid,vtid;};
struct vec5{double u,v,x,y,z;};
struct UVResiduals;
void solveCamera(const vec5* const arrayOfVerts, int nVerts, double* camera);
void calculateVerts(double* verts, int nVerts, const double* const camera);
void addNoise(const double* const oldCamera, double* newCamera);
void printCamera(double camera[]);
void parseObj(const std::string& filePath,
              std::vector<vec3>* xyzPtr,
              std::vector<vec2>* uvPtr,
              std::vector<index3>* indexPtr,
              std::map<std::string, int>* materialsPtr);
void createUvxyzLists (const std::vector <vec3>& xyzList,
                       const std::vector <vec2>& uvList,
                       const std::vector <index3>& indexList,
                       std::vector<vec5>* arrayOfVectors);
void selectRandomVerts(const std::vector<vec5>& vectorOfVerts,
                       int nVerts,
                       vec5* arrayOfVerts);
