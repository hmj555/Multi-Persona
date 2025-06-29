import React from "react";
import "./Tooltip.css"; // ✅ 추가된 CSS 가져오기

const Tooltip = () => {
  return (
    <div className="tooltip-container">
      <p>Hover me.</p>
      <div className="tooltip-content">
        <p><strong>Hello there! 👋</strong></p>
        <p>This is a tooltip message!<br />It <b>appears</b> and then <b>disappears</b>.</p>
      </div>
    </div>
  );
};

export default Tooltip;

{/* <Tooltip /> 으로 추가 가능 */}