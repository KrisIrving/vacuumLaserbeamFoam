// Optional wall timers. All MPI reductions happen at output times only.
#ifndef vacuumPerformance_H
#define vacuumPerformance_H

#include <array>
#include <chrono>

class vacuumPerformance
{
public:
    enum section
    {
        controls, alpha, props, laser, momentum, thermal, pressure,
        history, fieldWrite, diagnostics, rayIO, executionLog, other, count
    };

private:
    typedef std::chrono::steady_clock clock;
    bool enabled_;
    std::array<clock::time_point, count> starts_;
    std::array<Foam::scalar, count> totals_;
    clock::time_point stepStart_;
    Foam::scalar wallTotal_;
    Foam::scalar startTime_;
    Foam::label steps_;
    Foam::label thermalCorrectors_;
    Foam::label maxThermalCorrectors_;
    Foam::label thermalLimitHits_;

public:
    vacuumPerformance(const bool enabled, const Foam::scalar startTime)
    :
        enabled_(enabled), totals_(), wallTotal_(0), startTime_(startTime),
        steps_(0), thermalCorrectors_(0), maxThermalCorrectors_(0),
        thermalLimitHits_(0)
    {}

    void beginStep()
    {
        if (enabled_) stepStart_ = clock::now();
    }

    void start(const section s)
    {
        if (enabled_) starts_[s] = clock::now();
    }

    void stop(const section s)
    {
        if (enabled_)
        {
            totals_[s] += std::chrono::duration<Foam::scalar>
                (clock::now() - starts_[s]).count();
        }
    }

    void addThermalCorrectors(const Foam::label n, const bool limitHit)
    {
        if (enabled_)
        {
            thermalCorrectors_ += n;
            maxThermalCorrectors_ = Foam::max(maxThermalCorrectors_, n);
            if (limitHit) ++thermalLimitHits_;
        }
    }

    void endStep()
    {
        if (enabled_)
        {
            wallTotal_ += std::chrono::duration<Foam::scalar>
                (clock::now() - stepStart_).count();
            ++steps_;
        }
    }

    void report(const Foam::scalar time)
    {
        using namespace Foam;
        if (!enabled_ || !steps_) return;

        scalar accounted = 0;
        for (int i = 0; i < other; ++i) accounted += totals_[i];
        totals_[other] = max(wallTotal_ - accounted, scalar(0));

        const scalar ranks = Pstream::nProcs();
        scalar wallMean = wallTotal_, wallMax = wallTotal_;
        reduce(wallMean, sumOp<scalar>());
        reduce(wallMax, maxOp<scalar>());
        wallMean /= ranks;

        // Mean sections add to mean wall time. Independently maximised
        // sections are NOT additive: each maximum can occur on another rank.
        std::array<scalar, count> mean(totals_), maximum(totals_);
        for (int i = 0; i < count; ++i)
        {
            reduce(mean[i], sumOp<scalar>());
            reduce(maximum[i], maxOp<scalar>());
            mean[i] /= ranks;
        }
        label maxCorrectors = maxThermalCorrectors_;
        reduce(maxCorrectors, maxOp<label>());

        const scalar physical = time - startTime_;
        Info<< "PERF_DIAGNOSTICS schema=2"
            << " time=" << time << " startTime=" << startTime_
            << " ranks=" << Pstream::nProcs()
            << " steps=" << steps_
            << " thermalCorrectors=" << thermalCorrectors_
            << " thermalCorrectorsPerStep="
            << scalar(thermalCorrectors_)/steps_
            << " maxThermalCorrectors=" << maxCorrectors
            << " thermalLimitHits=" << thermalLimitHits_
            << " stepWall_s=" << wallMean
            << " stepWallMax_s=" << wallMax
            << " rankWallImbalance=" << wallMax/max(wallMean, SMALL)
            << " wall_s_per_us=" << wallMax/max(physical*1e6, SMALL);

        const char* names[count] =
        {
            "controls", "alpha", "props", "laser", "momentum", "thermal",
            "pressure", "history", "fieldWrite", "diagnostics", "rayIO",
            "executionLog", "other"
        };
        for (int i = 0; i < count; ++i)
        {
            Info<< ' ' << names[i] << "_s=" << mean[i]
                << ' ' << names[i] << "Max_s=" << maximum[i];
        }
        Info<< endl;

        totals_.fill(0);
        wallTotal_ = 0;
        steps_ = thermalCorrectors_ = maxThermalCorrectors_ = 0;
        thermalLimitHits_ = 0;
        startTime_ = time;
    }
};
#endif
