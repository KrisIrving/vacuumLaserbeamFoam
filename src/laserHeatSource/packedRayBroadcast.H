#ifndef packedRayBroadcast_H
#define packedRayBroadcast_H

#include "compactRay.H"
#include "Pstream.H"
#include <cstring>
#include <limits>

namespace Foam
{
namespace packedRayDetail
{
    // Same native scalar/label representation as OpenFOAM contiguous transfers.
    // Never copy the polymorphic compactRay object, pointers, or struct padding.
    constexpr label recordBytes = 7*sizeof(scalar) + 3*sizeof(label) + 2;
    template<class T> inline void put(char*& p, const T& value)
    {
        std::memcpy(p, &value, sizeof(T)); p += sizeof(T);
    }
    template<class T> inline void get(const char*& p, T& value)
    {
        std::memcpy(&value, p, sizeof(T)); p += sizeof(T);
    }
}

inline List<char> packRays(const DynamicList<compactRay>& rays)
{
    using namespace packedRayDetail;
    if (rays.size() > std::numeric_limits<label>::max()/recordBytes)
        FatalErrorInFunction << "Packed ray message exceeds label capacity"
            << exit(FatalError);
    List<char> bytes(rays.size()*recordBytes);
    if (rays.empty()) return bytes;
    char* p=bytes.begin();
    forAll(rays, i)
    {
        const compactRay& ray=rays[i];
        if (!ray.path_.empty())
            FatalErrorInFunction << "Packed rays require empty visual paths"
                << exit(FatalError);
        for (label d=0; d<3; ++d) put(p,ray.position_[d]);
        for (label d=0; d<3; ++d) put(p,ray.direction_[d]);
        put(p,ray.power_); put(p,ray.currentCell_);
        put(p,ray.bounceCount_); put(p,ray.globalRayIndex_);
        const unsigned char active=ray.active_ ? 1 : 0;
        const unsigned char pending=ray.pendingSample_ ? 1 : 0;
        put(p,active); put(p,pending);
    }
    return bytes;
}

inline void unpackRays(const List<char>& bytes, DynamicList<compactRay>& rays)
{
    using namespace packedRayDetail;
    if (bytes.size()%recordBytes)
        FatalErrorInFunction << "Truncated packed ray message" << exit(FatalError);
    rays.setSize(bytes.size()/recordBytes);
    if (bytes.empty()) return;
    const char* p=bytes.begin();
    forAll(rays, i)
    {
        compactRay& ray=rays[i];
        for (label d=0; d<3; ++d) get(p,ray.position_[d]);
        for (label d=0; d<3; ++d) get(p,ray.direction_[d]);
        get(p,ray.power_); get(p,ray.currentCell_);
        get(p,ray.bounceCount_); get(p,ray.globalRayIndex_);
        unsigned char active=0,pending=0;
        get(p,active); get(p,pending);
        if (active>1 || pending>1)
            FatalErrorInFunction << "Invalid packed ray flags" << exit(FatalError);
        ray.active_=active; ray.pendingSample_=pending; ray.path_.clear();
    }
}

inline void broadcastPackedRays(DynamicList<compactRay>& rays)
{
    List<char> bytes;
    if (Pstream::master()) bytes=packRays(rays);
    Pstream::broadcastList(bytes);
    if (!Pstream::master()) unpackRays(bytes,rays);
}
}
#endif
