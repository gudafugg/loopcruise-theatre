
export type CharacterSlot = 'left' | 'center' | 'right';

export type CharacterPose = {
  id: string;            // 角色ID（如 'dingqi'）
  sprite: string;        // 立绘图片URL
  opacity?: number;      // 0~1（可做淡入）
  effect?: 'fade' | 'none';
};

export type Line = {
  id: string;                  // 当前句ID
  speaker?: string;            // 角色名（名牌显示）
  text: string;                // 对话文本
  characters?: CharacterPose[];// 本句需要呈现的立绘
  bg?: string;                 // 背景图（可选）
  bgm?: string;                // 背景音乐（可选）
  sfx?: string;                // 音效（可选）
  next?: string;               // 下一句ID（无分支时）
  choices?: {                  // 分支（后续再用）
    id: string;
    text: string;
    next: string;
  }[];
};

export type Script = Record<string, Line>;