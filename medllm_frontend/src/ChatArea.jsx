import { useEffect, useRef } from "react"

function ChatArea({ messages }) {
  const bottomRef = useRef(null)
  console.log(messages)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <div className="chat-area">
      {messages.map((msg, i) => (
        <div key={i} className={`bubble ${msg.role}`}>
          {msg.text}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
export default ChatArea