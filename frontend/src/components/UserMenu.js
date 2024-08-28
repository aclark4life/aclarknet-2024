// UserMenu.js
import React from 'react';
import PropTypes from 'prop-types';

function handleLogout() {
    window.location.href = '/accounts/logout';
}

const UserMenu = ({ isAuthenticated, isSuperuser }) => {
  return (
    <div> 
      {isAuthenticated ? (
        <li className="nav-item dropdown text-nowrap">
          <a className="nav-link text-light text-uppercase exclude-from-hover" type="button" aria-expanded="false" href="/dashboard">
            <i className="fa-solid fa-leaf me-1"></i> 
            <span className="d-none d-lg-inline">Dashboard</span>
            <span className="visually-hidden">Link text</span>
          </a>
          <ul className="dropdown-menu">
            <li><a className="dropdown-item" href="/user/profile">Profile</a></li>
            <li><a className="dropdown-item" href="/dashboard/time/create/">Add Time</a></li>
            {isSuperuser ? (
              <>
                <li><hr className="dropdown-divider"></hr></li>
                <li><a className="dropdown-item" href="https://aclarknet.signin.aws.amazon.com/console" rel="noreferrer" target="_blank">AWS Console</a></li>
                <li><a className="dropdown-item" href="/blog">Puput Blog</a></li>
                <li><a className="dropdown-item" href="/django" target="_blank">Django Admin</a></li>
                <li><a className="dropdown-item" href="https://analytics.google.com" rel="noreferrer" target="_blank">Google Analytics</a></li>
                <li><a className="dropdown-item" href="https://admin.google.com/ac/home?hl=en" rel="noreferrer" target="_blank">Google Workspace</a></li>
                <li><a className="dropdown-item" href="/lounge" target="_blank">Lounge IRC</a></li>
                <li><a className="dropdown-item" href="https://logfire.pydantic.dev/aclark4life/aclarknet" rel="noreferrer" target="_blank">Pydantic Logfire</a></li>
                <li><a className="dropdown-item" href="/explorer" target="_blank">SQL Explorer</a></li>
                <li><a className="dropdown-item" href="/wagtail" target="_blank">Wagtail Admin</a></li>
              </>
            ) : null}
            <li><hr className="dropdown-divider"></hr></li>
            <li><a className="dropdown-item" href="/accounts/logout">Logout</a></li>
          </ul>
        </li>
      ) : (
        <li className="nav-item">
          <a className="nav-link text-light text-uppercase exclude-from-hover" href="/accounts/login">
            <i className="fa-solid fa-leaf me-1"></i> 
            <span className="visually-hidden">Link text</span>
          </a>
        </li>
      )}
    </div>
  );
};

UserMenu.propTypes = {
  isAuthenticated: PropTypes.bool.isRequired,
  isSuperuser: PropTypes.bool.isRequired,
};

export default UserMenu;
