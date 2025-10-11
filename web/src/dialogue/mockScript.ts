// src/dialogue/mockScript.ts
import type { Script } from './types';

const script: Script = {
  start: {
    id: 'start',
    speaker: '丁奇',
    text: '你终于来了。我们已经等你很久了。',
    bg: '/assets/bg.jpg',
    characters: [
      { id: 'dingqi', sprite: '/assets/chars/dingqi.png' }
    ],
    next: 'p1',
  },
  p1: {
    id: 'p1',
    speaker: '你',
    text: '这是哪里？刚刚发生了什么？',
    characters: [
      { id: 'player', sprite: '/assets/chars/player.png' }
    ],
    next: 'p2',
  },
  p2: {
    id: 'p2',
    speaker: 'DM',
    text: '（海风拂面，汽笛声在远处回荡……）',
    characters: [
      { id: 'dingqi', sprite: '/assets/chars/dingqi.png', opacity: 0.9 },
    ],
    // 没有 next 代表脚本结束
  },
};

export default script;