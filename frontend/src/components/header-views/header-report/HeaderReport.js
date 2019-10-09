import React, { Component } from 'react';
import { connect } from 'react-redux';
import { updateReportName, fetchReport } from 'base/redux/actions/Actions';
import { Link } from 'react-router-dom';
import classNames from 'classnames/bind';
import styles from './_header-report.scss';
import ContentEditable from 'base/components/inputs/ContentEditable'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCopy, faTrashAlt, faFilePdf, faPrint, faAngleRight, faEllipsisH } from '@fortawesome/free-solid-svg-icons';

let cx = classNames.bind(styles);

class HeaderReport extends Component {
  constructor(props) {
    super(props);

    this.state = {
      reportName: this.props.reportName,
      controlsExpanded: false,
    };

    this.editReportData = this.editReportData.bind(this);
  }

  editReportData = (evt) => {
    this.setState({
      reportName: evt.target.value,
    });
  }

  expandControls = () => {
    this.setState({
      controlsExpanded: !this.state.controlsExpanded,
    });
  }

  componentWillReceiveProps(nextProps) {
    if (this.props !== nextProps) {
      this.setState({
        reportName: nextProps.reportName,
      })
    }
  }

  componentDidMount() {
    this.props.fetchReport(this.props.reportId)
  }

  render() {

    return (
      <section className={styles['header-content-report']}>
        <div className={cx({ 'main-content': true, 'container': true})}>
          <div className={styles['content-top']}>
            <Link
              to='/figures/reports'
              className={styles['back-link']}
            >
              Back to reports list
            </Link>
            <ContentEditable
              className={styles['report-title']}
              html={this.state.reportName}
              dataLabel={'reportTitle'}
              onChange={this.editReportData}
              onBlur={() => this.props.updateReportName(this.state.reportName)}
            />
          </div>
          <div className={styles['content-bottom']}>
            <span className={styles['title-underline']}></span>
            <div className={styles['controls-container']}>
              <button key="save-button" className={styles['button-main']}>Save report</button>
              {this.state.controlsExpanded && [
                <span key="separator-1" className={styles['controls-separator']}></span>,
                <button key="duplicate-button" className={styles['button-secondary']}>
                  <FontAwesomeIcon icon={faCopy} className={styles['button-icon']} />
                </button>,
                <button key="trash-button" className={styles['button-secondary']}>
                  <FontAwesomeIcon icon={faTrashAlt} className={styles['button-icon']} />
                </button>,
                <button key="pdf-button" className={styles['button-secondary']}>
                  <FontAwesomeIcon icon={faFilePdf} className={styles['button-icon']} />
                </button>,
                <button key="print-button" className={styles['button-secondary']}>
                  <FontAwesomeIcon icon={faPrint} className={styles['button-icon']} />
                </button>,
                <span key="separator-2" className={styles['controls-separator']}></span>,
              ]}
              <button onClick={() => this.expandControls()} key="expand-button" className={cx({ 'button-secondary': true, 'button-more': true})}>
                {this.stateControlsExpanded ? (
                  <FontAwesomeIcon icon={faAngleRight} className={styles['button-icon']} />
                ) : (
                  <FontAwesomeIcon icon={faEllipsisH} className={styles['button-icon']} />
                )}
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }
}

HeaderReport.defaultProps = {

}

const mapStateToProps = (state, ownProps) => ({
  reportName: state.report.reportName,
})

const mapDispatchToProps = dispatch => ({
  updateReportName: newName => dispatch(updateReportName(newName)),
  fetchReport: reportId => dispatch(fetchReport(reportId)),
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(HeaderReport)
