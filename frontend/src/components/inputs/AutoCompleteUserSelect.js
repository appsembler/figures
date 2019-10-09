import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import Autosuggest from 'react-autosuggest';
import { Link } from 'react-router-dom';
import styles from './_autocomplete-user-select.scss';
import classNames from 'classnames/bind';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faTimes } from '@fortawesome/free-solid-svg-icons';

let cx = classNames.bind(styles);

var usersList = [
];

const getSuggestions = value => {
  const inputValue = value.trim().toLowerCase();
  const inputLength = inputValue.length;
  return inputLength === usersList ? [] : usersList.filter(user => ((user.userName.toLowerCase().slice(0, inputLength) === inputValue) || (user.userUsername.toLowerCase().slice(0, inputLength) === inputValue))).toArray();
};

const getSuggestionValue = suggestion => suggestion.userName;

class AutoCompleteUserSelect extends Component {
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

    usersList = this.props.usersIndex.map((item, index) => {
      return {
        userId: item['id'],
        userName: item['fullname'] ? item['fullname'] : item['username'],
        userUsername: item['username']
      }
    })

    const renderSuggestion = suggestion => (
      <Link className={styles['suggestion-link']} to={'/figures/user/' + suggestion.userId} onClick={this.modalTrigger}><span className={styles['suggestion-link__user-username']}>{suggestion.userUsername}</span><span className={styles['suggestion-link__user-name']}>{suggestion.userName}</span></Link>
    );


    return (
      <div className={styles['ac-user-selector']}>
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

AutoCompleteUserSelect.defaultProps = {
  negativeStyleButton: false,
  buttonText: 'Select a user',
  inputPlaceholder: 'Select or start typing',
}

AutoCompleteUserSelect.propTypes = {
  negativeStyleButton: PropTypes.bool,
  buttonText: PropTypes.string,
  inputPlaceholder: PropTypes.string
};

const mapStateToProps = (state, ownProps) => ({
  usersIndex: state.usersIndex.usersIndex,
})

export default connect(
  mapStateToProps
)(AutoCompleteUserSelect)
