import React, { Component } from 'react';
import { connect } from 'react-redux';
import {updateReportDescription, updateReportCards } from 'base/redux/actions/Actions';
import classNames from 'classnames/bind';
import styles from './_single-report-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderReport from 'base/components/header-views/header-report/HeaderReport';
import ContentEditable from 'base/components/inputs/ContentEditable';
import {Responsive, WidthProvider} from 'react-grid-layout';

let cx = classNames.bind(styles);
const ResponsiveGridLayout = WidthProvider(Responsive);


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

  componentWillReceiveProps(nextProps) {
    if (this.props !== nextProps) {
      this.setState({
        reportDescription: nextProps.reportDescription,
        reportCards: nextProps.reportCards,
        dateCreated: nextProps.dateCreated,
        reportAuthor: nextProps.reportAuthor,
        reportCarts: nextProps.reportCarts,
      })
    }
  }

  render() {
    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout>
          <HeaderReport
            reportId = {this.props.reportId}
          />
        </HeaderAreaLayout>
        <div className={cx({ 'container': true, 'report-content': true})}>
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
          <ResponsiveGridLayout className={styles['data-wrapper']} rowHeight={20} breakpoints={{xxs: 0}} cols={{xxs: 4}} margin={[30, 30]} compactType='vertical'>
            <div key="a" data-grid={{x: 0, y: 0, w: 1, h: 10, isResizable: false}} style={{background: 'red'}}>Kartica a</div>
            <div key="b" data-grid={{x: 1, y: 0, w: 1, h: 10, isResizable: false}} style={{background: 'blue'}}>Kartica b</div>
            <div key="c" data-grid={{x: 2, y: 0, w: 2, h: 14, isResizable: false}} style={{background: 'green'}}>Kartica c</div>
            <div key="d" data-grid={{x: 0, y: 1, w: 4, h: 12, isResizable: false}} style={{background: 'yellow'}}>Kartica d</div>
          </ResponsiveGridLayout>
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({
  reportDescription: state.report.reportDescription,
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
