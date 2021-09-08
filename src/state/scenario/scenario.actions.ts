import actionCreatorFactory from 'typescript-fsa'

import type { UUIDv4 } from '../../helpers/uuid'

import type {
  AgeDistributionDatum,
  ScenarioDatum,
  ScenarioParameters,
  SeverityDistributionDatum,
  CaseCountsData,
} from '../../algorithms/types/Param.types'

const action = actionCreatorFactory('SCENARIO')

export interface SetScenarioParams {
  name: string
}

export const renameCurrentScenario = action<SetScenarioParams>('RENAME_CURRENT_SCENARIO')
export const setScenario = action<SetScenarioParams>('SET_SCENARIO')

export const setScenarioData = action<ScenarioDatum>('SET_SCENARIO_DATA')
export const setAgeDistributionData = action<AgeDistributionDatum[]>('SET_AGE_DISTRIBUTION_DATA')
export const setSeverityDistributionData = action<SeverityDistributionDatum[]>('SET_SEVERITY_DISTRIBUTION_DATA')
export const setCaseCountsDataCustom = action<CaseCountsData>('SET_CASE_COUNTS_DATA_CUSTOM')
export const resetCaseCounts = action<void>('RESET_CASE_COUNTS')
export const setScenarioState = action<ScenarioParameters>('SET_STATE_DATA')
export const addMitigationInterval = action<void>('ADD_MITIGATION_INTERVAL')
export const removeMitigationInterval = action<UUIDv4>('REMOVE_MITIGATION_INTERVAL')

export const setCanRun = action<boolean>('SET_CAN_RUN')
