import { useAuth0 } from "@auth0/auth0-react"

function Sidebar({ open, onToggle, conversations, activeId, onSelect, onNewChat}) {
    const { logout, user } = useAuth0()   // get user and logout from Auth0
    const handleSignOut = () => logout({ logoutParams: { returnTo: window.location.origin } })
    return (
      <aside className={`sidebar ${open ? "open" : "closed"}`}>
        <div className="sidebar-top">
          <button className="icon-btn toggle-btn" onClick={onToggle} title="Toggle sidebar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
          {open && (
            <button className="new-chat-btn" onClick={onNewChat}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              New chat
            </button>
          )}
        </div>
  
        {open && (
          <>
            <div className="sidebar-label">Recent</div>
            <nav className="convo-list">
              {conversations.map(c => (
                <button
                  key={c.id}
                  className={`convo-item ${c.id === activeId ? "active" : ""}`}
                  onClick={() => onSelect(c)}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                  </svg>
                  <span>{c.title}</span>
                </button>
              ))}
            </nav>
          </>
        )}
  
        <div className="sidebar-bottom">
          {open ? (
            <div className="user-row">
              <div className="avatar">{user.name[0].toUpperCase()}</div>
              <div className="user-info">
                <p className="user-name">{user.name}</p>
                <p className="user-email">{user.email}</p>
              </div>
              <button className="icon-btn signout-btn" onClick={handleSignOut} title="Sign out">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                  <polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
              </button>
            </div>
          ) : (
            <button className="icon-btn avatar-icon" onClick={handleSignOut} title="Sign out">
              <div className="avatar small">{user.name[0].toUpperCase()}</div>
            </button>
          )}
        </div>
      </aside>
    )
  }
  
  export default Sidebar