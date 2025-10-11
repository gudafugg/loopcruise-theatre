

import type { CharacterPose } from './types'

/**
 * CharacterLayer
 * 渲染当前场景中的角色立绘。
 * - 根据 slot: 'left' | 'center' | 'right' 布局
 * - 支持透明度与简单淡入效果（effect: 'fade'）
 * - 样式定位依赖 src/styles/dialogue.css 中的 .char-layer / .char.*
 */
export default function CharacterLayer({ list }: { list?: CharacterPose[] }) {
  if (!list || list.length === 0) return null

  return (
    <div className="char-layer">
      {list.map((c) => (
        <img
          key={`${c.id}`}
          src={c.sprite}
          alt={c.id}
          style={{
            opacity: c.opacity ?? 1,
            transition: c.effect === 'fade' ? 'opacity 0.5s ease' : undefined,
          }}
        />
      ))}
    </div>
  )
}