import { useState, useEffect } from "react"
import Sidebar from "./Sidebar"
import ChatArea from "./ChatArea"
import Textbox from "./Textbox"
import SignIn from "./SignIn"
import { useAuth0 } from "@auth0/auth0-react"

function App() {
  const {isAuthenticated, isLoading, user} = useAuth0()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [conversations, setConversations] = useState([])
  const [activeId, setActiveId] = useState(null)
  const [messages, setMessages] = useState([])
  const [started, setStarted] = useState(false)
  const [isThinking, setIsThinking] = useState(false)

  useEffect(() => {
    if (!user) return
    
    const loadConversations = async () => {
      const res = await fetch(`http://127.0.0.1:8000/get_conversations?auth0_id=${user.sub}`)
      const data = await res.json()
      
      setConversations(data.conversations.map(c => ({
        id: c.id,
        title: c.title,
        messages: []
      })))
    }
    
    loadConversations()
  }, [user])

  if (isLoading) return <div className="loading">Loading...</div>
  if (!isAuthenticated) return <SignIn /> 

  const loadConvo = async (convo) => {
    if (convo.messages.length > 0) {
      setMessages(convo.messages)
      setActiveId(convo.id)
      setStarted(true)
      return
    }
  
    const res = await fetch(`http://127.0.0.1:8000/get_messages?conversation_id=${convo.id}`)
    const data = await res.json()
  
    const loaded = data.messages.map(m => ({
      role: m.role,
      text: m.content
    }))
  
    setMessages(loaded)
    setActiveId(convo.id)
    setStarted(true)
  
    setConversations(prev => prev.map(c =>
      c.id === convo.id ? { ...c, messages: loaded } : c
    ))
  }

  const sendMessage = async (text) => {
    if (!text.trim()) return
    if (!started) setStarted(true)
  
    const userMsg = { role: "user", text }
    const updated = [...messages, userMsg]
    setMessages(updated)
  
    const query = text.replaceAll(" ", "%20")
    setIsThinking(true)
    try {
      const response = await fetch(`http://127.0.0.1:8000/medLLM_message?query=${query}`)
      const data = await response.json()
      console.log(JSON.stringify(data.answer))
  
      const botMsg = { role: "bot", text: data.answer, topic: data.topic, sources: data.sources }
      setMessages(prev => [...prev, botMsg])
  
      // Determine the conversation ID to save under BEFORE any state updates
      const isNew = !activeId
      const tempTitle = text.slice(0, 36) + (text.length > 36 ? "…" : "")
  
      const user_save = await fetch("http://127.0.0.1:8000/save_message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: activeId,  // null for new → backend creates it
          role: "user",
          content: text,
          auth0_id: user.sub,
          title: tempTitle
        })
      })
      const supabase_user_save = await user_save.json()
      const realConvoId = supabase_user_save.conversation_id  // ✅ use the real DB ID
  
      const bot_save = await fetch("http://127.0.0.1:8000/save_message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: realConvoId,  // ✅ not activeId
          role: "bot",
          content: data.answer,
          auth0_id: user.sub,
        })
      })
      await bot_save.json()
  
      if (isNew) {
        const newConvo = {
          id: realConvoId,  // ✅ real DB ID, not Date.now()
          title: tempTitle,
          messages: [...updated, botMsg]
        }
        setConversations(prev => [newConvo, ...prev])
        setActiveId(realConvoId)
      } else {
        setConversations(prev => prev.map(c =>
          c.id === activeId ? { ...c, messages: [...updated, botMsg] } : c
        ))
      }
      setIsThinking(false)
    } catch (err) {
      setIsThinking(false)
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

  return (
    <div className={`app-layout ${sidebarOpen ? "sidebar-open" : "sidebar-closed"}`}>
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen(o => !o)}
        conversations={conversations}
        activeId={activeId}
        onSelect={loadConvo}
        onNewChat={newChat}
      />

      <main className={`main ${started ? "started" : ""}`}>
        {started ? (
          <ChatArea messages={messages} isThinking={isThinking}/>
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