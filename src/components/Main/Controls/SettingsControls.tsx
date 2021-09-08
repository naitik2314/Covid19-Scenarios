import React from 'react'

import { useTranslation } from 'react-i18next'
import { connect } from 'react-redux'
import { Col, Row } from 'reactstrap'
import { ActionCreator } from 'typescript-fsa'

import type { State } from '../../../state/reducer'

import {
  selectIsLogScale,
  selectShouldFormatNumbers,
  selectIsAutorunEnabled,
} from '../../../state/settings/settings.selectors'

import { setAutorun, setFormatNumbers, setLogScale } from '../../../state/settings/settings.actions'

import FormSwitch from '../../Form/FormSwitch'

export interface SettingsControlsProps {
  isAutorunEnabled: boolean
  isLogScale: boolean
  setAutorun: ActionCreator<boolean>
  setFormatNumbers: ActionCreator<boolean>
  setLogScale: ActionCreator<boolean>
  shouldFormatNumbers: boolean
}

const mapStateToProps = (state: State) => ({
  isAutorunEnabled: selectIsAutorunEnabled(state),
  isLogScale: selectIsLogScale(state),
  shouldFormatNumbers: selectShouldFormatNumbers(state),
})

const mapDispatchToProps = {
  setAutorun,
  setFormatNumbers,
  setLogScale,
}

export function SettingsControlsDisconnected({
  isAutorunEnabled,
  isLogScale,
  setAutorun,
  setFormatNumbers,
  setLogScale,
  shouldFormatNumbers,
}: SettingsControlsProps) {
  const { t } = useTranslation()

  return (
    <Row noGutters className="mt-1 ml-2">
      <Col className="d-flex flex-wrap my-auto">
        <span className="mr-4 flex-1" data-testid="AutorunSwitch">
          <FormSwitch
            identifier="autorun"
            label={t('Run automatically')}
            help={t('Run simulation automatically when any of the parameters change')}
            checked={isAutorunEnabled}
            onValueChanged={setAutorun}
          />
        </span>
        <span className="mr-4 flex-1" data-testid="LogScaleSwitch">
          <FormSwitch
            identifier="logScale"
            label={t('Log scale')}
            help={t('Toggle between logarithmic and linear scale on vertical axis of the plot')}
            checked={isLogScale}
            onValueChanged={setLogScale}
          />
        </span>
        <span className="flex-1" data-testid="HumanizedValuesSwitch">
          <FormSwitch
            identifier="showHumanized"
            label={t('Format numbers')}
            help={t('Show numerical results in a human-friendly format')}
            checked={shouldFormatNumbers}
            onValueChanged={setFormatNumbers}
          />
        </span>
      </Col>
    </Row>
  )
}

const SettingsControls = connect(mapStateToProps, mapDispatchToProps)(SettingsControlsDisconnected)

export { SettingsControls }
