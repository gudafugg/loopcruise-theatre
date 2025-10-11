import { useEffect, useCallback } from 'react'
import DialogueBox from './dialogue/DialogueBox'          // 可控对话框
import { useDialogueQueue } from './dialogue/useDialogueQueue' // 新的状态机 Hook
import script from './dialogue/mockScript'                  // ← 载入剧本：src/dialogue/mockScript.ts

export default function Game() {
  const {
    current,      // 当前行（含 speaker / text / next）
    status,       // 'typing' | 'waiting' | 'idle'
    setQueue,     // 载入剧本并从某行开始
    onTypingEnd,  // 本句逐字完成时的回调
    fastForward,  // 打字中：快进到整句
    next,         // 已整句：进入下一句
  } = useDialogueQueue()

  // 挂载后载入剧本，从 'start' 开始
  useEffect(() => {
    setQueue(script, 'start')
  }, [setQueue])

  // 推进逻辑：打字中→快进；已整句→下一句
  const handleAdvance = useCallback(() => {
    if (status === 'typing') fastForward()
    else if (status === 'waiting') next()
  }, [status, fastForward, next])

  // （键盘空格/回车与点击一致
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === ' ' || e.key === 'Enter') {
        e.preventDefault()
        handleAdvance()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [handleAdvance])

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'linear-gradient(180deg, #101114 0%, #0b0c0f 100%)',
        color: '#ffffff',
        fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif',
      }}
    >
      {/* 对话框：仅当有 current 时渲染。lineKey 用 id 触发重置与重新逐字 */}
      {current && (
        <DialogueBox
          speaker={current.speaker}
          text={current.text}
          lineKey={current.id}
          onTypingEnd={onTypingEnd}
          onAdvance={handleAdvance}
        />
      )}

      <div
        style={{
          position: 'absolute',
          top: 8,
          left: 8,
          fontSize: 12,
          padding: '4px 8px',
          background: 'rgba(0,0,0,0.45)',
          borderRadius: 6,
          pointerEvents: 'none',
        }}
      >
       Minimal HUD · {new Date().toLocaleTimeString()}
      </div>
    </div>
  )
}