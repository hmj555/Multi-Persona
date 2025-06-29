import React, { useState } from "react";
import { useNavigate, useLocation} from "react-router-dom";
import "./PerEval.css"; // ✅ 스타일 파일 정상 로드 확인!
import axios from "axios";

const PerEval = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const participantId = queryParams.get("participantId") || "Unknown";
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "https://multi-personas-backend.onrender.com"; 

  const surveyQuestions = [
    "This persona is interesting.",
    "This persona feels like it has a personality.",
    "I feel a strong connection with this persona.",
    "I feel that this persona understands me well.",
    "I feel that this persona acknowledges the different aspects of myself.",
    "I feel that this persona well reflects my personality.",
    "I feel that this persona well reflects my experiences.",
    "Conversations with this persona help me understand myself more deeply.",
    "나는 이 페르소나와 대화하면서 나의 상황을 '한 걸음 물러나' 볼 수 있었다.",
    "나는 이 페르소나와 대화할 때, 다른 사람의 기대나 사회적 역할에서 벗어나 자유롭게 나를 표현할 수 있었다.",
    "나는 이 페르소나와 대화하면서 ‘보여주고 싶은 나’가 아니라 ‘진짜 나’로서 반응할 수 있었다.",
    "나는 이 페르소나와 대화를 통해 나의 감정과 행동을 다시 생각해보게 되었다.",
    "나는 이 페르소나와 대화를 통해 내 생각을 돌아보게 되었다.",
    "나는 이 페르소나와 대화를 통해 나 자신을 더 받아들이게 되었다.",
    "나는 이 페르소나와 대화를 통해 나 자신을 비판하기보다는 이해하려고 노력하게 되었다.",
    "나는 이 페르소나를 더 알고 싶다.",
    "나는 이 페르소나를 필요할 때 다시 찾을 거 같다.",
    "나는 이 페르소나와 앞으로도 대화를 나누고 싶다.",
  ];

  const [surveyResponses, setSurveyResponses] = useState({});

  const handleSurveyChange = (question, value) => {
    setSurveyResponses((prev) => ({
      ...prev,
      [question]: value,
    }));
  };

  const handleSubmit = async () => {
    const unansweredQuestions = surveyQuestions.filter((question, index) => 
      !surveyResponses[`Q${index + 1}`]
    );
  
    if (unansweredQuestions.length > 0) {
      alert("모든 문항에 응답하지 않았습니다.");
      return; // ✅ 페이지 이동 방지
    }
  
    const timestamp = new Date().toISOString(); // 현재 시간 기록
  
    try {
      // ✅ 설문 응답 로깅 (FastAPI `/log_survey` 호출)
      await axios.post(`${BACKEND_URL}/log_survey`, {
        participantId: participantId,
        page: "PerEval(tag)",
        timestamp: timestamp,
        responses: surveyResponses,
      });
  
      console.log(`[LOG] 설문 응답 저장됨 - 시간: ${timestamp}, 응답:`, surveyResponses);
  
      // ✅ 버튼 클릭 이벤트 로깅 (FastAPI `/log_event` 호출)
      await axios.post(`${BACKEND_URL}/log_event`, {
        participantId: participantId,
        page: "PerEval(tag) submitted",
        button: "제출하기",
        timestamp: timestamp,
      });
  
      console.log(`[LOG] 제출하기 버튼 클릭 - 시간: ${timestamp}`);
  
      alert("설문이 제출되었습니다!");
  
      // ✅ 메인 페이지로 이동
      navigate(`/introper2?participantId=${participantId}`);
    } catch (error) {
      console.error("🚨 [ERROR] 설문 응답 또는 로그 저장 실패:", error);
    }
  };
  



  return (

<div className="page-container">
      <div className="fixed-shape">
        <span>>> Topic Selection >> Chat with Persona 1 and Experience Evaluation >> </span> 
        <p>&nbsp; Persona 1 Evaluation</p> 
      </div>

    <div className="pereval-container">
    <div className="chat-topic">
          <div className="per-content">☝️ Persona1 Evaluation</div>          
        </div>
        <hr className="per-divider" />
      <div className="pereval-body">
        {surveyQuestions.map((question, index) => (
    
          <div key={index} className="pereval-survey-question">
            <section className="experiment-procedure">
            <p style={{ fontSize: "14.5px" }}>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            
            <strong>{index + 1}. {question}</strong></p>
            </section>
            <div className="pereval-scale-container">
              <span className="pereval-scale-label" style={{ color: "#000000" }}>Strongly <br></br>Disagree</span>
              {[1, 2, 3, 4, 5, 6, 7].map((num) => (
                <label key={num} className="pereval-scale-option" style={{ color: "#000000" }}>
                  <input
                    type="radio"
                    name={`Q${index + 1}`}
                    value={num}
                    checked={surveyResponses[`Q${index + 1}`] === num}
                    onChange={() => handleSurveyChange(`Q${index + 1}`, num)}
                  />
                  {num}
                </label>
              ))}
              <span className="pereval-scale-label" style={{ color: "#000000" }}>Strongly <br></br> Agree</span>
            </div>
          </div>
        ))}
      </div>

      <button className="pereval-button submit-button" onClick={handleSubmit}>
        Submit
      </button>
    </div>
    </div>
  );
};

export default PerEval;
