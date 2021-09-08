import { AgeGroup } from '../.generated/latest/types'
import { AgeDistributionDatum, ScenarioFlat, SeverityDistributionDatum } from './types/Param.types'
import { AlgorithmResult, SimulationTimePoint, ExportedTimePoint, ModelParams } from './types/Result.types'

import { getPopulationParams, initializePopulation, withUncertainty, msPerDay } from './initialize'
import { collectTotals, evolve } from './model'
import { percentileTrajectory } from './results'
import { preparePlotData } from './preparePlotData'

const identity = (x: number) => x

export interface RunParams {
  params: ScenarioFlat
  severity: SeverityDistributionDatum[]
  ageDistribution: AgeDistributionDatum[]
}

function simulate(
  initialState: SimulationTimePoint,
  params: ModelParams,
  tMax: number,
  ageGroups: AgeGroup[],
  func: (x: number) => number,
): ExportedTimePoint[] {
  const dynamics = [initialState]
  let currState = initialState

  while (currState.time < tMax) {
    currState = evolve(currState, params, currState.time + 1, func)
    dynamics.push(currState)
  }

  return collectTotals(dynamics, ageGroups)
}

function burnIn(
  N: number,
  numCases: number,
  t0: number,
  scenario: ScenarioFlat,
  params: ModelParams,
  ageDistribution: AgeDistributionDatum[],
): SimulationTimePoint {
  const ageGroups = ageDistribution.map((d) => d.ageGroup)
  const burnInTime = 21 // run simulation for 21 days to equilibrate states
  const population = initializePopulation(N, numCases, t0, scenario, ageDistribution)
  const burnInTrajectory = simulate(population, params, t0 + msPerDay * burnInTime, ageGroups, identity)
  const burnedIn = burnInTrajectory[burnInTrajectory.length - 1]

  // determine the ratio of the specified number of cases and the cases in the burnedIn time point
  const rescaleFactor =
    numCases /
    (burnedIn.current.infectious.total +
      burnedIn.current.exposed.total +
      burnedIn.current.severe.total +
      burnedIn.current.critical.total +
      burnedIn.current.overflow.total)

  // copy the vales of the burnedIn timepoint to the .current structure of the initial population
  // rescale to match initial number of cases
  for (const [i, age] of ageGroups.entries()) {
    for (let e = 0; e < population.current.exposed[i].length; e++) {
      population.current.exposed[i][e] =
        (rescaleFactor * burnedIn.current.exposed[age]) / population.current.exposed[i].length
    }
    population.current.infectious[i] = rescaleFactor * burnedIn.current.infectious[age]
    population.current.severe[i] = rescaleFactor * burnedIn.current.severe[age]
    population.current.critical[i] = rescaleFactor * burnedIn.current.critical[age]
    population.current.overflow[i] = rescaleFactor * burnedIn.current.overflow[age]
  }

  return population
}

export async function run({ params, severity, ageDistribution }: RunParams): Promise<AlgorithmResult> {
  const tMin: number = new Date(params.simulationTimeRange.begin).getTime()
  const tMax: number = new Date(params.simulationTimeRange.end).getTime()
  const ageGroups = ageDistribution.map((d) => d.ageGroup)
  const initialCases = params.initialNumberOfCases

  const stochastic = withUncertainty(params)

  let stochasticTrajectories: ExportedTimePoint[][] = []
  let stochasticParams: ModelParams[] = []
  if (stochastic) {
    stochasticParams = getPopulationParams(params, severity, ageDistribution, false)
    stochasticTrajectories = stochasticParams.map((modelParams) => {
      const tmpPopulation = initializePopulation(
        modelParams.populationServed,
        initialCases,
        tMin,
        params,
        ageDistribution,
      )
      return simulate(tmpPopulation, modelParams, tMax, ageGroups, identity)
    })
  }
  const deterministicParams = getPopulationParams(params, severity, ageDistribution, true)[0]
  const population = burnIn(
    deterministicParams.populationServed,
    initialCases,
    tMin,
    params,
    deterministicParams,
    ageDistribution,
  )
  const deterministicTrajectory = simulate(population, deterministicParams, tMax, ageGroups, identity)
  const R0Times = []
  let tR0 = new Date('2020-02-01').getTime()

  while (tR0 < tMin) {
    R0Times.push({ time: tR0, seroprevalence: params.seroprevalence })
    tR0 += msPerDay
  }
  deterministicTrajectory.forEach((tp) => {
    R0Times.push({
      time: tp.time,
      seroprevalence: params.seroprevalence + tp.cumulative.recovered.total / params.populationServed,
    })
  })

  const thresholds = [0.2, 0.8]
  const idxs = thresholds.map((d) => Math.ceil((stochasticTrajectories.length - 1) * d))
  const R0Trajectories = stochastic
    ? R0Times.map((d) => {
        return {
          t: d.time,
          y: stochasticParams
            .map(
              (ModelParams) =>
                ModelParams.rate.infection(d.time) * params.infectiousPeriodDays * (1 - d.seroprevalence * 0.01),
            )
            .sort((a, b) => a - b),
        }
      })
    : []

  const meanR0Trajectory = R0Times.map((d) => {
    return {
      t: d.time,
      y: deterministicParams.rate.infection(d.time) * params.infectiousPeriodDays * (1 - d.seroprevalence * 0.01),
    }
  })
  const resultsTrajectory = {
    lower: stochastic ? percentileTrajectory(stochasticTrajectories, 0.2) : deterministicTrajectory,
    middle: deterministicTrajectory,
    upper: stochastic ? percentileTrajectory(stochasticTrajectories, 0.8) : deterministicTrajectory,
    percentile: {},
  }
  return {
    trajectory: resultsTrajectory,
    R0: {
      mean: meanR0Trajectory,
      lower: stochastic ? R0Trajectories.map((d) => ({ t: d.t, y: d.y[idxs[0]] })) : meanR0Trajectory,
      upper: stochastic ? R0Trajectories.map((d) => ({ t: d.t, y: d.y[idxs[1]] })) : meanR0Trajectory,
    },
    plotData: preparePlotData(resultsTrajectory),
  }
}
