import React, { Component } from 'react';
import classNames from 'classnames/bind';
import PropTypes from 'prop-types';
import styles from './_header-content-static.scss';

let cx = classNames.bind(styles);

class HeaderContentStatic extends Component {
  render() {

    return (
      <section className={cx({ 'header-content-static': true, 'container': true})}>
        <h1 className={styles['title']}>{this.props.title}</h1>
        <p className={styles['subtitle']}>{this.props.subtitle}</p>
      </section>
    );
  }
}

HeaderContentStatic.defaultProps = {
  title: 'Static page header',
  subtitle: 'Static page header subtitle.'
}

HeaderContentStatic.propTypes = {
  title: PropTypes.string,
  subtitle: PropTypes.string
};

export default HeaderContentStatic
