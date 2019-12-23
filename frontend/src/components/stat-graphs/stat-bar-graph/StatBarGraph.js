import React, { Component } from 'react';
import styles from './_stat-bar-graph.scss';
import { ResponsiveContainer, BarChart, Bar, Tooltip, CartesianGrid, YAxis, XAxis } from 'recharts';


class CustomTooltip extends Component {

  render() {
    const { active } = this.props;

    if (active) {
      const { payload } = this.props;
      return (
        <div className={styles['bar-tooltip']}>
          <span className={styles['tooltip-value']}>
            {(this.props.dataType === 'percentage') ? (payload[0].value)*100 : payload[0].value}
            {(this.props.dataType === 'percentage') && '%'}
          </span>
        </div>
      );
    }

    return null;
  }
}

class StatBarGraph extends Component {
  render() {
    const yAxisTickFormatter = (value) => {
      if (this.props.dataType === 'percentage') {
        return `${value*100}%`;
      } else {
        return `${value}`;
      }
    }

    const xAxisTickFormatter = (value) => {
      return `${value}`;
    }

    return (
      <ResponsiveContainer className={styles['stat-bar-graph']} width="100%" height={this.props.graphHeight}>
        <BarChart
          data={this.props.data.toJS()}
          margin={{top: 0, bottom: 0, left: 0, right: 0}}
          barCategoryGap={2}
        >
          <CartesianGrid
            vertical={false}
          />
          <Tooltip
            content={<CustomTooltip dataType={this.props.dataType} />}
            cursor={{ fill: 'rgba(255, 255, 255, 0.15)'}}
            offset={0}
          />
          <Bar className={styles['stat-bar']} dataKey='value' stroke='none' />
          <YAxis className="test" tickFormatter={yAxisTickFormatter} />
          <XAxis className="test" dataKey='period' tickFormatter={xAxisTickFormatter} />
        </BarChart>
      </ResponsiveContainer>
    );
  }
}

StatBarGraph.defaultProps = {
  graphHeight: 140,
  dataType: 'number',
}

export default StatBarGraph;
