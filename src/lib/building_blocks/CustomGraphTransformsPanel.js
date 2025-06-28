import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {
    Radio,
    TraceAccordion,
    DataSelector,
    Dropdown,
    PlotlySection,
    FilterOperation,
    FilterValue,
    connectAggregationToTransform,
} from 'react-chart-editor';

import CustomTransformAccordion from './CustomTransformAccordion';

const AggregationSection = connectAggregationToTransform(PlotlySection);

export class Aggregations extends Component {
    render() {
        const {
            fullContainer: {aggregations = []},
        } = this.context;
        const {localize: _} = this.context;
        if (aggregations.length === 0) {
            return null;
        }

        return (
            <PlotlySection name={_('Aggregations')} attr="aggregations">
                {aggregations
                    .filter((aggr, i) => aggr.target && i === 0)
                    .map(({target}, i) => (
                        <AggregationSection show key={i} aggregationIndex={i}>
                            <Dropdown
                                attr="func"
                                label={target}
                                options={[
                                    {label: _('Count'), value: 'count'},
                                    {label: _('Sum'), value: 'sum'},
                                    {label: _('Average'), value: 'avg'},
                                    {label: _('Median'), value: 'median'},
                                    {label: _('Mode'), value: 'mode'},
                                    {label: _('RMS'), value: 'rms'},
                                    {
                                        label: _('Standard Deviation'),
                                        value: 'stddev',
                                    },
                                    {label: _('Min'), value: 'min'},
                                    {label: _('Max'), value: 'max'},
                                    {label: _('First'), value: 'first'},
                                    {label: _('Last'), value: 'last'},
                                    // {label: _('Change'), value: 'change'},
                                    {label: _('Range'), value: 'range'},
                                ]}
                                clearable={false}
                            />
                        </AggregationSection>
                    ))}
            </PlotlySection>
        );
    }
}

Aggregations.plotly_editor_traits = {no_visibility_forcing: true};
Aggregations.contextTypes = {
    fullContainer: PropTypes.object,
    localize: PropTypes.func,
};

const CustomGraphTransformsPanel = (props, {localize: _}) => {
    return (
        <TraceAccordion traceFilterCondition={(t) => t.type}>
            <CustomTransformAccordion>
                <Radio
                    attr="enabled"
                    options={[
                        {label: _('Enabled'), value: true},
                        {label: _('Disabled'), value: false},
                    ]}
                />

                <DataSelector label={_('By')} attr="groups" />

                <DataSelector label={_('Target')} attr="target" />
                <FilterOperation label={_('Operator')} attr="operation" />
                <FilterValue label={_('Value')} attr="value" />

                <Radio
                    attr="order"
                    options={[
                        {label: _('Ascending'), value: 'ascending'},
                        {label: _('Descending'), value: 'descending'},
                    ]}
                />

                <Aggregations />
            </CustomTransformAccordion>
        </TraceAccordion>
    );
};

CustomGraphTransformsPanel.contextTypes = {
    localize: PropTypes.func,
};

export default CustomGraphTransformsPanel;
