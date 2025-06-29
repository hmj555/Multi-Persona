import React, { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./Topic.css"; 
import axios from "axios";

const IntroPer1 = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "https://multi-personas-backend.onrender.com";

  // URL에서 participantId 가져오기
  const queryParams = new URLSearchParams(location.search);
  const participantId = queryParams.get("participantId") || "Unknown";

  useEffect(() => {
    console.log(`[INFO] 참가자 번호 확인: ${participantId}`);
  }, [participantId]);

  // ✅ 시작하기 버튼 클릭 시 Chat1으로 이동
  // const handleStart = () => {
  //   navigate(`/chat1/1?participantId=${participantId}`);
  // };

  const handleStart = async () => {
    const timestamp = new Date().toISOString(); // ✅ 현재 시간 기록
  
    // ✅ "시작하기" 버튼 클릭 로그 서버로 전송
    try {
      await axios.post(`${BACKEND_URL}/log_event`, {
        participantId: participantId,
        page: "IntroPer1",
        button: "시작하기",
        timestamp: timestamp
      });
      console.log(`[LOG] "시작하기" 버튼 클릭됨 - 시간: ${timestamp}`);
    } catch (error) {
      console.error("🚨 [ERROR] 버튼 클릭 로그 저장 실패:", error);
    }
  
    // 🚀 Chat1 페이지로 이동
    navigate(`/chat1/1?participantId=${participantId}`);
  };

  return (
    <div className="page-container">
      <div className="fixed-shape">
        <span>자기 페르소나와 대화 경험 평가 >> 주제 선택 >> </span> 
        <p>&nbsp; 채팅 및 경험 평가1</p> 
      </div>

      <div className="topic-container">
        <section className="experiment-procedure">
          <p>&nbsp;</p>
          <p>&nbsp;</p>
          <p>&nbsp;</p>
          <p style={{ fontSize: "25px", textAlign: "center" }}>☝️ 첫번째 페르소나와 채팅</p>
          <p>&nbsp;</p>
          
          <img
          src="chat.png"
          alt="실험 절차"
          className="process-image"
          style={{
            width: "1050px",
            height: "280px",
            maxWidth: "none",
            display: "block",
            marginLeft: "-60px",
          }}
        />

          <p>&nbsp;</p>
          <p style={{ fontSize: "13px", textAlign: "center" }}>
            이 단계에서는 <strong>첫번째 페르소나</strong>와 <strong>10개</strong>의 주제로 대화를 하게 됩니다.
          </p>
          <p style={{ fontSize: "13px", textAlign: "center" }}>
            각 대화가 끝난 후에 <strong>대화 경험을 평가</strong>하고, 10번의 대화가 끝난 후엔 첫번째 <strong>페르소나를 평가</strong>하게 됩니다.
          </p>
          <p style={{ fontSize: "13px", textAlign: "center" }}>
            채팅 메시지는 키보드에서 'Enter'를 누르거나, 화면에서 'Enter' 버튼을 마우스로 클릭하시면 전송됩니다.
          </p>
          <p style={{ fontSize: "13px", textAlign: "center" }}>
            준비가 되셨으면 '시작하기' 버튼을 클릭해주세요.
          </p>
          <p>&nbsp;</p>
          {/* <p>&nbsp;</p> */}
        </section>

        {/* ✅ 버튼을 div 내부로 이동 */}
        <button onClick={handleStart} className="submitButton">
          시작하기
        </button>
      </div>
    </div>
  );
};

export default IntroPer1;
