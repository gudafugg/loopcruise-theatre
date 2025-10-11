import { useCallback, useMemo, useState } from 'react'
import type { Script, Line } from './types'

export type DialogueStatus = 'idle' | 'typing' | 'waiting'

/**
 * useDialogueQueue
 * 控制当前剧本行、状态流转、以及快进/推进逻辑。
 */
export function useDialogueQueue() {
  // 当前载入的剧本
  const [script, setScript] = useState<Script | null>(null)
  // 当前行 id
  const [currentId, setCurrentId] = useState<string | null>(null)
  // 当前对话状态
  const [status, setStatus] = useState<DialogueStatus>('idle')

  // 当前行数据
  const current: Line | undefined = useMemo(() => {
    if (!script || !currentId) return undefined
    return script[currentId]
  }, [script, currentId])

  /**
   * 初始化剧本并从起点开始
   */
  const setQueue = useCallback((newScript: Script, startId: string) => {
    setScript(newScript)
    setCurrentId(startId)
    setStatus('typing') // 新句进入打字态
  }, [])

  /**
   * 打字完成时由 DialogueBox 调用
   * -> typing → waiting
   */
  const onTypingEnd = useCallback(() => {
    if (status !== 'typing') return
    setStatus('waiting')
  }, [status])

  /**
   * 打字中点击/空格：快进到整句，但不跳下一句
   * -> typing → waiting
   */
  const fastForward = useCallback(() => {
    if (status === 'typing') {
      setStatus('waiting')
    }
  }, [status])

  /**
   * 整句显示后点击/空格：进入下一句
   * -> waiting → typing / idle
   */
  const next = useCallback(() => {
    if (status !== 'waiting' || !current) return

    const nextId = current.next
    if (nextId && script && script[nextId]) {
      setCurrentId(nextId)
      setStatus('typing')
    } else {
      // 没有 next 即剧本结束
      setStatus('idle')
    }
  }, [status, current, script])

  /**
   * 重置为初始状态
   */
  const reset = useCallback(() => {
    setScript(null)
    setCurrentId(null)
    setStatus('idle')
  }, [])

  return {
    current,    // 当前行
    status,     // 当前状态（typing / waiting / idle）
    setQueue,   // 初始化剧本
    onTypingEnd,
    fastForward,
    next,
    reset,
  }
}