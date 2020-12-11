import React, { Component } from 'react';
import Immutable from 'immutable';
import { Link } from 'react-router-dom';
import apiConfig from 'base/apiConfig';
import { trackPromise } from 'react-promise-tracker';
import styles from './_progress-overview-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentStatic from 'base/components/header-views/header-content-static/HeaderContentStatic';
import Paginator from 'base/components/layout/Paginator';
import ListSearch from 'base/components/inputs/ListSearch';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faAngleDoubleUp, faAngleDoubleDown } from '@fortawesome/free-solid-svg-icons';
import { ExportToCsv } from 'export-to-csv';
import { Multiselect } from 'multiselect-react-dropdown';

import classNames from 'classnames/bind';
let cx = classNames.bind(styles);

class ProgressOverview extends Component {
  constructor(props) {
    super(props);

    this.state = {
      learnersList: [],
      selectedCourses: [],
      coursesFilterOptions: [],
      perPage: 20,
      count: 0,
      pages: 0,
      currentPage: 1,
      searchQuery: '',
      ordering: 'profile__name',
      selectedCourseIds: '',
      csvExportProgress: 0,
      wideView: false,
    };
    this.fetchFullViewData = this.fetchFullViewData.bind(this);
    this.getUsersForCsv = this.getUsersForCsv.bind(this);
  }

  constructApiUrl = (rootUrl, searchQuery, selectedCourseIds, orderingType, perPageLimit, resultsOffset) => {
    let requestUrl = rootUrl;
    // add search term
    requestUrl += '?search=' + searchQuery;
    // optionally add course filtering
    if (selectedCourseIds) {
      requestUrl += '&course=' + selectedCourseIds;
    }
    // add ordering
    requestUrl += '&ordering=' + orderingType;
    // add results per page limit
    requestUrl += '&limit=' + perPageLimit;
    // add results offset
    requestUrl += '&offset=' + resultsOffset;
    // return
    return requestUrl;
  }

  getCourses = () => {
    const requestUrl = apiConfig.coursesIndex + '?limit=1000';
    trackPromise(
      fetch((requestUrl), { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => this.setCoursesIndex(json['results']))
    )
  }

  setCoursesIndex = (courses) => {
    const coursesFilterOptions = courses.map((course, index) => {
      const entry = {
        id: course.id,
        label: `${course.name} | ${course.number} | ${course.id}`,
        name: course.name,
        number: course.number,
        id: course.id,
      }
      return (
        entry
      )
    })
    this.setState({
      coursesFilterOptions: coursesFilterOptions,
    })
  }

  getUsers = (page = 1) => {
    const offset = (page-1) * this.state.perPage;
    const requestUrl = this.constructApiUrl(apiConfig.learnerMetrics, this.state.searchQuery, this.state.selectedCourseIds, this.state.ordering, this.state.perPage, offset);
    trackPromise(
      fetch((requestUrl), { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => this.setState({
          learnersList: json['results'],
          count: json['count'],
          pages: Math.ceil(json['count'] / this.state.perPage),
          currentPage: page,
        })
      )
    )
  }

  setPerPage = (newValue) => {
    this.setState({
      perPage: newValue,
    }, () => {
      (this.state.selectedCourses.length || this.state.searchQuery) && this.getUsers();
    })
  }

  setSearchQuery = (newValue) => {
    this.setState({
      searchQuery: newValue
    }, () => {
      (this.state.selectedCourses.length || this.state.searchQuery) && this.getUsers();
    })
  }

  setOrdering = (newValue) => {
    this.setState({
      ordering: newValue
    }, () => {
      (this.state.selectedCourses.length || this.state.searchQuery) && this.getUsers();
    })
  }

  onChangeSelectedCourses = (selectedList, item) => {
    const selectedIdsList = selectedList.map((course, index) => {
      return course.id;
    });
    const selectedCourseIds = selectedIdsList.join('&course=');
    this.setState({
      selectedCourses: selectedList,
      selectedCourseIds: selectedCourseIds,
    }, () => {
      (this.state.selectedCourses.length || this.state.searchQuery) && this.getUsers();
    })
  }

  startCsvExport = () => {
    this.setState({
      csvExportProgress: 0.01,
    }, async () => {
      const allData = await this.fetchFullViewData();
      this.exportViewToCsv(allData);
    })
  }

  async fetchFullViewData(page = 1) {
    const results = await this.getUsersForCsv(page);
    this.setState({
      csvExportProgress: (100 * (page - 1) / this.state.count) + 0.01,
    })
    console.log("Retreiving data from API for page : " + page);
    if (results.length > 0) {
      return results.concat(await this.fetchFullViewData(page+1));
    } else {
      return results;
    }
  }

  async getUsersForCsv(page = 1) {
    const offset = (page-1) * 100;
    const requestUrl = this.constructApiUrl(apiConfig.learnerMetrics, this.state.searchQuery, this.state.selectedCourseIds, this.state.ordering, 100, offset);
    var apiResults = await fetch((requestUrl), { credentials: "same-origin" })
      .then(response => response.json())
      .then(json => {return json['results']})
    return apiResults;
  }

  exportViewToCsv = (data) => {
    const options = {
      fieldSeparator: ',',
      quoteStrings: '"',
      decimalSeparator: '.',
      showLabels: true,
      showTitle: true,
      title: 'Learners progress overview',
      filename: 'CSV Export',
      useTextFile: false,
      useBom: true,
      useKeysAsHeaders: true,
    };
    const csvExporter = new ExportToCsv(options);
    const schemaData = this.convertJsonToCsvSchema(data);
    csvExporter.generateCsv(schemaData);
  }

  convertJsonToCsvSchema = (jsonData) => {
    const csvTestVar = jsonData.map((user, index) => {
      const singleRecord = {};
      singleRecord['name'] = user['fullname'];
      singleRecord['email'] = user['email'];
      singleRecord['username'] = user['username'];
      singleRecord['date_joined'] = user['date_joined'];

      const coursesFilter = this.state.selectedCourses.length ? this.state.selectedCourses : this.state.coursesFilterOptions;
      const userCoursesImmutable = Immutable.fromJS(user['enrollmentdata_set']);
      coursesFilter.forEach((course, i) => {
        const userProgress = userCoursesImmutable.find(singleCourse => singleCourse.get('course_id') === course.id);
        if (userProgress) {

          const progressPercent = (userProgress.getIn(['progress_percent'])) ? userProgress.getIn(['progress_percent']).toFixed(2) : '-';
          const sectionsWorked = (userProgress.getIn(['progress_details', 'sections_worked'])) ? userProgress.getIn(['progress_details', 'sections_worked']).toFixed(1) : '-';
          const sectionsPossible = (userProgress.getIn(['progress_details', 'sections_possible'])) ? userProgress.getIn(['progress_details', 'sections_possible']).toFixed(1) : '-';
          const pointsEarned = (userProgress.getIn(['progress_details', 'points_earned'])) ? userProgress.getIn(['progress_details', 'points_earned']).toFixed(1) : '-';
          const pointsPossible = (userProgress.getIn(['progress_details', 'points_possible'])) ? userProgress.getIn(['progress_details', 'points_possible']).toFixed(1) : '-';

          singleRecord[course.id] = `Progress: ${progressPercent}/1 | Sections: ${sectionsWorked}/${sectionsPossible} | Points: ${pointsEarned}/${pointsPossible}`;
        } else {
          singleRecord[course.id] = '-';
        };
      })
      return singleRecord;
    })
    return csvTestVar;
  }

  toggleWideView = () => {
    this.setState({
      wideView: !this.state.wideView
    })
  }

  componentDidMount() {
    this.getCourses();
  }

  render() {

    const coursesFilter = this.state.selectedCourses.length ? this.state.selectedCourses : this.state.coursesFilterOptions;

    const headerCourseColumns = coursesFilter.map((course, index) => {
      return(
        <div className={styles['course-info-column-header']}>
          <span className={styles['course-name']}>
            {course['name']}
          </span>
          <span className={styles['course-id']}>
            {course['id']}
          </span>
        </div>
      )
    })

    const floatingListItems = this.state.learnersList.map((user, index) => {
      return (
        <li key={`floating+${user['id']}`} className={styles['user-list-item']}>
          <div className={styles['user-fullname']}>
            <Link
              className={styles['user-fullname-link']}
              to={'/figures/user/' + user['id']}
            >
              <span className={styles['user-info-value']}>
                {user['fullname']}
              </span>
            </Link>
          </div>
        </li>
      )
    });

    const scrollingListItems = this.state.learnersList.map((user, index) => {

      const userCoursesImmutable = Immutable.fromJS(user['enrollmentdata_set']);
      const userCoursesRender = coursesFilter.map((course, i) => {
        const userProgress = userCoursesImmutable.find(singleCourse => singleCourse.get('course_id') === course.id);
        return (
          <div className={styles['single-course-progress']}>
            {userProgress ? [
              <div className={styles['data-group']}>
                <span className={styles['data-label']}>Sections</span>
                <span className={styles['data']}>{userProgress.getIn(['progress_details', 'sections_worked']) ? userProgress.getIn(['progress_details', 'sections_worked']).toFixed(1) : '-'}/{userProgress.getIn(['progress_details', 'sections_possible']) ? userProgress.getIn(['progress_details', 'sections_possible']).toFixed(1) : '-'}</span>
              </div>,
              <div className={styles['data-group']}>
                <span className={styles['data-label']}>Points</span>
                <span className={styles['data']}>{userProgress.getIn(['progress_details', 'points_earned']) ? userProgress.getIn(['progress_details', 'points_earned']).toFixed(1) : '-'}/{userProgress.getIn(['progress_details', 'points_possible']) ? userProgress.getIn(['progress_details', 'points_possible']).toFixed(1) : '-'}</span>
              </div>,
              <div className={styles['data-group']}>
                <span className={styles['data-label']}>Progress</span>
                <span className={styles['data']}>{(userProgress.getIn(['progress_percent'])*100).toFixed(0)}%</span>
              </div>
            ] : (
              <span className={styles['no-data']}>-</span>
            )}
          </div>
        )
      })

      return (
        <li key={`scrolling+${user['id']}`} className={styles['user-list-item']}>
          <div className={styles['username']}>
            <span className={styles['user-info-value']}>
              {user['username']}
            </span>
          </div>
          <div className={styles['email']}>
            <span className={styles['user-info-value']}>
              {user['email']}
            </span>
          </div>
          {userCoursesRender}
        </li>
      )
    })


    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout>
          <HeaderContentStatic
            title='Learners progress overview'
            subtitle={'This view allows you to view a snapshot of your sites learners progress. Total number of results in current view is: ' + this.state.count + '. You can also filter down the results in the view, then export the data in the view as a CSV file on-the-fly.'}
          />
        </HeaderAreaLayout>
        {this.state.csvExportProgress ? (
          <div className={cx({ 'container': true, 'csv-export-content': true})}>
            {(this.state.csvExportProgress < 1) ? [
              <h2>Exporting your CSV data...</h2>,
              <p>Please don't close this browser tab.</p>
            ] : [
              <h2>Export successful!</h2>,
              <p>Depending on your browser settings, you will either be prompted with a prompt to save the generated file, or the file will be automatically downloaded into your default Downloads folder.</p>,
              <p>It is now safe to close the exporter.</p>,
            ]}
            <div className={styles['progress-bar']}>
              <span className={styles['progress-bar-inner']} style={{ width: this.state.csvExportProgress * 100 + '%'}}></span>
            </div>
            {(this.state.csvExportProgress < 1) ? (
              <span className={styles['percentage']}>
                {(this.state.csvExportProgress * 100).toFixed(0)}%
              </span>
            ) : (
              <button
                className={styles['close-csv-button']}
                onClick = {() => this.setState({ csvExportProgress: 0 })}
              >
                Close the exporter
              </button>
            )}
          </div>
        ) : (
          <div className={cx({ 'container-max': this.state.wideView, 'container': !this.state.wideView, 'users-content': true})}>
            <div className={styles['refining-container']}>
              <div className={styles['refining-container__filters']}>
                <ListSearch
                  valueChangeFunction={this.setSearchQuery}
                  waitInterval={2000}
                  inputPlaceholder='Search by users name, username or email...'
                />
                <div className={styles['multiselect-container']}>
                  <Multiselect
                    options={this.state.coursesFilterOptions}
                    selectedValues={this.state.selectedCourses}
                    onSelect={this.onChangeSelectedCourses}
                    onRemove={this.onChangeSelectedCourses}
                    displayValue="label"
                    placeholder="Filter by courses..."
                    style={{ chips: { background: "#0090c1" }, searchBox: { border: "none", "border-bottom": "1px solid #ccc", "border-radius": "0px", "font-size": "14px", "padding-top": "13px", "padding-bottom": "13px" }, option: { "font-size": "14px" } }}
                  />
                </div>
              </div>
              {(this.state.selectedCourses.length || this.state.searchQuery) ? (
                <button
                  className={styles['export-the-csv-button']}
                  onClick = {() => this.startCsvExport()}
                >
                  Generate a CSV from Current View
                </button>
              ) : ''}
            </div>
            {this.state.pages ? (
              <div className={styles['view-controls-container']}>
                <Paginator
                  pageSwitchFunction={this.getUsers}
                  currentPage={this.state.currentPage}
                  perPage={this.state.perPage}
                  pages={this.state.pages}
                  changePerPageFunction={this.setPerPage}
                />
                <button
                  className={styles['toggle-wide-view-button']}
                  onClick = {() => this.toggleWideView()}
                >
                  {this.state.wideView ? 'Switch to narrow view' : 'Switch to wide view'}
                </button>
              </div>
            ) : ''}
            {(this.state.selectedCourses.length || this.state.searchQuery) ? (
              <div className={styles['users-overview-list']}>
                <ul className={styles['list-floating-columns']}>
                  <li key='list-header' className={cx(styles['user-list-item'], styles['list-header'])}>
                    <div className={styles['user-fullname']}>
                      <button
                        className={styles['sorting-header-button']}
                        onClick={() => (this.state.ordering !== 'profile__name') ? this.setOrdering('profile__name') : this.setOrdering('-profile__name')}
                      >
                        <span>
                          User full name
                        </span>
                        {(this.state.ordering === 'profile__name') ? (
                          <FontAwesomeIcon icon={faAngleDoubleUp} />
                        ) : (this.state.ordering === '-profile__name') ? (
                          <FontAwesomeIcon icon={faAngleDoubleDown} />
                        ) : ''}
                      </button>
                    </div>
                  </li>
                  {floatingListItems}
                </ul>
                <ul className={styles['list-scrolling-columns']}>
                  <li key='list-header' className={cx(styles['user-list-item'], styles['list-header'])}>
                    <div className={styles['username']}>
                      <button
                        className={styles['sorting-header-button']}
                        onClick={() => (this.state.ordering !== 'username') ? this.setOrdering('username') : this.setOrdering('-username')}
                      >
                        <span>
                          Username
                        </span>
                        {(this.state.ordering === 'username') ? (
                          <FontAwesomeIcon icon={faAngleDoubleUp} />
                        ) : (this.state.ordering === '-username') ? (
                          <FontAwesomeIcon icon={faAngleDoubleDown} />
                        ) : ''}
                      </button>
                    </div>
                    <div className={styles['email']}>
                      <button
                        className={styles['sorting-header-button']}
                        onClick={() => (this.state.ordering !== 'email') ? this.setOrdering('email') : this.setOrdering('-email')}
                      >
                        <span>
                          Email
                        </span>
                        {(this.state.ordering === 'email') ? (
                          <FontAwesomeIcon icon={faAngleDoubleUp} />
                        ) : (this.state.ordering === '-email') ? (
                          <FontAwesomeIcon icon={faAngleDoubleDown} />
                        ) : ''}
                      </button>
                    </div>
                    {headerCourseColumns}
                  </li>
                  {scrollingListItems}
                </ul>
              </div>
            ) : (
              <div className={styles['no-data-message']}>
                Enter a search term and/or select course(s) to display the data.
              </div>
            )}
            {this.state.pages ? (
              <Paginator
                pageSwitchFunction={this.getUsers}
                currentPage={this.state.currentPage}
                perPage={this.state.perPage}
                pages={this.state.pages}
                changePerPageFunction={this.setPerPage}
              />
            ) : ''}
          </div>
        )}
      </div>
    );
  }
}

export default ProgressOverview
