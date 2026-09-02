import {
  NavLink,
  Outlet,
} from 'react-router-dom'


const navigationItems = [
  {
    label: 'Dashboard',
    path: '/dashboard',
  },
  {
    label: 'Investments',
    path: '/investments',
  },
  {
    label: 'Transactions',
    path: '/transactions',
  },
  {
    label: 'Dividends',
    path: '/dividends',
  },
  {
    label: 'Import',
    path: '/import',
  },
]


function AppLayout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">
            EK
          </div>

          <div>
            <div className="sidebar-title">
              EK Finance OS
            </div>

            <div className="sidebar-subtitle">
              Personal Finance
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {
            navigationItems.map(
              (item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={
                    ({ isActive }) =>
                      isActive
                        ? 'nav-item active'
                        : 'nav-item'
                  }
                >
                  {item.label}
                </NavLink>
              ),
            )
          }
        </nav>

        <div className="sidebar-footer">
          EK Finance OS v1
        </div>
      </aside>

      <div className="layout-content">
        <header className="topbar">
          <div>
            Portfolio Management
          </div>

          <div className="topbar-status">
            ● Backend connected
          </div>
        </header>

        <div className="page-content">
          <Outlet />
        </div>
      </div>
    </div>
  )
}


export default AppLayout