import { useEffect, useRef } from "react"
import MessageRenderer from "./MessageRenderer"
import TypingIndicator from "./TypingIndicator"

function ChatArea({ messages, isThinking }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <div className="chat-area">
      {messages.map((msg, i) => (
        <div key={i} className={`bubble ${msg.role}`}>
          <MessageRenderer
            text={msg.text}
            isLatest={i === messages.length - 1 && msg.role === "bot"}
            msgId={i}
          />
        </div>
      ))}
      {isThinking && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  )
}

export default ChatArea