import { useState } from "react"
import Sidebar from "./Sidebar"
import ChatArea from "./ChatArea"
import Textbox from "./Textbox"
import SignIn from "./SignIn"

function App() {
  const [user, setUser] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [conversations, setConversations] = useState([
    { id: 1, title: "Beta blockers mechanism", messages: []},
    { id: 2, title: "Krebs cycle summary", messages: [] },
  ])
  const [activeId, setActiveId] = useState(null)
  const [messages, setMessages] = useState([])
  const [started, setStarted] = useState(false)

  if (!user) return <SignIn onSignIn={setUser} />

  // Change setTimeout to an async function
  const sendMessage = async (text) => {
    if (!text.trim()) return
    if (!started) setStarted(true)

    const userMsg = { role: "user", text }
    const updated = [...messages, userMsg]
    setMessages(updated)

    const query = text.replaceAll(" ", "%20")

    try {
      const response = await fetch(`http://127.0.0.1:8000/medLLM_message?query=${query}`)
      const data = await response.text()

      const botMsg = { role: "bot", text: data }
      setMessages(prev => [...prev, botMsg])

      if (activeId) {
        setConversations(prev => prev.map(c =>
          c.id === activeId ? { ...c, messages: [...updated, botMsg] } : c
        ))
      } else {
        const newConvo = {
          id: Date.now(),
          title: text.slice(0, 36) + (text.length > 36 ? "…" : ""),
          messages: [...updated, botMsg]
        }
        setConversations(prev => [newConvo, ...prev])
        setActiveId(newConvo.id)
      }
    } catch (err) {
      const botMsg = { role: "bot", text: "Something went wrong. Is your server running?" }
      setMessages(prev => [...prev, botMsg])
      console.error(err)
    }
  }

  const newChat = () => {
    setMessages([])
    setActiveId(null)
    setStarted(false)
  }

  const loadConvo = (convo) => {
    setMessages(convo.messages)
    setActiveId(convo.id)
    setStarted(convo.messages.length > 0)
  }

  return (
    <div className={`app-layout ${sidebarOpen ? "sidebar-open" : "sidebar-closed"}`}>
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen(o => !o)}
        conversations={conversations}
        activeId={activeId}
        onSelect={loadConvo}
        onNewChat={newChat}
        user={user}
        onSignOut={() => setUser(null)}
      />

      <main className={`main ${started ? "started" : ""}`}>
        {started ? (
          <ChatArea messages={messages} />
        ) : (
          <div className="welcome">
            <h2>What do you want to study?</h2>
            <p>Ask anything — anatomy, biology, chemistry and more.</p>
          </div>
        )}
        <Textbox onSend={sendMessage} />
      </main>
    </div>
  )
}

export default App