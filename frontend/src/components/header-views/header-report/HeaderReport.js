import React, { Component } from 'react';
import classNames from 'classnames/bind';
import styles from './_header-report.scss';
import ContentEditable from 'base/components/inputs/ContentEditable'
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import { faCopy, faTrashAlt, faFilePdf, faPrint, faAngleRight, faEllipsisH } from '@fortawesome/fontawesome-free-solid';

let cx = classNames.bind(styles);

class HeaderContentCourse extends Component {
  constructor(props) {
    super(props);

    this.state = {
      reportData: {},
      editedDataLabel: '',
      controlsExpanded: false,
    };

    this.getDataFromApi = this.getDataFromApi.bind(this);
    this.editReportData = this.editReportData.bind(this);
    this.pushNewReportData = this.pushNewReportData.bind(this);
  }

  getDataFromApi = () => {
    const retrievedReportData = {
      reportTitle: 'My report with the ID "' + this.props.reportId + '".',
    }
    this.setState({
      reportData: retrievedReportData,
    });
  }

  editReportData = (evt) => {
    const newData = this.state.reportData;
    newData[evt.target.dataLabel] = evt.target.value;
    console.log(newData);
    this.setState({
      reportData: newData,
    });
  }

  pushNewReportData = () => {
    console.log('Pushing new data to the DB: ', this.state.reportData);
  }

  expandControls = () => {
    this.setState({
      controlsExpanded: !this.state.controlsExpanded,
    });
  }

  componentDidMount() {
    this.getDataFromApi(this.props.reportId);
  }

  render() {

    return (
      <section className={styles['header-content-report']}>
        <div className={cx({ 'main-content': true, 'container': true})}>
          <div className={styles['content-top']}>
            <ContentEditable
              className={styles['report-title']}
              html={this.state.reportData.reportTitle}
              dataLabel={'reportTitle'}
              onChange={this.editReportData}
              onBlur={this.pushNewReportData}
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

HeaderContentCourse.defaultProps = {

}

export default HeaderContentCourse;
