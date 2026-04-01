import { useState, useEffect, useRef } from "react"
import { InlineMath, BlockMath } from 'react-katex'

function MessageRenderer({ text, isLatest, msgId }) {
  const [displayed, setDisplayed] = useState(text)
  const [done, setDone] = useState(!isLatest)
  const hasRun = useRef(false)

  useEffect(() => {
    if (!isLatest) {
      setDisplayed(text)
      setDone(true)
      return
    }
    if (hasRun.current) return
    hasRun.current = true
  
    const words = text.split(" ")
    let i = 0
    setDisplayed("")
    setDone(false)
  
    const next = () => {
      i++
      setDisplayed(words.slice(0, i).join(" "))
      if (i >= words.length) {
        setDone(true)
        return
      }
      const delay = Math.max(35, 80 - i * 1.2)
      setTimeout(next, delay)
    }
  
    setTimeout(next, 60)
  }, [msgId])

  const activeText = displayed || ""
  if (!activeText && !done) return <span className="typewriter-cursor" />
  if (typeof activeText !== "string") return null

  let cleaned = activeText.replace(/\\n/g, "\n").trim()
  console.log("CLEANED:", JSON.stringify(cleaned))
  const parts = cleaned.split(/(\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\))/g)
  console.log("PARTS JSON:", JSON.stringify(parts))

  return (
    <span>
      {parts.map((part, i) => {
        console.log(`PART ${i}:`, JSON.stringify(part), "isInline:", /^\\\([\s\S]*\\\)$/.test(part.trim()))
        if (/^\\\[[\s\S]*\\\]$/.test(part.trim())) {
          const math = part.replace(/^\s*\\\[\s*/, "").replace(/\s*\\\]\s*$/, "")
          return <div key={i} style={{ margin: "12px 0" }}><BlockMath math={math} /></div>
        }
        if (/^\\\([\s\S]*\\\)$/.test(part.trim())) {
          const math = part.replace(/^\s*\\\(\s*/, "").replace(/\s*\\\)\s*$/, "")
          return <InlineMath key={i} math={math} />
        }
        console.log(`RENDERING PART ${i} AS:`, /^\\\([\s\S]*\\\)$/.test(part?.trim()) ? "LATEX" : "PLAIN")
        return (
          <span key={i}>
            {part.split("\n").map((line, j, arr) => (
              <span key={j}>{line}{j < arr.length - 1 && <br />}</span>
            ))}
          </span>
        )
      })}
      {!done && <span className="typewriter-cursor" />}
    </span>
  )
}

export default MessageRenderer