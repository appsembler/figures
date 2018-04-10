import React, { Component } from 'react';
import styles from './_stat-horizontal-bar-graph.scss';

class StatHorizontalBarGraph extends Component {

  render() {
    let maxValue = 0;

    if (this.props.dataType !== 'percentage') {
      this.props.data.forEach((dataSingle, index) => {
        if (dataSingle[this.props.valueLabel] > maxValue) {
          maxValue = dataSingle[this.props.valueLabel];
        }
      });
    };

    const graphRender = this.props.data.map((dataSingle, index) => {
      const barWidth = (this.props.dataType === 'percentage') ? (dataSingle[this.props.valueLabel]*100 + '%') : (dataSingle[this.props.valueLabel]/maxValue*100 + '%');

      return (
        <div key={dataSingle[this.props.labelLabel]} className={styles['horizontal-bar-wrapper']}>
          <div className={styles['label-container']}>
            <span className={styles['label-text']}>{dataSingle[this.props.labelLabel]}</span>
            <span className={styles['label-value']}>{(this.props.dataType === 'percentage') ? (dataSingle[this.props.valueLabel]*100 + '%') : dataSingle[this.props.valueLabel]}</span>
          </div>
          <div className={styles['bar-container']}>
            <span className={styles['bar-line']} style={{width: barWidth}} />
          </div>
        </div>
      );
    });

    return (
      <div className={styles['horizontal-bar-chart']}>
        {graphRender}
      </div>
    );
  }
}

StatHorizontalBarGraph.defaultProps = {
  graphHeight: 140,
  dataType: 'number',
  valueLabel: 'value',
  labelLabel: 'label',
}

export default StatHorizontalBarGraph;
