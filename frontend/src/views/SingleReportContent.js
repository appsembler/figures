import React, { Component } from 'react';
import { connect } from 'react-redux';
import {updateReportDescription, updateReportCards } from 'base/redux/actions/Actions';
import classNames from 'classnames/bind';
import styles from './_single-report-content.scss';
import ContentEditable from 'base/components/inputs/ContentEditable'

let cx = classNames.bind(styles);


class SingleReportContent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      reportDescription: this.props.reportDescription,
      reportCards: this.props.reportCards,
      dateCreated: this.props.dateCreated,
      reportAuthor: this.props.reportAuthor,
      reportCarts: this.props.reportCarts,
    };

    this.editReportDescription = this.editReportDescription.bind(this);
  }

  editReportDescription = (evt) => {
    this.setState({
      reportDescription: evt.target.value,
    });
  }

  render() {
    return (
      <div className={cx({ 'container': true, 'base-grid-layout': true, 'report-content': true})}>
        <div className={styles['content-meta']}>
          <div className={styles['meta-description']}>
            <span className={styles['meta-heading']}>
              About this report:
            </span>
            <ContentEditable
              className={styles['report-description']}
              html={this.state.reportDescription}
              dataLabel={'reportDescription'}
              onChange={this.editReportDescription}
              onBlur={() => this.props.updateReportDescription(this.state.reportDescription)}
            />
          </div>
          <div className={styles['meta-date']}>
            <span className={styles['meta-heading']}>
              Date created:
            </span>
            <span className={styles['meta-content']}>
              {this.state.dateCreated}
            </span>
          </div>
          <div className={styles['meta-author']}>
            <span className={styles['meta-heading']}>
              Created by:
            </span>
            <span className={styles['meta-content']}>
              {this.state.reportAuthor}
            </span>
          </div>
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({
  reportName: state.report.reportName,
  dateCreated: state.report.dateCreated,
  reportAuthor: state.report.reportAuthor,
  reportCarts: state.report.reportCarts,
})

const mapDispatchToProps = dispatch => ({
  updateReportDescription: newDescription => dispatch(updateReportDescription(newDescription)),
  updateReportCards: newCards => dispatch(updateReportCards(newCards)),
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(SingleReportContent)
