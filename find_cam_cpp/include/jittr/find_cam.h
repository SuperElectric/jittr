struct vec3{double x,y,z;};
struct vec2{double u,v;};
struct index3{int mid,vid,vtid;};
struct vec5{double u,v,x,y,z;};
namespace jittr {
    struct UVResiduals;
    void solveCamera(const vec5* const arrayOfVerts, int nVerts, double* camera);
}
