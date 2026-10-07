#ifndef laserPerformance_H
#define laserPerformance_H

#include "PstreamReduceOps.H"
#include "scalarField.H"
#include "IOstreams.H"
#include <array>
#include <chrono>

namespace Foam
{
// Diagnostic only. Mean stages are additive; rank maxima are not.
// Sampled search time is a subset of trace, never an extra additive stage.
class laserPerformance
{
public:
    enum stage { seedGenerate, seedExchange, seedLocate, ownership, trace,
                 exchange, finalize, other, stageCount };
    enum counter { calls, initialRays, exchangeRounds, ownershipChecks,
                   localSegments, advances, traceSearchCalls, interfaceEvents,
                   bulkEvents, mergeCalls, mergeXRays, mergeYRays, mergeAppends,
                   counterCount };
    enum detail { exchangeCopy, gather, broadcast, merge, detailCount };
private:
    using clock = std::chrono::steady_clock;
    bool enabled_;
    std::array<clock::time_point, stageCount> starts_;
    std::array<scalar, stageCount> seconds_{};
    std::array<scalar, counterCount> counters_{};
    std::array<clock::time_point, detailCount> detailStarts_;
    std::array<scalar, detailCount> detailSeconds_{};
    clock::time_point callStart_;
    scalar total_ = 0;
    scalar sampledSearch_ = 0;
    scalar samples_ = 0;
    unsigned searchSequence_ = 0;
public:
    explicit laserPerformance(const bool enabled) : enabled_(enabled) {}
    void beginCall()
    {
        if (enabled_) { callStart_=clock::now(); ++counters_[calls]; }
    }
    void endCall()
    {
        if (enabled_) total_ += std::chrono::duration<scalar>(clock::now()-callStart_).count();
    }
    void start(const stage s) { if (enabled_) starts_[s]=clock::now(); }
    void stop(const stage s)
    {
        if (enabled_) seconds_[s] += std::chrono::duration<scalar>(clock::now()-starts_[s]).count();
    }
    void add(const counter c, const scalar n=1) { if (enabled_) counters_[c]+=n; }
    void startDetail(const detail d) { if (enabled_) detailStarts_[d]=clock::now(); }
    void stopDetail(const detail d)
    {
        if (enabled_) detailSeconds_[d]+=std::chrono::duration<scalar>(clock::now()-detailStarts_[d]).count();
    }
    template<class Search> label search(Search&& operation)
    {
        if (!enabled_) return operation();
        ++counters_[traceSearchCalls];
        // Deterministic stride avoids one clock read per ray advance.
        if ((searchSequence_++ % 128) != 0) return operation();
        const auto start=clock::now();
        const label result=operation();
        sampledSearch_ += std::chrono::duration<scalar>(clock::now()-start).count();
        ++samples_;
        return result;
    }
    void report(const scalar time)
    {
        if (!enabled_ || !counters_[calls]) return;
        scalar accounted=0;
        for (int i=0; i<other; ++i) accounted+=seconds_[i];
        seconds_[other]=max(total_-accounted,scalar(0));
        scalar mean=total_, maximum=total_;
        reduce(mean,sumOp<scalar>()); reduce(maximum,maxOp<scalar>());
        mean/=Pstream::nProcs();
        // Preserve large integer counters when checking rank/global sums.
        const auto oldPrecision=Info.precision();
        Info.precision(15);
        Info<< "LASER_PERF_DIAGNOSTICS schema=2 time=" << time
            << " ranks=" << Pstream::nProcs()
            << " total_s=" << mean << " totalMax_s=" << maximum;
        const char* names[stageCount]={"seedGenerate","seedExchange","seedLocate",
            "ownership","trace","exchange","finalize","other"};
        for (int i=0; i<stageCount; ++i)
        {
            scalar average=seconds_[i], high=seconds_[i];
            reduce(average,sumOp<scalar>()); reduce(high,maxOp<scalar>());
            Info<< ' ' << names[i] << "_s=" << average/Pstream::nProcs()
                << ' ' << names[i] << "Max_s=" << high;
        }
        const char* countNames[counterCount]={"callsMean","initialRaysMean",
            "exchangeRoundsMean","ownershipChecksSum","localSegmentsSum",
            "advancesSum","traceSearchCallsSum","interfaceEventsSum","bulkEventsSum",
            "mergeCallsSum","mergeXRaysSum","mergeYRaysSum","mergeAppendsSum"};
        for (int i=0; i<counterCount; ++i)
        {
            scalar sum=counters_[i]; reduce(sum,sumOp<scalar>());
            Info<< ' ' << countNames[i] << '=' << (i<=exchangeRounds ? sum/Pstream::nProcs() : sum);
        }
        scalar sampled=sampledSearch_, n=samples_;
        reduce(sampled,sumOp<scalar>()); reduce(n,sumOp<scalar>());
        Info<< " traceSearchSampleSum_s=" << sampled
            << " traceSearchSamplesSum=" << n << " searchSampleStride=128";
        const char* detailNames[detailCount]={"exchangeCopy","gather","broadcast","merge"};
        for (int i=0; i<detailCount; ++i)
        {
            scalar average=detailSeconds_[i], high=detailSeconds_[i];
            reduce(average,sumOp<scalar>()); reduce(high,maxOp<scalar>());
            Info<< ' ' << detailNames[i] << "_s=" << average/Pstream::nProcs()
                << ' ' << detailNames[i] << "Max_s=" << high;
        }
        Info<< endl;
        // Small rank rows are gathered only at output times, not ray rounds.
        List<scalarField> rankRows(Pstream::nProcs());
        scalarField values(18, scalar(0));
        values[0]=seconds_[trace]; values[1]=seconds_[ownership]; values[2]=seconds_[exchange];
        for (int i=0; i<detailCount; ++i) values[3+i]=detailSeconds_[i];
        const int rankCounters[11]={advances,localSegments,traceSearchCalls,interfaceEvents,
            bulkEvents,mergeCalls,mergeXRays,mergeYRays,mergeAppends,calls,exchangeRounds};
        for (int i=0; i<11; ++i) values[7+i]=counters_[rankCounters[i]];
        rankRows[Pstream::myProcNo()]=values;
        Pstream::gatherList(rankRows);
        if (Pstream::master())
        {
            const char* rankNames[18]={"trace_s","ownership_s","exchange_s","exchangeCopy_s",
                "gather_s","broadcast_s","merge_s","advances","segments","searches",
                "interfaceEvents","bulkEvents","mergeCalls","mergeXRays","mergeYRays",
                "mergeAppends","calls","rounds"};
            forAll(rankRows, rank)
            {
                Info<< "LASER_RANK_DIAGNOSTICS schema=2 time=" << time << " rank=" << rank;
                for (int i=0; i<18; ++i) Info<< ' ' << rankNames[i] << '=' << rankRows[rank][i];
                Info<< endl;
            }
        }
        Info.precision(oldPrecision);
        seconds_.fill(0); counters_.fill(0); total_=sampledSearch_=samples_=0;
        detailSeconds_.fill(0);
        searchSequence_=0;
    }
};
}
#endif
