import React, { Component } from 'react';
import PropTypes from 'prop-types';
import styles from './_list-search.scss';
import classNames from 'classnames/bind';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSearch, faTimes } from '@fortawesome/free-solid-svg-icons';

let cx = classNames.bind(styles);


class ListSearch extends Component {
  constructor(props) {
    super(props);

    this.state = {
      value: '',
    };

    this.onChange = this.onChange.bind(this);
    this.clearInput = this.clearInput.bind(this);
    this.passValue = this.passValue.bind(this);
  }

  onChange = (newValue) => {
    clearTimeout(this.timer);
    this.setState({
      value: newValue
    });
    this.timer = setTimeout(this.passValue, this.props.waitInterval);
  };

  clearInput = () => {
    this.setState({
      value: ''
    }, () => this.props.valueChangeFunction(''))
  }

  passValue = () => {
    this.props.valueChangeFunction(this.state.value);
  }

  componentWillMount() {
    this.timer = null;
  }



  render() {

    return (
      <div className={styles['list-search']}>
        <div className={cx({ 'inner-container': true, 'active': (this.state.value !== '')})}>
          <FontAwesomeIcon icon={faSearch} className={styles['search-icon']} />
          <input
            type="text"
            className={styles['list-search-input']}
            value={this.state.value}
            onChange={(e) => this.onChange(e.target.value)}
            placeholder={this.props.inputPlaceholder}
          />
          {this.state.value ? (
            <button className={styles['clear-button']} onClick={() => this.clearInput()}>
              <FontAwesomeIcon icon={faTimes} className={styles['clear-icon']} />
            </button>
          ) : ''}
        </div>
      </div>
    )
  }
}

ListSearch.defaultProps = {
  waitInterval: 1000,
  inputPlaceholder: 'Start typing...',
}

ListSearch.propTypes = {
  negativeStyleButton: PropTypes.bool,
  buttonText: PropTypes.string,
  inputPlaceholder: PropTypes.string
};

export default ListSearch
