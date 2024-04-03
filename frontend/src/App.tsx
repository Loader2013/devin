import React, { useContext, useState } from "react";
import "./App.css";
import ChatInterface from "./components/ChatInterface";
import Errors from "./components/Errors";
import SettingModal from "./components/SettingModal";
import Workspace from "./components/Workspace";
import { ThemeContext } from "./Theme";
function App(): JSX.Element {
  const [settingOpen, setSettingOpen] = useState(false);
  const { theme,toggleTheme } = useContext(ThemeContext);
  const handleCloseModal = () => {
    setSettingOpen(false);
  };

  return (
    <div className={`App ${theme}`}>
    <div className="flex h-screen bg-bg-dark text-white">
      <Errors />
      <div className="flex-1 rounded-xl m-4 overflow-hidden bg-bg-light">
        <ChatInterface setSettingOpen={setSettingOpen} />
      </div>
      <div className="flex flex-col flex-1 m-4 overflow-hidden rounded-xl bg-bg-light">
        <Workspace />
      </div>
<button  className="test"onClick={() => toggleTheme()}>{theme}</button>
      <SettingModal isOpen={settingOpen} onClose={handleCloseModal} />
    </div>
    </div>
  );
}

export default App;
