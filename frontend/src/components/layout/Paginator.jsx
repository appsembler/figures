import React from 'react';
import PropTypes from 'prop-types';
import Select from 'react-select';
import { List } from 'immutable';
import styles from './_paginator.scss';

const perPageDropdownOptions = List([
  { value: 20, label: '20' },
  { value: 50, label: '50' },
  { value: 100, label: '100' },
])

class Paginator extends React.Component {

  constructor(props: Props) {
    super(props);
    this.state = {
      currentPage: this.props.currentPage,
      perPage: this.props.perPage,
    };
  }

  componentWillReceiveProps(nextProps) {
    if (this.props !== nextProps) {
      this.setState({
        currentPage: nextProps.currentPage,
        perPage: nextProps.perPage,
      });
    }
  }

  render() {

    const pageNumbers = [];

    const numbersToRender = [];
    if (this.props.pages > this.props.ellipsisPageLimit) {
      if ((this.state.currentPage === 1) || (this.state.currentPage === 2)) {
        numbersToRender.push(0, 1, 2, 3, 4, this.props.pages -1, this.props.pages);
      } else if ((this.state.currentPage === this.props.pages - 1) || (this.state.currentPage === this.props.pages)) {
        numbersToRender.push(0, 1, this.props.pages -4, this.props.pages -3, this.props.pages -2, this.props.pages -1, this.props.pages);
      } else {
        numbersToRender.push(0, 1, this.state.currentPage - 1, this.state.currentPage, this.state.currentPage + 1, this.props.pages -1, this.props.pages);
      }
    }
    var renderEllipsis = true;
    for (let i = 0; i < this.props.pages; i++) {
      const page = i + 1;
      const buttonClass = (page !== this.state.currentPage) ? styles['number-item'] : styles['number-item-active'];
      if (this.props.pages > this.props.ellipsisPageLimit) {
        if (numbersToRender.includes(i)) {
          pageNumbers.push(
            <button
              className={buttonClass}
              onClick={() => this.props.pageSwitchFunction(page)}
            >
              {page}
            </button>
          )
          renderEllipsis = true;
        } else {
          if (renderEllipsis) {
            pageNumbers.push(
              <span className={styles['ellipsis-item']}>...</span>
            )
            renderEllipsis = false;
          }
        }
      } else {
        pageNumbers.push(
          <button
            className={buttonClass}
            onClick={() => this.props.pageSwitchFunction(i+1)}
          >
            {i+1}
          </button>
        )
      }
    }

    return (
      <div className={styles['paginator']}>
        <div className={styles['number-controls-container']}>
          {(this.state.currentPage !== 1) ? (
            <button
              className={styles['text-item']}
              onClick={() => this.props.pageSwitchFunction(1)}
            >
              First
            </button>
          ) : (
            <span
              className={styles['text-item-dummy']}
            >
              First
            </span>
          )}
          {(this.state.currentPage !== 1) ? (
            <button
              className={styles['text-item']}
              onClick={() => this.props.pageSwitchFunction(this.props.currentPage-1)}
            >
              Previous
            </button>
          ) : (
            <span
              className={styles['text-item-dummy']}
            >
              Previous
            </span>
          )}
          {pageNumbers}
          {(this.state.currentPage !== this.props.pages) ? (
            <button
              className={styles['text-item']}
              onClick={() => this.props.pageSwitchFunction(this.props.currentPage+1)}
            >
              Next
            </button>
          ) : (
            <span
              className={styles['text-item-dummy']}
            >
              Next
            </span>
          )}
          {(this.state.currentPage !== this.props.pages) ? (
            <button
              className={styles['text-item']}
              onClick={() => this.props.pageSwitchFunction(this.props.pages)}
            >
              Last
            </button>
          ) : (
            <span
              className={styles['text-item-dummy']}
            >
              Last
            </span>
          )}
        </div>
        <div className={styles['dropdown-controls-container']}>
          <span className={styles['paginator-dropdown-label']}>
            Per page:
          </span>
          <div className={styles['dropdown-inner-container']}>
            <Select
              options={perPageDropdownOptions.toArray()}
              onChange = {(payload) => this.props.changePerPageFunction(payload.value)}
              value={perPageDropdownOptions.get(perPageDropdownOptions.findIndex(item => (item.value === this.state.perPage)))}
            />
          </div>
        </div>
      </div>
    );
  }
}

Paginator.defaultProps = {
  perPage: 20,
  ellipsisPageLimit: 9,
};

Paginator.propTypes = {
  pages: PropTypes.number,
  pageSwitchFunction: PropTypes.func,
  changePerPageFunction: PropTypes.func,
  perPage: PropTypes.number,
  currentPage: PropTypes.number,
};

export default Paginator;
