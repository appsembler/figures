import React, { Component } from 'react';
import styles from './_header-content-user.scss';

class HeaderContentUser extends Component {
  render() {

    return (
      <section className={styles['header-content-user']}>
        <img src={this.props.image} alt={this.props.name} role="presentation" className={styles['user-image']} />
      </section>
    );
  }
}

export default HeaderContentUser
