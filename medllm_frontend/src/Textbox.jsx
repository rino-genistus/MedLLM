import {useState} from 'react'

function Textbox({onSend}){
    const [value, setValue] = useState("")

    const handleSend = () => {
        onSend(value)
        setValue("")
    }

    const handleKeyDown = (e) => {
        if (e.key === "Enter") handleSend()
    }

    return (
        <div className="input-row">
          <input 
            placeholder="Ask a study question..."
            value={value}
            onChange={e => setValue(e.target.value)}
            onKeyDown={handleKeyDown} 
          />
          <button onClick={handleSend}>Ask →</button>
        </div>
      )
}
export default Textbox