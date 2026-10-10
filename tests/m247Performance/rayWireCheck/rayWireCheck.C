#include "argList.H"
#include "packedRayBroadcast.H"
#include "PstreamReduceOps.H"
#include <limits>

int main(int argc, char *argv[])
{
    Foam::argList args(argc,argv);
    using namespace Foam;
    const label sizes[]={0,1,7,1536};
    label failures=0;
    for (const label count:sizes)
    {
        DynamicList<compactRay> expected;
        expected.setSize(count);
        forAll(expected,i)
        {
            compactRay& ray=expected[i];
            ray.position_=point(scalar(i)*1e-6,-scalar(i)*1e-9,-scalar(0));
            ray.direction_=vector(1,scalar(i%7)/7,-1);
            ray.power_=i%2 ? std::numeric_limits<scalar>::max() : SMALL;
            ray.currentCell_=i%2 ? std::numeric_limits<label>::max() : -1;
            ray.bounceCount_=i;
            ray.globalRayIndex_=i%2 ? i : std::numeric_limits<label>::min();
            ray.active_=i%2; ray.pendingSample_=i%3==0;
        }
        const List<char> original=packRays(expected);
        DynamicList<compactRay> actual;
        if (Pstream::master()) actual=expected;
        broadcastPackedRays(actual);
        if (packRays(actual)!=original) ++failures; // bitwise, including signed zero
        if (actual.size()!=expected.size()) ++failures;
        else forAll(actual,i) if (actual[i]!=expected[i]) ++failures;
    }
    reduce(failures,sumOp<label>());
    Info<< "RAY_WIRE_CHECK schema=1 ranks=" << Pstream::nProcs()
        << " cases=4 failures=" << failures << endl;
    return failures ? 1 : 0;
}
