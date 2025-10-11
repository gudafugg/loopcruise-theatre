import { useNavigate } from 'react-router-dom'
import './App.css'

function App() {
  const navigate = useNavigate()

  const handleStart = () => {
    navigate('/game')
  }

  const handleSettings = () => {
    alert('⚙️ 设置功能暂未实现')
  }

  const handleExit = () => {
    window.close() // 可能会被浏览器拦截
  }

  return (
    <div className="home">
      {/* 背景图占位 */}
      <div className="background"></div>

      {/* 标题 */}
      <h1 className="title">LoopCruise</h1>

      {/* 按钮组 */}
      <div className="menu">
        <button onClick={handleStart}>开始游戏</button>
        <button onClick={handleSettings}>设置</button>
        <button onClick={handleExit}>退出游戏</button>
      </div>

      {/* 背景音乐预留 */}
      {/* <audio autoPlay loop src="/assets/bgm.mp3" /> */}
    </div>
  )
}

export default App