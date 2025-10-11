import { useEffect, useRef, useState } from 'react'
import './dialogue.css'

interface DialogueBoxProps {
  speaker?: string
  text: string
  speed?: number // 打字速度，可选
  onTypingEnd?: () => void // 一句打完时通知上层
  onAdvance?: () => void // 用户点击或空格时推进
  enableHotkeys?: boolean // 是否启用空格/回车监听
  lineKey?: string // 当前行的唯一标识（用于重置）
}

export default function DialogueBox({
  speaker,
  text,
  speed = 80,
  onTypingEnd,
  onAdvance,
  enableHotkeys = true,
  lineKey,
}: DialogueBoxProps) {
  const [displayText, setDisplayText] = useState('')
  const [isTyping, setIsTyping] = useState(true)
  const timerRef = useRef<number | null>(null)
  const onTypingEndRef = useRef(onTypingEnd)

  useEffect(() => {
    onTypingEndRef.current = onTypingEnd
  }, [onTypingEnd])

  // 每次 text 或 lineKey 变化时重新开始打字
  useEffect(() => {
    setDisplayText('')
    setIsTyping(true)
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }

    timerRef.current = window.setInterval(() => {
      setDisplayText(prev => {
        const nextLen = prev.length + 1
        if (nextLen >= text.length) {
          if (timerRef.current) {
            clearInterval(timerRef.current)
            timerRef.current = null
          }
          setIsTyping(false)
          onTypingEndRef.current?.()
          return text
        }
        return text.slice(0, nextLen)
      })
    }, speed)

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [text, speed, lineKey])

  // 点击逻辑：打字中 → 快进；已打完 → 请求下一句
  const handleClick = () => {
    if (isTyping) {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
      setDisplayText(text)
      setIsTyping(false)
      onTypingEndRef.current?.()
    } else {
      onAdvance?.()
    }
  }

  // 监听空格/回车，与点击行为一致
  useEffect(() => {
    if (!enableHotkeys) return
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === ' ' || e.key === 'Enter') {
        e.preventDefault()
        handleClick()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [enableHotkeys, isTyping, text])

  return (
    <div className="dlg-wrap" onClick={handleClick}>
      <div className="dlg-box">
        <div className="dlg-speaker">{speaker}</div>
        <div className="dlg-text">{displayText}</div>
      </div>
    </div>
  )
}