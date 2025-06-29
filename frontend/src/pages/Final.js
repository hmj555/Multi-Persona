import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import "./Topic.css"; 

const Topics = () => {

  const navigate = useNavigate();
  const location = useLocation();

  // URL에서 participantId 가져오기
  const queryParams = new URLSearchParams(location.search);
  const participantId = queryParams.get("participantId") || "Unknown";

  useEffect(() => {
    console.log(`[INFO] 참가자 번호 확인: ${participantId}`);
  }, [participantId]);



  return (
    <div className="page-container">
      <div className="fixed-shape">
        <span>자기 페르소나와 대화 경험 평가 >> 주제 선택 >> 채팅 및 경험 평가1 >> 페르소나 평가1 >> 채팅 및 경험 평가2 >> 페르소나 평가2 >> </span> 
        <p>&nbsp; 사후 인터뷰</p> 
      </div>


    <div className="topic-container">

      <section className="experiment-procedure">
      <p>&nbsp;</p>
      <p>&nbsp;</p>
      <p>&nbsp;</p>
      <p>&nbsp;</p>
      <p>&nbsp;</p>
      <p>&nbsp;</p>
      <p>&nbsp;</p>
      <img src="girl.png" alt="실험 절차" className="process-image" style={{ width: "130px", height: "auto" }} />
      <p style={{fontSize: "30px" , textAlign: "center"}}>수고하셨습니다.</p>
      <p style={{fontSize: "30px", textAlign: "center"}}>마지막으로 사후 인터뷰 진행하겠습니다.</p>
      </section>
      
    </div>
    </div>
  );
};

export default Topics;
