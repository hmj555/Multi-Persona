import './App.css';
import "./index.css";

import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Intro from "./pages/Intro";
import Info from "./pages/Info";
import Topic from "./pages/Topic";
import IntroPer1 from "./pages/IntroPer1";
import Chat1 from "./pages/Chat1";
import IntroPer2 from "./pages/IntroPer2";
import Chat2 from "./pages/Chat2";
import PerEval from "./pages/PerEval";
import PerEval2 from "./pages/PerEval2";
import EpiEval from "./pages/EpiEval";
import Final from "./pages/Final";


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Intro />} />
        <Route path="/info" element={<Info />} />  {/* "/persona" → "/Info" 변경 */}
        <Route path="/topic" element={<Topic />} />
        {/* ✅ chatId를 동적으로 받도록 설정 */}
        <Route path="/introper1" element={<IntroPer1 />} />
        <Route path="/chat1/:chatId" element={<Chat1 />} />
        <Route path="/pereval/tag" element={<PerEval />} />
        <Route path="/introper2" element={<IntroPer2 />} />
        <Route path="/chat2/:chatId" element={<Chat2 />} />
        <Route path="/pereval/epi" element={<PerEval2 />} />
        <Route path="/epieval" element={<EpiEval />} />
        <Route path="/final" element={<Final />} />
        
        
      </Routes>
    </Router>
  );
}

export default App;