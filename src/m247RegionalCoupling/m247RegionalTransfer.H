// Cached axis-aligned cell overlap, global coarse ownership and parallel corrections.
#ifndef m247RegionalTransfer_H
#define m247RegionalTransfer_H
#include "fvCFD.H"
#include "Pstream.H"
#include <array>
#include <vector>
#include <map>
#include <set>
#include <cmath>
#include <cstdint>
#include <cstring>
namespace Foam
{
class m247RegionalTransfer
{
    const fvMesh& globalMesh_;
    const fvMesh& localMesh_;
    std::uint64_t globalStamp_,localStamp_;
    struct Box
    {
        std::array<scalar,6> c;
        scalar volume() const {return (c[3]-c[0])*(c[4]-c[1])*(c[5]-c[2]);}
    };
    using Key=std::array<long long,3>;
    struct Weight {label source;scalar volume;};
    std::vector<Box> source_;
    std::vector<std::vector<Weight>> weights_;
    scalarField localVolume_;
    labelList offsets_;
    label globalLocalCount_,globalLocalStart_;
    static scalar intersection(const Box& a,const Box& b)
    {
        scalar v=1;
        for(label d=0;d<3;++d)v*=max(scalar(0),min(a.c[d+3],b.c[d+3])-max(a.c[d],b.c[d]));
        return v;
    }
    static std::vector<Box> boxes(const fvMesh& mesh)
    {
        std::vector<Box> result(mesh.nCells());
        forAll(mesh.cells(),i)
        {
            Box b{{GREAT,GREAT,GREAT,-GREAT,-GREAT,-GREAT}};
            const cell& faces=mesh.cells()[i];
            forAll(faces,j)
            {
                const face& points=mesh.faces()[faces[j]];
                forAll(points,k)for(label d=0;d<3;++d)
                {scalar x=mesh.points()[points[k]][d];if(!std::isfinite(x))FatalErrorInFunction<<"Nonfinite mesh point"<<exit(FatalError);b.c[d]=min(b.c[d],x);b.c[d+3]=max(b.c[d+3],x);}
            }
            const scalar v=b.volume();
            if(!std::isfinite(v)||v<=0||mag(v-mesh.V()[i])>1e-10*mesh.V()[i])
                FatalErrorInFunction<<"Regional transfer requires rectangular cells with matching mesh volume"<<exit(FatalError);
            result[i]=b;
        }
        return result;
    }
    static std::uint64_t stamp(const fvMesh& mesh)
    {
        std::uint64_t h=1469598103934665603ULL;
        auto add=[&](std::uint64_t x){h=(h^x)*1099511628211ULL;};
        add(mesh.nCells());add(mesh.nPoints());add(mesh.nFaces());
        for(const point& p:mesh.points())for(label d=0;d<3;++d)
        {std::uint64_t bits=0;scalar x=p[d];std::memcpy(&bits,&x,sizeof(scalar));add(bits);}
        for(const face& f:mesh.faces()){add(f.size());for(label v:f)add(v);}
        for(const cell& c:mesh.cells()){add(c.size());for(label f:c)add(f);}
        return h;
    }
    void ensureCurrent() const
    {
        if(stamp(globalMesh_)!=globalStamp_ || stamp(localMesh_)!=localStamp_)
            FatalErrorInFunction<<"Regional geometry/addressing changed: rebuild transfer"<<exit(FatalError);
    }
    scalarField gather(const scalarField& values) const
    {
        if(values.size()!=globalLocalCount_)FatalErrorInFunction<<"Global field addressing changed"<<exit(FatalError);
        forAll(values,i)if(!std::isfinite(values[i]))FatalErrorInFunction<<"Nonfinite source density"<<exit(FatalError);
        List<scalarField> ranks(Pstream::nProcs());ranks[Pstream::myProcNo()]=values;
        Pstream::allGatherList(ranks);
        scalarField result(source_.size());
        forAll(ranks,p)
        {
            if(ranks[p].size()!=offsets_[p+1]-offsets_[p])FatalErrorInFunction<<"Changed global partition"<<exit(FatalError);
            forAll(ranks[p],i)result[offsets_[p]+i]=ranks[p][i];
        }
        return result;
    }
public:
    m247RegionalTransfer(const fvMesh& global,const fvMesh& local)
    : globalMesh_(global),localMesh_(local),globalStamp_(stamp(global)),localStamp_(stamp(local)),
      localVolume_(local.V()),offsets_(Pstream::nProcs()+1,0),
      globalLocalCount_(global.nCells()),globalLocalStart_(0)
    {
        const auto owned=boxes(global);
        scalarField packed(6*owned.size());
        for(label i=0;i<label(owned.size());++i)for(label d=0;d<6;++d)packed[6*i+d]=owned[i].c[d];
        List<scalarField> ranks(Pstream::nProcs());ranks[Pstream::myProcNo()]=packed;
        Pstream::allGatherList(ranks);
        forAll(ranks,p)
        {
            if(ranks[p].size()%6)FatalErrorInFunction<<"Bad geometry packet"<<exit(FatalError);
            offsets_[p+1]=offsets_[p]+ranks[p].size()/6;
            for(label i=0;i<ranks[p].size()/6;++i)
            {Box b;for(label d=0;d<6;++d)b.c[d]=ranks[p][6*i+d];source_.push_back(b);}
        }
        if(source_.empty()||source_.size()>200000)
            FatalErrorInFunction<<"Reference global thermal mesh must contain 1..200000 cells"<<exit(FatalError);
        globalLocalStart_=offsets_[Pstream::myProcNo()];
        std::array<scalar,3> origin{{GREAT,GREAT,GREAT}};scalar width=0;
        for(const Box& b:source_)for(label d=0;d<3;++d)
        {origin[d]=min(origin[d],b.c[d]);width=max(width,b.c[d+3]-b.c[d]);}
        auto keys=[&](const Box& b)
        {
            std::vector<Key> result;Key lo,hi;
            for(label d=0;d<3;++d)
            {lo[d]=std::floor((b.c[d]-origin[d])/width);hi[d]=std::floor((b.c[d+3]-origin[d])/width);}
            for(long long x=lo[0];x<=hi[0];++x)for(long long y=lo[1];y<=hi[1];++y)for(long long z=lo[2];z<=hi[2];++z)
                result.push_back(Key{{x,y,z}});
            return result;
        };
        std::map<Key,std::vector<label>> index;
        for(label i=0;i<label(source_.size());++i)
        {
            std::set<label> seen;
            for(const Key& key:keys(source_[i]))
            {
                for(label j:index[key])if(seen.insert(j).second && intersection(source_[i],source_[j])>0)
                    FatalErrorInFunction<<"Overlapping global thermal cells"<<exit(FatalError);
                index[key].push_back(i);
            }
        }
        const auto targets=boxes(local);weights_.resize(targets.size());
        for(label j=0;j<label(targets.size());++j)
        {
            std::set<label> candidates;
            for(const Key& key:keys(targets[j]))
            {auto found=index.find(key);if(found!=index.end())candidates.insert(found->second.begin(),found->second.end());}
            scalar covered=0;
            for(label i:candidates)
            {scalar w=intersection(source_[i],targets[j]);if(w>0){weights_[j].push_back(Weight{i,w});covered+=w;}}
            if(mag(covered-localVolume_[j])>1e-10*localVolume_[j])
                FatalErrorInFunction<<"Local cell outside global thermal coverage"<<exit(FatalError);
        }
    }
    scalarField gatherDensity(const scalarField& globalDensity) const
    {
        ensureCurrent();
        const scalarField all=gather(globalDensity);scalarField result(localVolume_.size(),0);
        forAll(result,j)
        {
            scalar covered=0;
            for(const Weight& w:weights_[j]){result[j]+=all[w.source]*w.volume;covered+=w.volume;}
            // Coverage was checked against actual V on construction. Normalize the
            // geometric row once: constant alpha=1 must not become 1+roundoff.
            result[j]/=covered;
        }
        return result;
    }
    scalarField scatterIntegratedCorrection(const scalarField& delta) const
    {
        ensureCurrent();
        if(delta.size()!=localVolume_.size())FatalErrorInFunction<<"Local topology changed: rebuild transfer"<<exit(FatalError);
        List<scalar> correction(source_.size(),0);scalar before=0,scale=0;
        forAll(delta,j)
        {
            if(!std::isfinite(delta[j]))FatalErrorInFunction<<"Nonfinite local correction"<<exit(FatalError);
            before+=delta[j];scale+=mag(delta[j]);
            for(const Weight& w:weights_[j])correction[w.source]+=delta[j]*w.volume/localVolume_[j];
        }
        Pstream::listCombineReduce(correction,plusEqOp<scalar>());
        scalar after=0;scalarField result(globalLocalCount_,0);
        forAll(result,i)
        {const label j=globalLocalStart_+i;result[i]=correction[j]/source_[j].volume();after+=correction[j];}
        reduce(before,sumOp<scalar>());reduce(after,sumOp<scalar>());reduce(scale,sumOp<scalar>());
        if(mag(after-before)>1e-10*max(scale,scalar(1e-300)))
            FatalErrorInFunction<<"Regional integrated correction failed conservation"<<exit(FatalError);
        return result;
    }
};
}
#endif
