import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import Autosuggest from 'react-autosuggest';
import { Link } from 'react-router-dom';
import styles from './_autocomplete-course-select.scss';
import classNames from 'classnames/bind';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faTimes } from '@fortawesome/free-solid-svg-icons';

let cx = classNames.bind(styles);

var coursesList = [
];

const getSuggestions = value => {
  const inputValue = value.trim().toLowerCase();
  const inputLength = inputValue.length;
  return inputLength === coursesList ? [] : coursesList.filter(course => ((course.courseName.toLowerCase().slice(0, inputLength) === inputValue) || (course.courseNumber.toLowerCase().slice(0, inputLength) === inputValue))).toArray();
};

const getSuggestionValue = suggestion => suggestion.courseName;

class AutoCompleteCourseSelect extends Component {
  constructor(props) {
    super(props);

    this.state = {
      value: '',
      suggestions: [],
      modalActive: false,
    };

    this.onChange = this.onChange.bind(this);
    this.modalTrigger = this.modalTrigger.bind(this);
    this.storeInputReference = this.storeInputReference.bind(this);
  }

  modalTrigger = () => {
    this.setState({
      modalActive: !this.state.modalActive,
      value: ''
    }, () => {
      this.state.modalActive && this.input.focus();
    });
  }

  onChange = (event, { newValue }) => {
    this.setState({
      value: newValue
    });
  };

  onSuggestionsClearRequested = () => {

  }

  onSuggestionSelected = () => {
    this.setState({
      modalActive: false,
      value: '',
      suggestions: [],
    });
  }

  onSuggestionsFetchRequested = ({ value }) => {
    this.setState({
      suggestions: getSuggestions(value)
    });
  };

  storeInputReference = autosuggest => {
    if (autosuggest !== null) {
      this.input = autosuggest.input;
    }
  };

  render() {
    const { value, suggestions } = this.state;

    const inputProps = {
      placeholder: this.props.inputPlaceholder,
      value,
      onChange: this.onChange
    };

    coursesList = this.props.coursesIndex.map((item, index) => {
      return {
        courseId: item['course_id'],
        courseName: item['course_name'],
        courseNumber: item['course_code']
      }
    })

    const renderSuggestion = suggestion => (
      <Link className={styles['suggestion-link']} to={'/figures/course/' + suggestion.courseId} onClick={this.modalTrigger}>
        <div className={styles['suggestion-link__link-upper']}>
          <span className={styles['suggestion-link__course-number']}>{suggestion.courseNumber}</span>
          <span className={styles['suggestion-link__course-id']}>{suggestion.courseId}</span>
        </div>
        <span className={styles['suggestion-link__course-name']}>{suggestion.courseName}</span>
      </Link>
    );


    return (
      <div className={styles['ac-course-selector']}>
        <button onClick={this.modalTrigger} className={cx({ 'selector-trigger-button': true, 'positive': !this.props.negativeStyleButton, 'negative': this.props.negativeStyleButton })}>{this.props.buttonText}</button>
        {this.state.modalActive && (
          <div className={styles['selector-modal']}>
            <Autosuggest
              suggestions = {suggestions}
              onSuggestionsFetchRequested = {this.onSuggestionsFetchRequested}
              onSuggestionsClearRequested = {this.onSuggestionsClearRequested}
              getSuggestionValue = {getSuggestionValue}
              renderSuggestion = {renderSuggestion}
              inputProps = {inputProps}
              theme = {styles}
              alwaysRenderSuggestions
              ref={this.storeInputReference}
            />
            <button onClick={this.modalTrigger} className={styles['modal-dismiss']}><FontAwesomeIcon icon={faTimes}/></button>
          </div>
        )}
        {this.state.modalActive && <div className={styles['selector-backdrop']} onClick={this.modalTrigger}></div>}
      </div>
    )
  }
}

AutoCompleteCourseSelect.defaultProps = {
  negativeStyleButton: false,
  buttonText: 'Select a course',
  inputPlaceholder: 'Select or start typing',
  coursesList: [
    {
      courseId: 'A101',
      courseName: 'This is the name of the course'
    },
    {
      courseId: 'A102',
      courseName: 'This is another name of the course'
    },
    {
      courseId: 'A103',
      courseName: 'My introduction to EdX Figures'
    },
    {
      courseId: 'A101',
      courseName: 'This is the name of the course'
    },
    {
      courseId: 'A102',
      courseName: 'This is another name of the course'
    },
    {
      courseId: 'A103',
      courseName: 'My introduction to EdX Figures'
    },
    {
      courseId: 'A101',
      courseName: 'This is the name of the course'
    },
    {
      courseId: 'A102',
      courseName: 'This is another name of the course'
    },
    {
      courseId: 'A103',
      courseName: 'My introduction to EdX Figures'
    }
  ]
}

AutoCompleteCourseSelect.propTypes = {
  negativeStyleButton: PropTypes.bool,
  buttonText: PropTypes.string,
  inputPlaceholder: PropTypes.string,
  coursesList: PropTypes.array
};

const mapStateToProps = (state, ownProps) => ({
  coursesIndex: state.coursesIndex.coursesIndex,
})

export default connect(
  mapStateToProps
)(AutoCompleteCourseSelect)
